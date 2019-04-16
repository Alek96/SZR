import json

from GitLabApi.objects import VisibilityLevel, AccessLevel
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q, Value, When, Case
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from model_utils import FieldTracker
from social_django.models import UserSocialAuth


class BaseModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def on_class_prepared(cls):
        """Method that is run after setting the app. Here you can add extra fields.

        :return: None
        """

    def save(self, *args, **kwargs):
        self.full_clean()
        self._pre_save(*args, **kwargs)
        super().save(*args, **kwargs)
        self._post_save(*args, **kwargs)

    def _pre_save(self, *args, **kwargs):
        """
        Here Children class can set special rules in saving model

        :return: None
        """

    def _post_save(self, *args, **kwargs):
        """
        Here Children class can set special rules in saving model

        :return: None
        """


class AbstractGitlabModel(BaseModel):
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


class AbstractAccessLevel(BaseModel, AccessLevel):
    access_level = models.IntegerField(choices=AccessLevel.ACCESS_LEVEL_CHOICES, default=AccessLevel.ACCESS_GUEST)

    class Meta:
        abstract = True


class AbstractVisibilityLevel(BaseModel, VisibilityLevel):
    visibility = models.CharField(max_length=10, choices=VisibilityLevel.VISIBILITY_CHOICES,
                                  default=VisibilityLevel.PRIVATE)

    class Meta:
        abstract = True


class AbstractTaskDates(BaseModel):
    create_date = models.DateTimeField(default=timezone.now, blank=True)
    execute_date = models.DateTimeField(default=timezone.now, blank=True)
    finished_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class StatusMethods:
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

    def is_started(self):
        status = getattr(self, 'status', None)
        return not (status == self.READY or status == self.WAITING)

    def is_finished(self):
        status = getattr(self, 'status', None)
        return status == self.SUCCEED or status == self.FAILED


class AbstractStatus(BaseModel, StatusMethods):
    status = models.PositiveIntegerField(choices=StatusMethods.STATUS_CHOICES, default=StatusMethods.READY)

    class Meta:
        abstract = True


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


class AbstractTaskGroup(AbstractTaskDates, StatusMethods, ModelUrlsMethods):
    _parent_task_model = None

    name = models.CharField(max_length=2000)

    def __init__(self, *args, **kwargs):
        self._status = None
        self._tasks_number = None
        self._finished_tasks_number = None
        self._failed_task_number = None

        super().__init__(*args, **kwargs)

    tracker = None

    class Meta:
        abstract = True

    @classmethod
    def on_class_prepared(cls):
        models.ForeignKey(
            cls._parent_task_model,
            on_delete=models.CASCADE,
            related_name='child_group_task_set_%(app_label)s_%(class)s',
            null=True, blank=True
        ).contribute_to_class(cls, 'parent_task')
        create_field_tracker(cls, 'tracker')

    def refresh_from_db(self, *args, **kwargs):
        super().refresh_from_db(*args, **kwargs)
        self._status = None
        self._tasks_number = None
        self._finished_tasks_number = None
        self._failed_task_number = None

    def _pre_save(self, *args, **kwargs):
        if self.tracker.has_changed('execute_date'):
            self._update_tasks_execute_dates()

    def _update_tasks_execute_dates(self):
        for task in self.task_set:
            if not task.is_started():
                task.execute_date = self.execute_date
                task.save()

    @property
    def task_set(self):
        task_sets = []
        for attr in self.__dir__():
            if attr.startswith('task_set_'):
                task_set = getattr(self, attr)
                task_sets.extend(list(task_set.all()))
        return task_sets

    @property
    def status(self):
        if self._status is None:
            self._update_status()
        return self._status

    @property
    def tasks_number(self):
        if self._tasks_number is None:
            self._update_status()

        return self._tasks_number

    @property
    def finished_tasks_number(self):
        if self._finished_tasks_number is None:
            self._update_status()

        return self._finished_tasks_number

    def _update_status(self):
        self._tasks_number = 0
        self._finished_tasks_number = 0
        waiting = False
        running = False
        failed = False

        for task in self.task_set:
            self._tasks_number += 1
            if task.is_finished():
                self._finished_tasks_number += 1
                if task.status == self.FAILED:
                    failed = True
            elif task.is_started():
                running = True
            elif task.status == self.WAITING:
                waiting = True

        if waiting:
            self._status = self.WAITING
        elif not running and self.finished_tasks_number == 0:
            self._status = self.READY
        elif running or self.finished_tasks_number < self._tasks_number:
            self._status = self.RUNNING
        else:
            if failed:
                self._status = self.FAILED
            else:
                self._status = self.SUCCEED


