import unittest
from unittest import mock
from django.test import TestCase
from freezegun import freeze_time
from pydoc import locate

from core.models import *
from core.tasks import BaseTask
from core.tests.models import *


class GitlabUserModelMethod:

    @staticmethod
    def create_gitlab_user(gitlab_id=42, save=True, **kwargs):
        gitlab_user = GitlabUser(gitlab_id=gitlab_id, **kwargs)
        if save:
            gitlab_user.save()
        return gitlab_user

    @staticmethod
    def create_user_and_user_social_auth(username='userTest', password='password', email='email@example.com',
                                         first_name='name', last_name='', provider='gitlab', uid=500, extra_data=None):

        if not extra_data:
            extra_data = {"auth_time": 0, "id": uid, "expires": None, "refresh_token": "aaa", "access_token": "bbb",
                          "token_type": "bearer"}

        user = User.objects.create(username=username, email=email, password=password,
                                   first_name=first_name, last_name=last_name)
        user_social_auth = UserSocialAuth.objects.create(provider=provider, uid=uid, user_id=user.id,
                                                         extra_data=extra_data)

        return user, user_social_auth


class GitlabUserModelUnitTests(unittest.TestCase, GitlabUserModelMethod):
    def test_representation(self):
        user = self.create_gitlab_user(save=False)
        self.assertEqual(repr(user), "<User: {}>".format(user.id))

    def test_string_representation(self):
        user = self.create_gitlab_user(save=False)
        self.assertEqual(str(user), "<User: {}>".format(user.id))

    def test_social_auth_does_not_exists_and_does_not_has_access_token(self):
        user = self.create_gitlab_user(save=False)
        self.assertFalse(user.has_access_token())
        with self.assertRaises(RuntimeError):
            self.assertEqual(user.get_access_token(), None)

    def test_social_auth_does_not_has_access_token(self):
        user = self.create_gitlab_user(save=False)
        user.user_social_auth = UserSocialAuth()
        self.assertFalse(user.has_access_token())
        with self.assertRaises(RuntimeError):
            self.assertEqual(user.get_access_token(), None)

    def test_social_auth_has_access_token(self):
        access_token = 'token'
        user = self.create_gitlab_user(save=False)
        user.user_social_auth = UserSocialAuth()
        user.user_social_auth.extra_data['access_token'] = access_token
        self.assertTrue(user.has_access_token())
        self.assertEqual(user.get_access_token(), access_token)


class AbstractTaskStatus(TestCase):
    def test_default_values(self):
        task_status = FakeTaskStatus()
        self.assertEqual(task_status.status, task_status.READY)

    def test_is_started(self):
        self.assertFalse(FakeTaskStatus(status=FakeTaskStatus.WAITING).is_started())
        self.assertFalse(FakeTaskStatus(status=FakeTaskStatus.READY).is_started())
        self.assertTrue(FakeTaskStatus(status=FakeTaskStatus.RUNNING).is_started())
        self.assertTrue(FakeTaskStatus(status=FakeTaskStatus.SUCCEED).is_started())
        self.assertTrue(FakeTaskStatus(status=FakeTaskStatus.FAILED).is_started())

    def test_is_finished(self):
        self.assertFalse(FakeTaskStatus(status=FakeTaskStatus.WAITING).is_finished())
        self.assertFalse(FakeTaskStatus(status=FakeTaskStatus.READY).is_finished())
        self.assertFalse(FakeTaskStatus(status=FakeTaskStatus.RUNNING).is_finished())
        self.assertTrue(FakeTaskStatus(status=FakeTaskStatus.SUCCEED).is_finished())
        self.assertTrue(FakeTaskStatus(status=FakeTaskStatus.FAILED).is_finished())


class ModelLinksMethodsTests(TestCase):
    def setUp(self):
        self.model = ModelLinksMethods()

    def test_link_to_edit(self):
        self.assertEqual(self.model.link_to_edit, '#')

    def test_link_to_delete(self):
        self.assertEqual(self.model.link_to_delete, '#')

    def test_link_to_tasks_page(self):
        self.assertEqual(self.model.link_to_tasks_page, '#')


