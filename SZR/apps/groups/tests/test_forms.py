from unittest import mock

from GitLabApi import mock_all_gitlab_url
from core.tests.test_view import LoginMethods
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from groups import forms
from groups import models
from groups.tests.forms import FakeTaskForm
from groups.tests.models import FakeTask
from groups.tests import models as test_models
from core.tests import test_forms
from core.models import GitlabUser


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

    def test_save_with_group_id(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(group_id=1)

        self.assertEqual(task_group.gitlab_group_id, 1)

    def test_save_with_parent_task(self):
        parent_task = self.model_methods.create_parent_task()
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(parent_task=parent_task)

        self.assertEqual(task_group.parent_task.id, parent_task.id)

    def test_save_with_group_id_and_parent_task(self):
        parent_task = self.model_methods.create_parent_task()
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(ValueError):
            form.save(group_id=1, parent_task=parent_task)


class BaseTaskFormTest(test_forms.BaseTaskFormTest):
    form_class = FakeTaskForm
    model_class = FakeTask
    model_methods = test_models.AbstractTaskCreateMethods()
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = []
    readonly_fields = ['status', 'error_msg', 'execute_date', 'finished_date']

    @LoginMethods.create_user_wrapper
    def test_save(self):
        """Running save method without parameters raise error"""
        form = self.form_class(self.valid_form_data)
        with self.assertRaises(ValueError):
            form.save(user_id=self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_with_group_id(self):
        form = self.form_class(self.valid_form_data)
        task = form.save(user_id=self.user.id, group_id=1)

        self.assertIsInstance(task, self.model_class)
        self.assertTrue(task.id)
        self.assertEqual(task.gitlab_group_id, 1)
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


class AddSubgroupFormTests(BaseTaskFormTest):
    form_class = forms.AddSubgroupForm
    model_class = models.AddSubgroup
    model_methods = test_models.AddSubgroupCreateMethods()
    valid_form_data = {
        'name': "Group_name",
        'path': "Group_path",
        'description': "Description",
        'visibility': models.AddSubgroup.PRIVATE,
    }
    mandatory_fields = ['name', 'path']
    readonly_fields = ['status', 'error_msg', 'execute_date', 'finished_date']

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddSubgroupForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)


class AddProjectFormTests(BaseTaskFormTest):
    form_class = forms.AddProjectForm
    model_class = models.AddProject
    model_methods = test_models.AddProjectCreateMethods()
    valid_form_data = {
        'name': "Group_name",
        'path': "Group_path",
        # 'create_type': models.AddProject.BLANK,
        # 'import_url': '',
        'description': "Description",
        'visibility': models.AddProject.PRIVATE,
    }
    mandatory_fields = ['name', 'path']
    readonly_fields = ['status', 'error_msg', 'execute_date', 'finished_date']

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddProjectForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)


class AddMemberFormTests(BaseTaskFormTest):
    form_class = forms.AddMemberForm
    model_class = models.AddMember
    model_methods = test_models.AddMemberCreateMethods()
    valid_form_data = {
        'username': "username",
        'access_level': models.AddMember.ACCESS_GUEST,
    }
    mandatory_fields = ['username']
    readonly_fields = ['status', 'error_msg', 'execute_date', 'finished_date']

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddMemberForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)


