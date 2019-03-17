import unittest
from django.test import TestCase
from django.utils import timezone
import json
from freezegun import freeze_time

from core.tests.test_models import AbstractTaskGroupAndTaskMethods


class BaseTaskTestCase:
    class BaseTaskTests(TestCase):
        _task_cls = None
        _task_group_and_task_methods_class = AbstractTaskGroupAndTaskMethods

        def setUp(self):
            self._task_group_and_task_methods = self._task_group_and_task_methods_class()
            self.task_model = self._task_group_and_task_methods.create_task()

        def run_task(self):
            task = self._task_cls()
            args = json.loads(self.task_model.celery_task.kwargs)
            task.run(**args)
            return task

        def test_name_is_set_correctly(self):
            task = self._task_cls()
            self.assertEqual(task.name, '{0}.{1}'.format(task.__module__, task.__name__))

        @freeze_time("2019-01-01")
        def test_run(self):
            self.run_task()
            self.task_model.refresh_from_db()
            self.assertEqual(self.task_model.celery_task, None)
            self.assertEqual(self.task_model.status, self.task_model.COMPLETED)
            self.assertEqual(self.task_model.finished_date, timezone.now())
            self.assertEqual(self.task_model.task_group.finished_tasks_number, 1)
