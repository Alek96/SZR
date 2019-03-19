from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from model_utils import FieldTracker

from core.models import AbstractGitlabModel
from core.models import GitlabUser
from core.models import AbstractTaskGroup, AbstractTask


class FakeTaskGroup(AbstractTaskGroup):
    tracker = FieldTracker()  # We need specified this field every time after inheritance


class FakeTask(AbstractTask):
    task_group = models.ForeignKey(FakeTaskGroup, on_delete=models.CASCADE, related_name='tasks_set')
    tracker = FieldTracker()  # We need specified this field every time after inheritance

    def _get_task_path(self):
        return 'core.tests.tasks.FakeTask'


class FakeRaiseTaskGroup(AbstractTaskGroup):
    tracker = FieldTracker()  # We need specified this field every time after inheritance


class FakeRaiseTask(AbstractTask):
    task_group = models.ForeignKey(FakeRaiseTaskGroup, on_delete=models.CASCADE, related_name='tasks_set')
    tracker = FieldTracker()  # We need specified this field every time after inheritance