class MembersFromFileFormTests(TaskGroupFormTests):
    form_class = forms.MembersFromFileForm
    model_class = models.TaskGroup
    model_methods = test_models.AbstractTaskCreateMethods()
    valid_form_data = {
        'name': "My Name",
        'access_level': models.AddMember.ACCESS_GUEST,
    }
    valid_file_data = {
        'file': SimpleUploadedFile('file_members.csv', b'"surname";"name";0;0;999998\n'
                                                       b'"surname";"name";0;0;999999'),
    }
    mandatory_fields = ['name', 'access_level', 'file']
    readonly_fields = ['status', 'finished_date', 'tasks_number', 'finished_tasks_number']

    def _check_task_group(self, task_group):
        self.assertEqual(task_group.task_set[0].username, '999998')
        self.assertEqual(task_group.task_set[0].access_level, self.valid_form_data['access_level'])

        self.assertEqual(task_group.task_set[1].username, '999999')
        self.assertEqual(task_group.task_set[1].access_level, self.valid_form_data['access_level'])

    @LoginMethods.create_user_wrapper
    def test_save_with_group_id(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(group_id=1, user_id=self.user.id)

        self.assertEqual(task_group.gitlab_group_id, 1)
        self._check_task_group(task_group)

    @LoginMethods.create_user_wrapper
    def test_save_with_parent_task(self):
        parent_task = self.model_methods.create_parent_task()
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(parent_task=parent_task, user_id=self.user.id)

        self.assertEqual(task_group.parent_task.id, parent_task.id)
        self._check_task_group(task_group)

    @LoginMethods.create_user_wrapper
    def test_save_raise_FormNotValidError_if_parser_raise_error(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(forms.FormNotValidError):
            with mock.patch.object(forms, 'csv_members_parse', side_effect=Exception("Error msg")):
                form.save(group_id=1, user_id=self.user.id)

        with self.assertRaises(self.model_class.DoesNotExist):
            self.model_class.objects.get(id=1)

    @LoginMethods.create_user_wrapper
    def test_save_raise_FormNotValidError_if_creating_members_raise_error(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(forms.FormNotValidError):
            with mock.patch.object(forms.models.AddMember.objects, 'create', side_effect=Exception("Error msg")):
                form.save(group_id=1, user_id=self.user.id)

        with self.assertRaises(self.model_class.DoesNotExist):
            self.model_class.objects.get(id=1)


class SubgroupAndMembersFromFileFormTests(TaskGroupFormTests):
    form_class = forms.SubgroupAndMembersFromFileForm
    model_class = models.TaskGroup
    model_methods = test_models.AbstractTaskCreateMethods()
    valid_form_data = {
        'name': "My Name",
        'visibility': models.AddSubgroup.PRIVATE,
        'access_level': models.AddMember.ACCESS_GUEST,
    }
    valid_file_data = {
        'file': SimpleUploadedFile('file_subgroups_members.csv',
                                   b'999997;"name";"surname";0;"LAB101, WYK1";"103B-ISP-IN"\n'
                                   b'999998;"name";"surname";0;"LAB102, WYK1";"103B-ISP-IN"\n'
                                   b'999999;"name";"surname";0;"LAB102, WYK1";"103B-ISP-IN"'),
    }
    mandatory_fields = ['name', 'access_level', 'file']
    readonly_fields = ['status', 'finished_date', 'tasks_number', 'finished_tasks_number']

    def _check_task_group(self, task_group, owner_id):
        owner = GitlabUser.objects.get(id=owner_id)

        subgroup_0 = task_group.task_set[0]
        subgroup_0_member_0 = subgroup_0.child_task_set[0]
        subgroup_1 = task_group.task_set[1]
        subgroup_1_member_0 = subgroup_0.child_task_set[0]
        subgroup_1_member_1 = subgroup_1.child_task_set[1]
        subgroup_1_member_2 = subgroup_1.child_task_set[2]
        subgroup_2 = task_group.task_set[2]
        subgroup_2_member_0 = subgroup_2.child_task_set[0]
        subgroup_2_member_1 = subgroup_2.child_task_set[1]

        self.assertEqual(subgroup_0.owner, owner)
        self.assertEqual(subgroup_0.name, 'LAB101')
        self.assertEqual(subgroup_0.path, 'LAB101')
        self.assertEqual(subgroup_0.visibility, self.valid_form_data['visibility'])

        self.assertEqual(subgroup_0_member_0.username, '999997')
        self.assertEqual(subgroup_0_member_0.access_level, self.valid_form_data['access_level'])

        self.assertEqual(subgroup_1.owner, owner)
        self.assertEqual(subgroup_1.name, 'WYK1')
        self.assertEqual(subgroup_1.path, 'WYK1')
        self.assertEqual(subgroup_1.visibility, self.valid_form_data['visibility'])

        self.assertEqual(subgroup_1_member_0.username, '999997')
        self.assertEqual(subgroup_1_member_0.access_level, self.valid_form_data['access_level'])

        self.assertEqual(subgroup_1_member_1.username, '999998')
        self.assertEqual(subgroup_1_member_1.access_level, self.valid_form_data['access_level'])

        self.assertEqual(subgroup_1_member_2.username, '999999')
        self.assertEqual(subgroup_1_member_2.access_level, self.valid_form_data['access_level'])

        self.assertEqual(subgroup_2.owner, owner)
        self.assertEqual(subgroup_2.name, 'LAB102')
        self.assertEqual(subgroup_2.path, 'LAB102')
        self.assertEqual(subgroup_2.visibility, self.valid_form_data['visibility'])

        self.assertEqual(subgroup_2_member_0.username, '999998')
        self.assertEqual(subgroup_2_member_0.access_level, self.valid_form_data['access_level'])

        self.assertEqual(subgroup_2_member_1.username, '999999')
        self.assertEqual(subgroup_2_member_1.access_level, self.valid_form_data['access_level'])

    @LoginMethods.create_user_wrapper
    def test_save_with_group_id(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(group_id=1, user_id=self.user.id)

        self.assertEqual(task_group.gitlab_group_id, 1)
        self._check_task_group(task_group, self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_with_parent_task(self):
        parent_task = self.model_methods.create_parent_task()
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        task_group = form.save(parent_task=parent_task, user_id=self.user.id)

        self.assertEqual(task_group.parent_task.id, parent_task.id)
        self._check_task_group(task_group, self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_raise_FormNotValidError_if_parser_raise_error(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(forms.FormNotValidError):
            with mock.patch.object(forms, 'csv_subgroup_and_members_parse', side_effect=Exception("Error msg")):
                form.save(group_id=1, user_id=self.user.id)

        with self.assertRaises(self.model_class.DoesNotExist):
            self.model_class.objects.get(id=1)

    @LoginMethods.create_user_wrapper
    def test_save_raise_FormNotValidError_if_creating_members_raise_error(self):
        form = self.form_class(self.valid_form_data, self.valid_file_data)
        with self.assertRaises(forms.FormNotValidError):
            with mock.patch.object(forms.models.AddMember.objects, 'create', side_effect=Exception("Error msg")):
                form.save(group_id=1, user_id=self.user.id)

        with self.assertRaises(self.model_class.DoesNotExist):
            self.model_class.objects.get(id=1)
