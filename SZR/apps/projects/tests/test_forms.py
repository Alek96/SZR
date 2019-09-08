from unittest import mock
import unittest

from GitLabApi import mock_all_gitlab_url
from core.tests import test_forms
from core.tests.test_view import LoginMethods
from django import forms
from groups.tests.test_forms import BaseTaskFormTest as groups_BaseTaskFormTest
from projects import forms
from projects import models
from projects.tests import models as test_models
from projects.tests.forms import FakeTaskForm
from projects.tests.models import FakeTask
from groups.tests.models import TaskGroupMethods


class AddProjectFormTests(groups_BaseTaskFormTest):
    form_class = forms.AddProjectForm
    model_class = models.AddProject
    model_methods = test_models.AddProjectCreateMethods()
    valid_form_data = {
        'name': "Group_name",
        'path': "Group_path",
        'create_type': models.AddProject.BLANK,
        'import_url': None,
        'description': "Description",
        'visibility': models.AddProject.PRIVATE,
    }
    mandatory_fields = ['name', 'path']
    readonly_fields = ['status', 'error_msg', 'finished_date']

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddProjectForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)


class AddMultipleProjectFormTests(test_forms.BaseTaskGroupFormTest):
    form_class = forms.AddMultipleProjectForm
    model_class = models.group_models.TaskGroup
    model_methods = TaskGroupMethods()
    valid_form_data = {
        'name': "My Name",
        'suffix': forms.AddMultipleProjectForm.SUFFIX_NUMBER,
        'access_level': models.AddMember.ACCESS_GUEST,
    }
    mandatory_fields = ['name', 'access_level', 'suffix']
    readonly_fields = ['status', 'finished_date', 'tasks_number', 'finished_tasks_number']

    def setUp(self):
        super().setUp()
        self.project_form = forms.AddProjectForm(AddProjectFormTests.valid_form_data)

    def _check_task_group(self, task_group):
        self.assertTrue(task_group.task_set)

        for project in task_group.task_set:
            self.assertIsInstance(project, models.AddProject)
            self.assertEqual(len(project.child_task_set), 1)
            self.assertIsInstance(project.child_task_set[0], models.AddMember)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(ValueError):
            form.save()

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_with_group_id(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(group_id=1, user_id=self.user.id, project_form=self.project_form)

        self.assertEqual(task_group.gitlab_group_id, 1)
        self._check_task_group(task_group)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_with_parent_task(self):
        parent_task = self.model_methods.create_parent_task()
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(parent_task=parent_task, user_id=self.user.id, project_form=self.project_form)

        self.assertEqual(task_group.parent_task.id, parent_task.id)
        self.assertFalse(task_group.task_set)
        # self._check_task_group(task_group)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_raise_FormNotValidError_if_creating_members_raise_error(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(forms.FormNotValidError):
            with mock.patch.object(forms.models.AddMember.objects, 'create', side_effect=Exception("Error msg")):
                form.save(group_id=1, user_id=self.user.id, project_form=self.project_form)

        with self.assertRaises(self.model_class.DoesNotExist):
            self.model_class.objects.get(id=1)

    @unittest.skip
    def test_if_status_is_finished_disable_all_fields(self):
        pass


class TaskGroupFormTests(test_forms.BaseTaskGroupFormTest):
    form_class = forms.TaskGroupForm
    model_class = models.TaskGroup
    model_methods = test_models.AbstractTaskCreateMethods()
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = ['name']
    readonly_fields = ['status', 'finished_date', 'tasks_number', 'finished_tasks_number']

    def test_save(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(ValueError):
            form.save()

    def test_save_with_project_id(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(project_id=1)

        self.assertEqual(task_group.gitlab_project_id, 1)

    def test_save_with_parent_task(self):
        parent_task = self.model_methods.create_parent_task()
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(parent_task=parent_task)

        self.assertEqual(task_group.parent_task.id, parent_task.id)

    def test_save_with_project_id_and_parent_task(self):
        parent_task = self.model_methods.create_parent_task()
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(ValueError):
            form.save(project_id=1, parent_task=parent_task)


class BaseTaskFormTest(test_forms.BaseTaskFormTest):
    form_class = FakeTaskForm
    model_class = FakeTask
    model_methods = test_models.AbstractTaskCreateMethods()
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = []
    readonly_fields = ['status', 'error_msg', 'finished_date']

    @LoginMethods.create_user_wrapper
    def test_save(self):
        """Running save method without parameters raise error"""
        form = self.form_class(self.valid_form_data)
        with self.assertRaises(ValueError):
            form.save(user_id=self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_with_project_id(self):
        form = self.form_class(self.valid_form_data)
        task = form.save(user_id=self.user.id, project_id=1)

        self.assertIsInstance(task, self.model_class)
        self.assertTrue(task.id)
        self.assertEqual(task.gitlab_project_id, 1)
        self.assertEqual(task.owner_id, self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_with_parent_task(self):
        parent_task = self.model_methods.create_parent_task()
        form = self.form_class(self.valid_form_data)
        task = form.save(user_id=self.user.id, parent_task=parent_task)

        self.assertIsInstance(task, self.model_class)
        self.assertTrue(task.id)
        self.assertEqual(task.parent_task.id, parent_task.id)
        self.assertEqual(task.owner_id, self.user.id)


class AddMemberFormTests(BaseTaskFormTest):
    form_class = forms.AddMemberForm
    model_class = models.AddMember
    model_methods = test_models.AddMemberCreateMethods()
    valid_form_data = {
        'username': "username",
        'access_level': models.AddMember.ACCESS_GUEST,
    }
    mandatory_fields = ['username']
    readonly_fields = ['status', 'error_msg', 'finished_date']

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddMemberForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, project_id=1)
