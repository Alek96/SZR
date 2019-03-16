from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import F, Value, When, Case
from django.utils import timezone
from django.contrib.auth.models import User as Auth_user
from social_django.models import UserSocialAuth
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from model_utils import FieldTracker


class AbstractGitlabModel(models.Model):
    gitlab_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    gitlab_web_url = models.URLField(null=True, blank=True)

    class Meta:
        abstract = True


class GitlabUser(AbstractGitlabModel):
    auth_user = models.OneToOneField(Auth_user, on_delete=models.SET_NULL, null=True, blank=True)
    social_auth = models.OneToOneField(UserSocialAuth, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='SZR_user')

    def has_access_token(self):
        if self.social_auth:
            return 'access_token' in self.social_auth.extra_data
        return False

    def get_access_token(self):
        if self.has_access_token():
            return self.social_auth.extra_data['access_token']
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
    CREATED = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    STATUS_CHOICES = (
        (CREATED, 'Created'),
        (RUNNING, 'Running'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    )

    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=CREATED)

    class Meta:
        abstract = True


class AbstractTaskGroup(AbstractTaskDates, AbstractTaskStatus):
    tasks_number = models.PositiveIntegerField(default=0)
    finished_tasks_number = models.PositiveIntegerField(default=0)
    failed_task_number = models.PositiveIntegerField(default=0)

    tasks_set = None
    tracker = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._set_status()
        super().save(update_fields=['status'])
        if self.tracker.has_changed('execute_date'):
            self._update_tasks_execute_dates()

    def _update_tasks_execute_dates(self):
        for task in self.tasks_set.all():
            if task.status == task.CREATED:
                task.execute_date = self.execute_date
                task.save()

    def increment_task_number(self):
        self.tasks_number = F('tasks_number') + 1
        self.finished_date = None

    def _set_status(self):
        self.status = Case(
            When(finished_tasks_number=0, then=Value(self.CREATED)),
            When(finished_tasks_number__lt=F('tasks_number'), then=Value(self.RUNNING)),
            When(failed_task_number__gt=0, then=Value(self.FAILED)),
            default=Value(self.COMPLETED),
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
    owner = models.ForeignKey(GitlabUser, on_delete=models.CASCADE, related_name='owned_tasks_%(class)s')
    celery_task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True)

    task_group = None  # models.ForeignKey(TaskGroup, on_delete=models.CASCADE, related_name='tasks_set_%(class)s')
    tracker = None

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if self.tracker.has_changed('execute_date'):
            if self.status != self.CREATED:
                raise ValidationError(
                    {'execute_date': _('Execute_date cannot be change after start of the celery task')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        if not self.celery_task and self.status == self.CREATED:
            self.celery_task = self._create_task()
            super().save(update_fields=['celery_task'])

        if self.celery_task and self.tracker.has_changed('execute_date'):
            self.celery_task.start_time = self.execute_date
            self.celery_task.save()

    def _create_task(self):
        return PeriodicTask.objects.create(
            interval=self._create_or_get_interval(),
            name='task-{}-{}'.format(self.__class__.__name__, self.id),
            task=self._get_task_path(),
            kwargs={'id': self.id},
            one_off=True,
            start_time=self.execute_date
        )

    def _create_or_get_interval(self):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=10,
            period=IntervalSchedule.SECONDS
        )

        return schedule

    def _get_task_path(self):
        raise NotImplementedError('AbstractTask must define the _get_task_path method.')
