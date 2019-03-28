from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import F, Value, When, Case
from django.utils import timezone
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from model_utils import FieldTracker
import json


class AbstractGitlabModel(models.Model):
    gitlab_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    gitlab_web_url = models.URLField(null=True, blank=True)

    class Meta:
        abstract = True


class GitlabUser(AbstractGitlabModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_social_auth = models.OneToOneField(UserSocialAuth, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='SZR_user')

    def has_access_token(self):
        if self.user_social_auth:
            return 'access_token' in self.user_social_auth.extra_data
        return False

    def get_access_token(self):
        if self.has_access_token():
            return self.user_social_auth.extra_data['access_token']
        raise RuntimeError("User {} does not have access token".format(self))

    def __str__(self):
        return "<User: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()


class AbstractTaskDates(models.Model):
    create_date = models.DateTimeField(default=timezone.now, blank=True)
    execute_date = models.DateTimeField(default=timezone.now, blank=True)
    finished_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class AbstractTaskStatus(models.Model):
    READY = 0
    RUNNING = 1
    SUCCEED = 2
    FAILED = 3
    WAITING = 4
    STATUS_CHOICES = (
        (WAITING, _('Waiting')),
        (READY, _('Ready')),
        (RUNNING, _('Running')),
        (SUCCEED, _('Succeed')),
        (FAILED, _('Failed')),
    )

    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=READY)

    class Meta:
        abstract = True

    def is_started(self):
        return not (self.status == self.READY or self.status == self.WAITING)

    def is_finished(self):
        return self.status == self.SUCCEED or self.status == self.FAILED


def create_field_tracker(cls, name):
    """
    Add field tracker to given model class and set it to given name attribute.

    Signal class_prepared cannot be created in class_prepared, so we run finalize_class manually.

    :param cls: model class
    :param name: field name
    :return: None
    """
    tracker = FieldTracker()
    tracker.contribute_to_class(cls, name)
    tracker.finalize_class(cls)


class AbstractTaskGroup(AbstractTaskDates, AbstractTaskStatus):
    # _parent_task = GitlabUser

    name = models.CharField(max_length=2000)

    tasks_number = models.PositiveIntegerField(default=0)
    finished_tasks_number = models.PositiveIntegerField(default=0)
    failed_task_number = models.PositiveIntegerField(default=0)

    tasks_set = None
    tracker = None

    class Meta:
        abstract = True

    @classmethod
    def on_class_prepared(cls):
        # models.ForeignKey(
        #     cls._parent_task,
        #     on_delete=models.SET_NULL,
        #     related_name='child_tasks_%(class)s',
        #     null=True, blank=True
        # ).contribute_to_class(cls, 'parent_task')
        create_field_tracker(cls, 'tracker')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._set_status()
        super().save(update_fields=['status'])
        if self.tracker.has_changed('execute_date'):
            self._update_tasks_execute_dates()
        self.refresh_from_db()

    def _update_tasks_execute_dates(self):
        for task in self.tasks_set.all():
            if task.status == self.READY:
                task.execute_date = self.execute_date
                task.save()

    def increment_task_number(self):
        self.tasks_number = F('tasks_number') + 1
        self.finished_date = None

    def _set_status(self):
        self.status = Case(
            When(finished_tasks_number=0, then=Value(self.READY)),
            When(finished_tasks_number__lt=F('tasks_number'), then=Value(self.RUNNING)),
            When(failed_task_number__gt=0, then=Value(self.FAILED)),
            default=Value(self.SUCCEED),
            output_field=models.PositiveIntegerField()
        )

    def increment_finished_tasks_number(self, task_status):
        self.finished_tasks_number += F('finished_tasks_number') + 1
        if task_status == self.FAILED:
            self.failed_task_number += F('failed_task_number') + 1

        self.finished_date = Case(
            When(tasks_number=F('finished_tasks_number') + 1, then=Value(timezone.now())),
            default=None,
            output_field=models.DateTimeField()
        )


class AbstractTask(AbstractTaskDates, AbstractTaskStatus):
    _task_group_model = None

    owner = models.ForeignKey(GitlabUser, on_delete=models.CASCADE, related_name='owned_tasks_%(class)s')
    celery_task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)
    error_msg = models.CharField(max_length=2000, null=True, blank=True)

    task_group = None  # models.ForeignKey(TaskGroup, on_delete=models.CASCADE, related_name='tasks_set_%(class)s')
    tracker = None

    class Meta:
        abstract = True

    @classmethod
    def on_class_prepared(cls):
        task_group = models.ForeignKey(cls._task_group_model, on_delete=models.CASCADE, related_name='tasks_set')
        task_group.contribute_to_class(cls, 'task_group')
        create_field_tracker(cls, 'tracker')

    def clean(self):
        super().clean()

        if self.tracker.has_changed('execute_date'):
            if self.is_started():
                raise ValidationError(
                    {'execute_date': _('Execute_date cannot be change after start of the celery task')})

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.pk is None:
            self.task_group.increment_task_number()
            self.task_group.save()
            self.execute_date = self.task_group.execute_date

        if self.tracker.has_changed('execute_date'):
            if self.celery_task:
                self.celery_task.start_time = self.execute_date
                self.celery_task.save()

        if self.tracker.has_changed('status'):
            if self.is_started():
                if self.celery_task:
                    self.celery_task.delete()
                    self.celery_task = None
            if self.is_finished():
                self.task_group.increment_finished_tasks_number(self.status)
                self.task_group.save()

        super().save(*args, **kwargs)

        if self.status == self.READY:
            if not self.celery_task:
                self.celery_task = self._create_task()
                super().save(update_fields=['celery_task'])

    def _create_task(self):
        return PeriodicTask.objects.create(
            interval=self._get_or_create_interval(),
            name='task-{}-{}'.format(self.__class__.__name__, self.id),
            task=self._get_task_path(),
            kwargs=json.dumps({'task_id': self.id}),
            one_off=True,
            start_time=self.execute_date
        )

    def _get_or_create_interval(self):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS
        )

        return schedule

    def _get_task_path(self):
        raise NotImplementedError('AbstractTask must define the _get_task_path method.')
