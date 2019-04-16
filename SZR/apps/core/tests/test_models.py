import json
import unittest
from pydoc import locate
from unittest import mock

from core.models import GitlabUser, StatusMethods, ModelUrlsMethods
from core.tasks import BaseTask
from core.tests import models as test_models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from social_django.models import UserSocialAuth


class BaseModel(TestCase):
    def test_save(self):
        model = test_models.FakeBaseModel()
        with mock.patch.object(model, '_pre_save') as mock_pre_save:
            with mock.patch.object(model, '_post_save') as mock_post_save:
                model.save()
        mock_pre_save.assert_called_once_with()
        mock_post_save.assert_called_once_with()
        self.assertTrue(model.id)


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


class GitlabUserModelTests(unittest.TestCase, GitlabUserModelMethod):
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


class FakeAccessLevelTests(TestCase):
    def test_default_values(self):
        model = test_models.FakeAccessLevel()
        self.assertEqual(model.access_level, model.ACCESS_GUEST)
        self.assertEqual(model.get_access_level_readable(), dict(model.ACCESS_LEVEL_CHOICES).get(model.ACCESS_GUEST))


class AbstractVisibilityLevelTests(TestCase):
    def test_default_values(self):
        model = test_models.FakeVisibilityLevel()
        self.assertEqual(model.visibility, model.PRIVATE)
        self.assertEqual(model.get_visibility_readable(), dict(model.VISIBILITY_CHOICES).get(model.PRIVATE))


class AbstractTaskDatesTests(TestCase):
    @freeze_time("2019-01-01")
    def test_default_values(self):
        model = test_models.FakeTaskDates()
        self.assertEqual(model.create_date, timezone.now())
        self.assertEqual(model.execute_date, timezone.now())
        self.assertEqual(model.finished_date, None)


class StatusMethodsTests(TestCase):
    def create_status(self, status):
        obj = StatusMethods()
        obj.status = status
        return obj

    def test_is_started_status_waiting(self):
        self.assertFalse(self.create_status(StatusMethods.WAITING).is_started())
        self.assertFalse(self.create_status(StatusMethods.READY).is_started())
        self.assertTrue(self.create_status(StatusMethods.RUNNING).is_started())
        self.assertTrue(self.create_status(StatusMethods.SUCCEED).is_started())
        self.assertTrue(self.create_status(StatusMethods.FAILED).is_started())

    def test_is_finished(self):
        self.assertFalse(self.create_status(StatusMethods.WAITING).is_finished())
        self.assertFalse(self.create_status(StatusMethods.READY).is_finished())
        self.assertFalse(self.create_status(StatusMethods.RUNNING).is_finished())
        self.assertTrue(self.create_status(StatusMethods.SUCCEED).is_finished())
        self.assertTrue(self.create_status(StatusMethods.FAILED).is_finished())


class AbstractTaskStatusTests(TestCase):
    def test_default_values(self):
        task_status = test_models.FakeStatus()
        self.assertEqual(task_status.status, task_status.READY)


class ModelLinksMethodsTests(TestCase):
    def setUp(self):
        self.model = ModelUrlsMethods()

    def test_edit_url(self):
        self.assertEqual(self.model.edit_url, '#')

    def test_delete_url(self):
        self.assertEqual(self.model.delete_url, '#')

    def test_tasks_page_url(self):
        self.assertEqual(self.model.tasks_page_url, '#')


class TaskGroupMethods(TestCase):
    def create_task_group(self, name='Name', **kwargs):
        return test_models.FakeTaskGroup.objects.create(
            name=name,
            **kwargs
        )