class TaskGroupAndTaskMethods(TestCase):
    def setUp(self):
        self.task_group = self.create_task_group()

    def create_task_group(self, **kwargs):
        return FakeTaskGroup.objects.create(**kwargs)

    def create_task(self, owner=None, task_group=None, **kwargs):
        return FakeTask.objects.create(
            owner=owner or GitlabUser.objects.create(),
            task_group=task_group or getattr(self, 'task_group', self.create_task_group()),
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return self.create_task(
            task_group=self.create_task_group(),
            **kwargs
        )


class AbstractTaskGroupTests(TaskGroupAndTaskMethods):
    def test_default_values(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.tasks_number, 0)
        self.assertEqual(task_group.finished_tasks_number, 0)
        self.assertEqual(task_group.failed_task_number, 0)

    def test_link_to_new_task(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.link_to_new_task, '#')

    def test_status_ready(self):
        task_group = self.create_task_group(tasks_number=1)
        self.assertEqual(task_group.status, task_group.READY)

    def test_status_running(self):
        task_group = self.create_task_group(tasks_number=2, finished_tasks_number=1)
        self.assertEqual(task_group.status, task_group.RUNNING)

    def test_status_succeed(self):
        task_group = self.create_task_group(tasks_number=1, finished_tasks_number=1)
        self.assertEqual(task_group.status, task_group.SUCCEED)

    def test_status_finished(self):
        task_group = self.create_task_group(tasks_number=1, finished_tasks_number=1, failed_task_number=1)
        self.assertEqual(task_group.status, task_group.FAILED)

    def test_increment_task_number(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.tasks_number, 0)
        task_group.increment_task_number()
        task_group.save()
        self.assertEqual(task_group.status, task_group.READY)
        self.assertEqual(task_group.tasks_number, 1)

    def test_increment_task_number_after_completed(self):
        task_group = self.create_task_group(tasks_number=1, finished_tasks_number=1,
                                            finished_date=timezone.now())
        task_group.increment_task_number()
        task_group.save()
        self.assertEqual(task_group.tasks_number, 2)
        self.assertEqual(task_group.status, task_group.RUNNING)
        self.assertEqual(task_group.finished_date, None)

    @freeze_time("2019-01-01")
    def test_increment_finished_tasks_number(self):
        task_group = self.create_task_group(tasks_number=2)
        task_group.increment_finished_tasks_number(task_group.SUCCEED)
        task_group.save()
        self.assertEqual(task_group.finished_tasks_number, 1)
        self.assertEqual(task_group.status, task_group.RUNNING)
        self.assertEqual(task_group.finished_date, None)

    @freeze_time("2019-01-01")
    def test_increment_finished_tasks_number_with_status_completed(self):
        task_group = self.create_task_group(tasks_number=1)
        task_group.increment_finished_tasks_number(task_group.SUCCEED)
        task_group.save()
        self.assertEqual(task_group.finished_tasks_number, 1)
        self.assertEqual(task_group.status, task_group.SUCCEED)
        self.assertEqual(task_group.finished_date, timezone.now())

    @freeze_time("2019-01-01")
    def test_increment_finished_tasks_number_with_status_failed(self):
        task_group = self.create_task_group(tasks_number=1)
        task_group.increment_finished_tasks_number(task_group.FAILED)
        task_group.save()
        self.assertEqual(task_group.finished_tasks_number, 1)
        self.assertEqual(task_group.status, task_group.FAILED)
        self.assertEqual(task_group.finished_date, timezone.now())

    @freeze_time("2019-01-01")
    def test_changing_execute_date_change_tasks_set_execute_date(self):
        task_group = self.create_task_group()
        task_1 = self.create_task(task_group=task_group)
        task_2 = self.create_task(task_group=task_group)
        task_2.status = task_2.RUNNING
        task_2.save()

        with freeze_time("2019-01-02"):
            task_group.execute_date = timezone.now()
            task_group.save()

        task_1.refresh_from_db()
        task_2.refresh_from_db()
        self.assertEqual(task_group.execute_date, task_1.execute_date)
        self.assertNotEqual(task_group.execute_date, task_2.execute_date)

    def test_cannot_change_status_to_waiting_after_creating(self):
        task_group = self.create_task_group()
        task_group.status = task_group.WAITING

        with self.assertRaises(ValidationError):
            task_group.save()

    def test_creating_with_parent_task_witch_is_not_finished_sets_status_to_waiting(self):
        task_group = self.create_task_group(parent_task=self.create_parent_task())
        self.assertEqual(task_group.status, task_group.WAITING)

    def test_changing_status_to_ready_change_tasks_set_status_to_ready_from_waiting(self):
        task_group = self.create_task_group(status=FakeTaskGroup.WAITING)
        self.assertEqual(task_group.status, task_group.WAITING)
        task_1 = self.create_task(task_group=task_group)
        task_2 = self.create_task(task_group=task_group)
        self.assertEqual(task_1.status, task_1.WAITING)
        self.assertEqual(task_2.status, task_2.WAITING)

        task_group.status = task_group.READY
        task_group.save()

        task_1.refresh_from_db()
        task_2.refresh_from_db()
        self.assertEqual(task_1.status, task_1.READY)
        self.assertEqual(task_2.status, task_2.READY)


class AbstractTaskNotImplementedTests(TestCase):
    def setUp(self):
        super().setUp()
        self.gitlab_user = GitlabUser.objects.create()
        self.task_group = FakeRaiseTaskGroup.objects.create()

    def create_task(self, **kwargs):
        return FakeRaiseTask.objects.create(
            owner=self.gitlab_user,
            task_group=self.task_group,
            **kwargs
        )

    def test_get_task_path_raise_error(self):
        with self.assertRaises(NotImplementedError):
            self.create_task()


class AbstractTaskTests(TaskGroupAndTaskMethods):
    def test_task_name(self):
        task = self.create_task()
        self.assertEqual(task.task_name, str(task))

    def test_after_creating_task_group_is_updated(self):
        task = self.create_task()
        # task group
        self.assertEqual(task.task_group.tasks_number, 1)
        self.assertEqual(task.execute_date, task.task_group.execute_date)

    def test_after_creating_with_status_waiting_celery_task_is_not_created(self):
        task = self.create_task(status=FakeTask.WAITING)
        self.assertEqual(task.celery_task, None)

    def test_after_creating_celery_task_is_created(self):
        task = self.create_task()
        # celery task
        self.assertNotEqual(task.celery_task, None)
        self.assertIn("{}-{}".format(task.__class__.__name__, task.id), str(task.celery_task))
        self.assertEqual(task.celery_task.task, task._get_task_path())
        self.assertEqual(task.celery_task.kwargs, json.dumps({"task_id": task.id}))
        self.assertEqual(task.celery_task.interval, task._get_or_create_interval())
        self.assertEqual(task.celery_task.enabled, True)
        self.assertEqual(task.celery_task.one_off, True)
        self.assertEqual(task.celery_task.start_time, task.execute_date)

    def test_after_saving_second_celery_task_is_not_created(self):
        task = self.create_task()
        celery_task = task.celery_task
        task.save()
        self.assertEqual(task.celery_task, celery_task)

    def _test_after_starting_celery_task_is_deleted(self, status):
        task = self.create_task()
        task.status = status
        task.save()
        self.assertEqual(task.celery_task, None)

    def test_after_starting_celery_task_is_deleted_with_status_RUNNING(self):
        self._test_after_starting_celery_task_is_deleted(FakeTask.RUNNING)

    def test_after_starting_celery_task_is_deleted_with_status_SUCCEED(self):
        self._test_after_starting_celery_task_is_deleted(FakeTask.SUCCEED)

    def test_after_starting_celery_task_is_deleted_with_status_FAILED(self):
        self._test_after_starting_celery_task_is_deleted(FakeTask.FAILED)

    def _test_after_finishing_task_group_is_updated(self, status):
        task = self.create_task()
        task.status = status
        task.save()
        task.refresh_from_db()
        self.assertEqual(task.task_group.finished_tasks_number, 1)

    def test_after_finishing_task_group_is_updated_with_status_succeed(self):
        self._test_after_finishing_task_group_is_updated(FakeTask.SUCCEED)

    def test_after_finishing_task_group_is_updated_with_status_failed(self):
        self._test_after_finishing_task_group_is_updated(FakeTask.FAILED)

    def _test_can_update_execute_date(self, status):
        task = self.create_task(status=status)
        old_date_ = task.execute_date

        with freeze_time("2019-01-02"):
            new_date = timezone.now()
            task.execute_date = new_date
            task.save()

        task.refresh_from_db()
        self.assertNotEqual(task.execute_date, old_date_)
        self.assertEqual(task.execute_date, new_date)

    @freeze_time("2019-01-01")
    def test_can_update_execute_date_with_status_ready(self):
        self._test_can_update_execute_date(FakeTask.READY)

    @freeze_time("2019-01-01")
    def test_can_update_execute_date_with_status_waiting(self):
        self._test_can_update_execute_date(FakeTask.WAITING)

    @freeze_time("2019-01-01")
    def test_after_updating_execute_date_celery_task_is_also_updated(self):
        task = self.create_task()
        old_date_ = task.execute_date

        with freeze_time("2019-01-02"):
            new_date = timezone.now()
            task.execute_date = new_date
            task.save()

        task.refresh_from_db()
        self.assertNotEqual(task.celery_task.start_time, old_date_)
        self.assertEqual(task.celery_task.start_time, new_date)

    def _test_updating_execute_date_after_running_raise_error(self, status):
        task = self.create_task()
        task.status = status
        task.save()

        with self.assertRaises(ValidationError):
            task.execute_date = timezone.now()
            task.save()

    @freeze_time("2019-01-01")
    def test_updating_execute_date_after_running_raise_error_with_status_running(self):
        self._test_updating_execute_date_after_running_raise_error(FakeTask.RUNNING)

    @freeze_time("2019-01-01")
    def test_updating_execute_date_after_running_raise_error_with_status_succeed(self):
        self._test_updating_execute_date_after_running_raise_error(FakeTask.SUCCEED)

    @freeze_time("2019-01-01")
    def test_updating_execute_date_after_running_raise_error_with_status_failed(self):
        self._test_updating_execute_date_after_running_raise_error(FakeTask.FAILED)

    def test_creating_task_with_task_group_status_waiting_set_status_to_waiting(self):
        task_group = self.create_task_group(status=FakeTaskGroup.WAITING)
        task = self.create_task(task_group=task_group)
        self.assertEqual(task.status, task.WAITING)

    def _test_after_finishing_child_task_groups_are_updated(self, status):
        task = self.create_parent_task()
        task_group_1 = self.create_task_group(parent_task=task)
        task_group_2 = self.create_task_group(parent_task=task)
        task.refresh_from_db()

        task.status = status
        task.save()
        task_group_1.refresh_from_db()
        task_group_2.refresh_from_db()
        self.assertEqual(task_group_1.status, task_group_1.READY)
        self.assertEqual(task_group_2.status, task_group_2.READY)

    def test_after_finishing_child_task_groups_are_updated_with_status_succeed(self):
        self._test_after_finishing_child_task_groups_are_updated(FakeTask.SUCCEED)

    def test_after_finishing_child_task_group_is_updated_with_status_failed(self):
        self._test_after_finishing_child_task_groups_are_updated(FakeTask.FAILED)

    def test_path_to_task(self):
        task = self.create_task()
        class_task = locate(task._get_task_path())
        assert issubclass(class_task, BaseTask)

    def test_celery_run_task_class(self):
        task = self.create_task()
        class_task = locate(task._get_task_path())
        args = json.loads(task.celery_task.kwargs)
        with mock.patch.object(class_task, '_run') as mock_run:
            class_task().delay(**args)
        mock_run.assert_called_once_with()
