import unittest
from unittest import mock
from django.test import TestCase
from django.utils import timezone
import json
from freezegun import freeze_time

from core.models import *
from core.tests.tasks import *
from core.tests import models


class BaseTaskTests(TestCase):
    _task_cls = FakeTask

    def setUp(self):
        super().setUp()
        self.gitlab_user = GitlabUser.objects.create()
        self.task_group_model = models.FakeTaskGroup.objects.create()
        self.task_model = models.FakeTask.objects.create(
            owner=self.gitlab_user,
            task_group=self.task_group_model
        )

    def get_run_args(self):
        return json.loads(self.task_model.celery_task.kwargs)

    def test_name_is_set_correctly(self):
        task = self._task_cls()
        self.assertEqual(task.name, '{0}.{1}'.format(task.__module__, task.__name__))

    @freeze_time("2019-01-01")
    def test_if_run_method_is_not_implemented_save_error(self):
        class FakeRaiseTask(BaseTask):
            _task_model = models.FakeTask

        FakeRaiseTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.task_model.task_group.refresh_from_db()  # Bug in Django 2.0
        self.assertEqual(self.task_model.celery_task, None)
        self.assertEqual(self.task_model.error_msg, "Task must define the _run method.")
        self.assertEqual(self.task_model.status, self.task_model.FAILED)
        self.assertEqual(self.task_model.finished_date, timezone.now())
        self.assertEqual(self.task_model.task_group.finished_tasks_number, 1)

    @freeze_time("2019-01-01")
    def test_run_failed(self):
        task = self._task_cls()
        with mock.patch.object(task, '_run', side_effect=RuntimeError("Error msg")) as mock_run:
            task.run(**self.get_run_args())
        mock_run.assert_called_once_with()

        self.task_model.refresh_from_db()
        self.task_model.task_group.refresh_from_db()  # Bug in Django 2.0
        self.assertEqual(self.task_model.celery_task, None)
        self.assertEqual(self.task_model.error_msg, "Error msg")
        self.assertEqual(self.task_model.status, self.task_model.FAILED)
        self.assertEqual(self.task_model.finished_date, timezone.now())
        self.assertEqual(self.task_model.task_group.finished_tasks_number, 1)

    @freeze_time("2019-01-01")
    def test_run_correctly(self):
        self._task_cls().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.task_model.task_group.refresh_from_db()  # Bug in Django 2.0
        self.assertEqual(self.task_model.celery_task, None)
        self.assertEqual(self.task_model.error_msg, None)
        self.assertEqual(self.task_model.status, self.task_model.COMPLETED)
        self.assertEqual(self.task_model.finished_date, timezone.now())
        self.assertEqual(self.task_model.task_group.finished_tasks_number, 1)