class AbstractTask(AbstractTaskDates, AbstractStatus, ModelUrlsMethods):
    _parent_task_model = None
    _task_group_model = None

    owner = models.ForeignKey(GitlabUser, on_delete=models.CASCADE, related_name='owned_tasks_%(app_label)s_%(class)s')
    celery_task = models.OneToOneField(PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    error_msg = models.CharField(max_length=2000, null=True, blank=True)

    parent_task = None
    task_group = None
    tracker = None

    class Meta:
        abstract = True

    @classmethod
    def on_class_prepared(cls):
        models.ForeignKey(
            cls._parent_task_model,
            on_delete=models.CASCADE,
            related_name='child_task_set_%(app_label)s_%(class)s',
            null=True, blank=True
        ).contribute_to_class(cls, 'parent_task')
        models.ForeignKey(
            cls._task_group_model,
            on_delete=models.CASCADE,
            related_name='task_set_%(app_label)s_%(class)s',
            null=True, blank=True
        ).contribute_to_class(cls, 'task_group')
        create_field_tracker(cls, 'tracker')

    @property
    def task_name(self):
        return str(self)

    def clean(self):
        super().clean()

        if self.pk is None:
            if getattr(self, 'task_group', None) and getattr(self, 'parent_task', None):
                raise ValidationError(
                    {'parent_task': _('Do not set parent_task. It is set from task_group if task_group exist')})

        if self.pk:
            if self.tracker.has_changed('execute_date') and self.is_started():
                raise ValidationError(
                    {'execute_date': _('Execute_date cannot be change after the celery task is started')})

            if self.tracker.has_changed('status'):
                if self.status == self.WAITING:
                    raise ValidationError(
                        {'status': _('StatusMethods cannot be change to "Waiting" after creating')})

    def _pre_save(self, *args, **kwargs):
        if self.task_group:
            if not self.is_started():
                self.execute_date = self.task_group.execute_date
                self.parent_task = self.task_group.parent_task

        if self.parent_task:
            if self.parent_task.is_finished():
                if self.parent_task.status == self.FAILED:
                    self.status = self.FAILED
                    self.error_msg = "Error in parent task: {0}".format(self.parent_task.error_msg)
            else:
                self.status = self.WAITING

        if self.tracker.has_changed('status'):
            if self.is_started():
                if self.celery_task:
                    self.celery_task.delete()
                    self.celery_task = None
            if self.is_finished():
                self._update_children_tasks_status()

        if self.tracker.has_changed('execute_date'):
            if self.celery_task:
                self.celery_task.start_time = self.execute_date
                self.celery_task.save()

    def _post_save(self, *args, **kwargs):
        if self.status == self.READY:
            if not self.celery_task:
                self.celery_task = self._create_task()
                super().save(update_fields=['celery_task'])

    def _update_children_tasks_status(self):
        for task in self.child_task_set:
            task.status = self.READY
            task.save()

    @property
    def child_task_set(self):
        task_sets = []
        for attr in self.__dir__():
            if attr.startswith('child_task_set_'):
                task_set = getattr(self, attr)
                task_sets.extend(list(task_set.all()))
        return task_sets

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
