from django.test import TestCase
import unittest
from unittest import mock
from freezegun import freeze_time

from tasks.models import *
from core.utils import print_sql
from authentication.models import GitlabUser


class AbstractTaskGroupTestCase:
    class AbstractTaskGroupTests(TestCase):
        def create_group_task(self, **kwargs):
            raise NotImplementedError('AbstractTaskGroupTests must define the create_group_task method.')

        def test_default_values(self):
            task_group = self.create_group_task()
            task_group.refresh_from_db()
            self.assertEqual(task_group.status, task_group.CREATED)
            self.assertEqual(task_group.tasks_number, 0)
            self.assertEqual(task_group.finished_tasks_number, 0)
            self.assertEqual(task_group.failed_task_number, 0)

        def test_status_created(self):
            task_group = self.create_group_task(tasks_number=1)
            task_group.refresh_from_db()
            self.assertEqual(task_group.status, task_group.CREATED)

        def test_status_running(self):
            task_group = self.create_group_task(tasks_number=2, finished_tasks_number=1)
            task_group.refresh_from_db()
            self.assertEqual(task_group.status, task_group.RUNNING)

        def test_status_completed(self):
            task_group = self.create_group_task(tasks_number=1, finished_tasks_number=1)
            task_group.refresh_from_db()
            self.assertEqual(task_group.status, task_group.COMPLETED)

        def test_status_finished(self):
            task_group = self.create_group_task(tasks_number=1, finished_tasks_number=1, failed_task_number=1)
            task_group.refresh_from_db()
            self.assertEqual(task_group.status, task_group.FAILED)

        def test_increment_task_number(self):
            task_group = self.create_group_task()
            self.assertEqual(task_group.tasks_number, 0)
            task_group.increment_task_number()
            task_group.save()
            task_group.refresh_from_db()
            self.assertEqual(task_group.status, task_group.CREATED)
            self.assertEqual(task_group.tasks_number, 1)

        def test_increment_task_number_after_completed(self):
            task_group = self.create_group_task(tasks_number=1, finished_tasks_number=1,
                                                finished_date=timezone.now())
            task_group.increment_task_number()
            task_group.save()
            task_group.refresh_from_db()
            self.assertEqual(task_group.tasks_number, 2)
            self.assertEqual(task_group.status, task_group.RUNNING)
            self.assertEqual(task_group.finished_date, None)

        @freeze_time("2019-01-01")
        def test_increment_finished_tasks_number(self):
            task_group = self.create_group_task(tasks_number=2)
            task_group.increment_finished_tasks_number(task_group.COMPLETED)
            task_group.save()
            task_group.refresh_from_db()
            self.assertEqual(task_group.finished_tasks_number, 1)
            self.assertEqual(task_group.status, task_group.RUNNING)
            self.assertEqual(task_group.finished_date, None)

        @freeze_time("2019-01-01")
        def test_increment_finished_tasks_number_with_status_completed(self):
            task_group = self.create_group_task(tasks_number=1)
            task_group.increment_finished_tasks_number(task_group.COMPLETED)
            task_group.save()
            task_group.refresh_from_db()
            self.assertEqual(task_group.finished_tasks_number, 1)
            self.assertEqual(task_group.status, task_group.COMPLETED)
            self.assertEqual(task_group.finished_date, timezone.now())

        @freeze_time("2019-01-01")
        def test_increment_finished_tasks_number_with_status_failed(self):
            task_group = self.create_group_task(tasks_number=1)
            task_group.increment_finished_tasks_number(task_group.FAILED)
            task_group.save()
            task_group.refresh_from_db()
            self.assertEqual(task_group.finished_tasks_number, 1)
            self.assertEqual(task_group.status, task_group.FAILED)
            self.assertEqual(task_group.finished_date, timezone.now())


class AbstractTaskTestCase:
    class AbstractTaskTests(TestCase):
        def setUp(self):
            super().setUp()
            self.gitlab_user = GitlabUser.objects.create()
            self.task_group = None

        def create_task(self, *args, **kwargs):
            raise NotImplementedError('AbstractTaskTests must define the create_task method.')

        def test_after_created_celery_task_is_created(self):
            task = self.create_task()
            self.assertNotEqual(task.celery_task, None)
            self.assertIn("{}-{}".format(task.__class__.__name__, task.id), str(task.celery_task))
            self.assertEqual(task.celery_task.task, task._get_task_path())
            self.assertEqual(task.celery_task.kwargs, {'id': task.id})
            self.assertEqual(task.celery_task.interval, task._create_or_get_interval())
            self.assertEqual(task.celery_task.one_off, True)
            self.assertEqual(task.celery_task.start_time, task.execute_date)

        def test_after_save_second_celery_task_is_not_created(self):
            task = self.create_task()
            celery_task = task.celery_task
            task.save()
            self.assertEqual(task.celery_task, celery_task)

        def test_after_finished_second_celery_task_is_not_created(self):
            task = self.create_task()
            task.celery_task.delete()
            task.refresh_from_db()
            task.status = task.COMPLETED
            task.save()
            self.assertEqual(task.celery_task, None)

        @freeze_time("2019-01-01")
        def test_after_updating_execute_date_celery_task_is_also_updated(self):
            task = self.create_task()
            old_date_ = task.execute_date

            with freeze_time("2019-01-02"):
                new_date = timezone.now()
                task.execute_date = new_date
                task.save()

            task.refresh_from_db()
            self.assertNotEqual(task.execute_date, old_date_)
            self.assertEqual(task.execute_date, new_date)
            self.assertEqual(task.celery_task.start_time, new_date)

        @freeze_time("2019-01-01")
        def test_updating_execute_date_after_running_raise_error(self):
            task = self.create_task()
            task.status = task.RUNNING
            task.save()

            with freeze_time("2019-01-02"):
                with self.assertRaises(ValidationError):
                    task.execute_date = timezone.now()
                    task.save()

        @freeze_time("2019-01-01")
        def test_updating_execute_date_on_task_group_level(self):
            task_1 = self.create_task()
            task_2 = self.create_task()
            task_2.status = task_2.RUNNING
            task_2.save()

            with freeze_time("2019-01-02"):
                self.task_group.execute_date = timezone.now()
                self.task_group.save()

            self.task_group.refresh_from_db()
            task_1.refresh_from_db()
            task_2.refresh_from_db()
            self.assertEqual(self.task_group.execute_date, task_1.execute_date)
            self.assertNotEqual(self.task_group.execute_date, task_2.execute_date)


class ExampleTaskGroupTests(AbstractTaskGroupTestCase.AbstractTaskGroupTests):
    def create_group_task(self, **kwargs):
        return ExampleTaskGroup.objects.create(**kwargs)


class ExampleTaskTests(AbstractTaskTestCase.AbstractTaskTests):
    def setUp(self):
        super().setUp()
        self.task_group = ExampleTaskGroup.objects.create()

    def create_task(self, **kwargs):
        return ExampleTask.objects.create(owner=self.gitlab_user, task_group=self.task_group, **kwargs)
