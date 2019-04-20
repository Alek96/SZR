import json
from unittest import mock

from core.tasks import BaseTask
from core.tests import models
from core.tests.tasks import FakeTask
from core.tests.models import TaskCreateMethods
from django.utils import timezone
from django.test import TestCase
from freezegun import freeze_time


class BaseTaskTests(TestCase, TaskCreateMethods):
    _task_cls = FakeTask

    def setUp(self):
        super().setUp()
        self.task_model = self.create_task()

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
        self.assertEqual(self.task_model.error_msg, "Task must define the _run method.")
        self.assertEqual(self.task_model.status, self.task_model.FAILED)
        self.assertEqual(self.task_model.finished_date, timezone.now())

    @freeze_time("2019-01-01")
    def test_run_failed(self):
        task = self._task_cls()
        with mock.patch.object(task, '_run', side_effect=RuntimeError("Error msg")) as mock_run:
            task.run(**self.get_run_args())
        mock_run.assert_called_once_with()

        self.task_model.refresh_from_db()
        self.assertEqual(self.task_model.error_msg, "Error msg")
        self.assertEqual(self.task_model.status, self.task_model.FAILED)
        self.assertEqual(self.task_model.finished_date, timezone.now())

    @freeze_time("2019-01-01")
    def test_run_correctly(self):
        self._task_cls().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.assertEqual(self.task_model.error_msg, None)
        self.assertEqual(self.task_model.status, self.task_model.SUCCEED)
        self.assertEqual(self.task_model.finished_date, timezone.now())
