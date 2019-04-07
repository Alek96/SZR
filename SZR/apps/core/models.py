import json

from GitLabApi.objects import VisibilityLevel, AccessLevel
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Value, When, Case
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from model_utils import FieldTracker
from social_django.models import UserSocialAuth


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


class ModelUrlsMethods:

    @property
    def edit_url(self):
        return '#'

    @property
    def delete_url(self):
        return '#'

    @property
    def tasks_page_url(self):
        return '#'


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


class AbstractTaskGroup(AbstractTaskDates, AbstractTaskStatus, ModelUrlsMethods):
    _parent_task_model = None

    name = models.CharField(max_length=2000)

    tasks_number = models.PositiveIntegerField(default=0)
    finished_tasks_number = models.PositiveIntegerField(default=0)
    failed_task_number = models.PositiveIntegerField(default=0)

    parent_task = None
    tasks_set = None
    tracker = None

    class Meta:
        abstract = True

    @classmethod
    def on_class_prepared(cls):
        models.ForeignKey(
            cls._parent_task_model,
            on_delete=models.SET_NULL,
            related_name='child_task_group_%(class)s',
            null=True, blank=True
        ).contribute_to_class(cls, 'parent_task')
        create_field_tracker(cls, 'tracker')

    @property
    def new_task_url(self):
        return '#'

    def clean(self):
        super().clean()

        if self.pk is not None:
            if self.tracker.has_changed('status'):
                if self.status == self.WAITING:
                    raise ValidationError(
                        {'status': _('Status cannot be change to "Waiting" after creating')})

    def save(self, *args, **kwargs):
        self.clean()

        if self.parent_task and not self.parent_task.is_finished():
            self.status = self.WAITING

        if self.tracker.has_changed('status'):
            if self.status == self.READY:
                self._set_tasks_to_ready()

        if self.tracker.has_changed('execute_date'):
            self._update_tasks_execute_dates()

        self._save(*args, **kwargs)

        super().save(*args, **kwargs)
        self._set_status()
        super().save(update_fields=['status'])
        self.refresh_from_db()

    def _set_tasks_to_ready(self):
        for task in self.tasks_set.all():
            task.status = self.READY
            task.save()

    def _update_tasks_execute_dates(self):
        for task in self.tasks_set.all():
            if task.status == self.READY:
                task.execute_date = self.execute_date
                task.save()

    def _save(self, *args, **kwargs):
        """
        Here Children class can set special attributes to saving model

        :return: None
        """

    def _set_status(self):
        if self.status != self.WAITING:
            self.status = Case(
                When(finished_tasks_number=0, then=Value(self.READY)),
                When(finished_tasks_number__lt=F('tasks_number'), then=Value(self.RUNNING)),
                When(failed_task_number__gt=0, then=Value(self.FAILED)),
                default=Value(self.SUCCEED),
                output_field=models.PositiveIntegerField()
            )

    def increment_task_number(self):
        self.tasks_number = F('tasks_number') + 1
        self.finished_date = None

    def increment_finished_tasks_number(self, task_status):
        self.finished_tasks_number += F('finished_tasks_number') + 1
        if task_status == self.FAILED:
            self.failed_task_number += F('failed_task_number') + 1

        self.finished_date = Case(
            When(tasks_number=F('finished_tasks_number') + 1, then=Value(timezone.now())),
            default=None,
            output_field=models.DateTimeField()
        )


class AbstractTask(AbstractTaskDates, AbstractTaskStatus, ModelUrlsMethods):
    _task_group_model = None

    owner = models.ForeignKey(GitlabUser, on_delete=models.CASCADE, related_name='owned_tasks_%(class)s')
    celery_task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)
    error_msg = models.CharField(max_length=2000, null=True, blank=True)

    task_group = None
    tracker = None

    class Meta:
        abstract = True

    @classmethod
    def on_class_prepared(cls):
        task_group = models.ForeignKey(cls._task_group_model, on_delete=models.CASCADE, related_name='tasks_set')
        task_group.contribute_to_class(cls, 'task_group')
        create_field_tracker(cls, 'tracker')

    @property
    def task_name(self):
        return str(self)

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
            if self.task_group.status == self.WAITING:
                self.status = self.WAITING
            if self.is_started():
                if self.celery_task:
                    self.celery_task.delete()
                    self.celery_task = None
            if self.is_finished():
                self.task_group.increment_finished_tasks_number(self.status)
                self.task_group.save()
                self._update_children_tasks_status()

        self._save(*args, **kwargs)

        super().save(*args, **kwargs)

        if self.status == self.READY:
            if not self.celery_task:
                self.celery_task = self._create_task()
                super().save(update_fields=['celery_task'])

    def _update_children_tasks_status(self):
        for attr in self.__dir__():
            if attr.startswith('child_task_group_'):
                task_group_set = getattr(self, attr)
                for task_group in task_group_set.all():
                    task_group.status = self.READY
                    task_group.save()

    def _save(self, *args, **kwargs):
        """
        Here Children class can set special attributes to saving model

        :return: None
        """

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


class AbstractAccessLevel(models.Model, AccessLevel):
    access_level = models.IntegerField(choices=AccessLevel.ACCESS_LEVEL_CHOICES, default=AccessLevel.ACCESS_GUEST)

    class Meta:
        abstract = True


class AbstractVisibilityLevel(models.Model, VisibilityLevel):
    visibility = models.CharField(max_length=10, choices=VisibilityLevel.VISIBILITY_CHOICES,
                                  default=VisibilityLevel.PRIVATE)

    class Meta:
        abstract = True