class TaskMethods(TaskGroupMethods):
    def create_task(self, owner=None, task_group=None, **kwargs):
        return test_models.FakeTask.objects.create(
            owner=owner or GitlabUser.objects.create(),
            task_group=task_group,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return self.create_task(**kwargs)


class AbstractTaskGroupTests(TaskMethods):
    def test_default_values(self):
        self.create_task_group()

    def test_refresh_from_db(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.status, task_group.READY)
        self.create_task(task_group=task_group, status=StatusMethods.SUCCEED)
        self.assertEqual(task_group.status, task_group.READY)

        task_group.refresh_from_db()
        self.assertEqual(task_group.status, task_group.SUCCEED)

    def test_task_set(self):
        task_group = self.create_task_group()
        tasks = [self.create_task(task_group=task_group), self.create_task(task_group=task_group)]

        task_set = task_group.task_set
        for task in tasks:
            self.assertIn(task, task_set)

    @freeze_time("2019-01-01")
    def test_changing_execute_date_change_tasks_set_execute_date(self):
        task_group = self.create_task_group()
        task_1 = self.create_task(task_group=task_group)
        task_2 = self.create_task(task_group=task_group, status=StatusMethods.RUNNING)

        with freeze_time("2019-01-02"):
            task_group.execute_date = timezone.now()
            task_group.save()

        task_1.refresh_from_db()
        task_2.refresh_from_db()
        self.assertEqual(task_group.execute_date, task_1.execute_date)
        self.assertNotEqual(task_group.execute_date, task_2.execute_date)

    def test_status_waiting_when_some_assigned_task_is_waiting(self):
        task_group = self.create_task_group(parent_task=self.create_parent_task())
        task = self.create_task(task_group=task_group)
        self.assertEqual(task.status, task_group.WAITING)
        self.assertEqual(task_group.status, task_group.WAITING)

    def test_status_ready_when_not_assigned_tasks(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.status, task_group.READY)

    def test_status_ready_when_all_assigned_tasks_are_ready(self):
        task_group = self.create_task_group()
        self.create_task(task_group=task_group, status=StatusMethods.READY)
        self.assertEqual(task_group.status, task_group.READY)

    def test_status_running_when_some_assigned_task_is_running(self):
        task_group = self.create_task_group()
        self.create_task(task_group=task_group, status=StatusMethods.RUNNING)
        self.assertEqual(task_group.status, task_group.RUNNING)

    def test_status_running_when_not_all_assigned_tasks_finished(self):
        task_group = self.create_task_group()
        self.create_task(task_group=task_group, status=StatusMethods.SUCCEED)
        self.create_task(task_group=task_group)
        self.assertEqual(task_group.status, task_group.RUNNING)

    def test_status_succeed_when_all_assigned_tasks_finished_with_status_succeed(self):
        task_group = self.create_task_group()
        self.create_task(task_group=task_group, status=StatusMethods.SUCCEED)
        self.assertEqual(task_group.status, task_group.SUCCEED)

    def test_status_failed_when_all_assigned_tasks_finished_with_status_succeed(self):
        task_group = self.create_task_group()
        self.create_task(task_group=task_group, status=StatusMethods.FAILED)
        self.assertEqual(task_group.status, task_group.FAILED)

    def test_task_number_with_0_assigned_tasks(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.tasks_number, 0)

    def test_task_number_with_assigned_tasks(self):
        task_group = self.create_task_group()
        self.create_task(task_group=task_group)
        self.create_task(task_group=task_group)
        self.assertEqual(task_group.tasks_number, 2)
        self.assertEqual(task_group.tasks_number, 2)

    def test_finished_task_number_with_0_assigned_tasks(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.finished_tasks_number, 0)

    def test_finished_task_number_with_assigned_tasks(self):
        task_group = self.create_task_group()
        self.create_task(task_group=task_group, status=StatusMethods.SUCCEED)
        self.create_task(task_group=task_group, status=StatusMethods.FAILED)
        self.assertEqual(task_group.finished_tasks_number, 2)
        self.assertEqual(task_group.finished_tasks_number, 2)


class AbstractTaskNotImplementedTests(TestCase):
    def test_get_task_path_raise_error(self):
        with self.assertRaises(NotImplementedError):
            test_models.FakeRaiseTask.objects.create(owner=GitlabUser.objects.create())


class AbstractTaskTests(TaskMethods):
    def test_task_name(self):
        task = self.create_task()
        self.assertEqual(task.task_name, str(task))

    def test_after_creating_with_status_waiting_celery_task_is_not_created(self):
        task = self.create_task(status=StatusMethods.WAITING)
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

    def test_after_starting_celery_task_is_deleted(self):
        def test(status):
            task = self.create_task()
            task.status = status
            task.save()
            self.assertEqual(task.celery_task, None)

        test(StatusMethods.RUNNING)
        test(StatusMethods.SUCCEED)
        test(StatusMethods.FAILED)

    def test_status_cannot_be_change_to_waiting_after_creating(self):
        def test(status):
            task = self.create_task(status=status)
            task.status = task.WAITING
            with self.assertRaises(ValidationError):
                task.save()

        test(StatusMethods.READY)
        test(StatusMethods.RUNNING)
        test(StatusMethods.SUCCEED)
        test(StatusMethods.FAILED)

    def test_creating_with_task_group_and_parent_task_raise_error(self):
        task_group = self.create_task_group()
        parent_task = self.create_parent_task()
        with self.assertRaises(ValidationError):
            self.create_task(task_group=task_group, parent_task=parent_task)

    def test_execute_date_is_copied_from_task_group_if_it_has_not_been_started(self):
        task_group = self.create_task_group()
        task = self.create_task(task_group=task_group)
        self.assertEqual(task.execute_date, task_group.execute_date)

    def test_execute_date_is_not_copied_from_task_group_if_it_has_been_started(self):
        task_group = self.create_task_group()
        task = self.create_task(task_group=task_group, status=task_group.RUNNING)
        self.assertNotEqual(task.execute_date, task_group.execute_date)

    def test_parent_task_is_copied_from_task_group_if_it_has_not_been_started(self):
        task_group = self.create_task_group(parent_task=self.create_parent_task())
        task = self.create_task(task_group=task_group)
        self.assertEqual(task.parent_task, task_group.parent_task)

    def test_parent_task_is_not_copied_from_task_group_if_it_has_been_started(self):
        task_group = self.create_task_group(parent_task=self.create_parent_task())
        task = self.create_task(task_group=task_group, status=task_group.RUNNING)
        self.assertNotEqual(task.parent_task, task_group.parent_task)

    def test_creating_with_parent_task_witch_is_not_finished_sets_status_to_waiting(self):
        def test(status):
            task = self.create_task(parent_task=self.create_parent_task(status=status))
            self.assertEqual(task.status, StatusMethods.WAITING)

        test(StatusMethods.WAITING)
        test(StatusMethods.READY)
        test(StatusMethods.RUNNING)

    def test_creating_with_parent_task_with_status_failed_set_status_to_failed(self):
        task = self.create_task(parent_task=self.create_parent_task(status=StatusMethods.FAILED))
        self.assertEqual(task.status, StatusMethods.FAILED)
        self.assertNotEqual(task.error_msg, None)

    def test_child_task_set(self):
        parent_task = self.create_parent_task()
        tasks = [self.create_task(parent_task=parent_task), self.create_task(parent_task=parent_task)]

        child_task_set = parent_task.child_task_set
        for task in tasks:
            self.assertIn(task, child_task_set)

    def test_after_finishing_with_succeed_child_task_set_statuses_is_set_to_ready(self):
        parent_task = self.create_parent_task()
        task_1 = self.create_task(parent_task=parent_task)
        task_2 = self.create_task(parent_task=parent_task)

        parent_task.status = StatusMethods.SUCCEED
        parent_task.save()

        task_1.refresh_from_db()
        task_2.refresh_from_db()
        self.assertEqual(task_1.status, task_1.READY)
        self.assertEqual(task_2.status, task_2.READY)

    def test_cannot_update_execute_date_after_starting(self):
        def test(status):
            task = self.create_task(status=status)
            with self.assertRaises(ValidationError):
                task.execute_date = timezone.now()
                task.save()

        test(StatusMethods.RUNNING)
        test(StatusMethods.SUCCEED)
        test(StatusMethods.FAILED)

    @freeze_time("2019-01-01")
    def test_after_updating_execute_date_celery_task_is_also_updated(self):
        task = self.create_task()
        old_date = task.execute_date

        with freeze_time("2019-01-02"):
            new_date = timezone.now()
            task.execute_date = new_date
            task.save()

        task.refresh_from_db()
        self.assertNotEqual(task.celery_task.start_time, old_date)
        self.assertEqual(task.celery_task.start_time, new_date)

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
