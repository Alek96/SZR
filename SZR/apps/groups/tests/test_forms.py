from django.test import TestCase
from django import forms
from django.utils import timezone

from core.exceptions import WrongFormError
from groups.forms import *
from GitLabApi import mock_all_gitlab_url
from GitLabApi.exceptions import GitlabCreateError
from core.tests.test_view import LoginMethods
from groups.tests.test_models import AddSubgroupCreateMethods, AddMemberCreateMethods


class AddSubgroupGroupFormTests(LoginMethods):
    valid_form_data = {
        'name': "name",
    }

    def test_init(self):
        AddSubgroupGroupForm()

    def test_valid_data(self):
        form = AddSubgroupGroupForm(self.valid_form_data)
        self.assertTrue(form.is_valid())
        for key, value in self.valid_form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = AddSubgroupGroupForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])

    def test_save_in_task_group(self):
        form = AddSubgroupGroupForm(self.valid_form_data)
        form.save(group_id=1)

        task_group = models.AddSubgroupGroup.objects.get(id=1)
        self.assertEqual(task_group.gitlab_group_id, 1)


class AddSubgroupFormTests(LoginMethods):
    valid_form_data = {
        'name': "Group_name",
        'path': "Group_path",
        'description': "Description",
        'visibility': models.AddSubgroup.PRIVATE,
    }

    def test_init(self):
        AddSubgroupForm()

    def test_valid_data(self):
        form = AddSubgroupForm(self.valid_form_data)
        self.assertTrue(form.is_valid())
        for key, value in self.valid_form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = AddSubgroupForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])
        self.assertEqual(form.errors['path'], ['This field is required.'])

    def test_save_in_gitlab_not_valid(self):
        form = AddSubgroupForm({})
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(user_id=1, group_id=1)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = AddSubgroupForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url(raise_error=GitlabCreateError('{"path": ["has already been taken"]}'))
    def test_save_in_gitlab_error(self):
        form = AddSubgroupForm(self.valid_form_data)
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(user_id=self.user.id, group_id=1)
        all_errors = form.errors
        self.assertIn('has already been taken', all_errors['path'][-1])

    def test_save_in_task_not_valid(self):
        form = AddSubgroupForm({})
        with self.assertRaises(WrongFormError):
            form.save(user_id=1, task_group_id=1)

    @LoginMethods.create_user_wrapper
    def test_save_in_task(self):
        form = AddSubgroupForm(self.valid_form_data)
        task_group = AddSubgroupCreateMethods().create_task_group()
        form.save(user_id=self.user.id, task_group_id=task_group.id)

        task = models.AddSubgroup.objects.get(task_group=task_group)
        for key, value in self.valid_form_data.items():
            self.assertEqual(getattr(task, key), value)
        self.assertEqual(task.owner_id, self.user.id)


class AddMemberGroupFormTests(LoginMethods):
    valid_form_data = {
        'name': "name",
    }

    def test_init(self):
        AddMemberGroupForm()

    def test_valid_data(self):
        form = AddMemberGroupForm(self.valid_form_data)
        self.assertTrue(form.is_valid())
        for key, value in self.valid_form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = AddMemberGroupForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])

    def test_save_in_task_group(self):
        form = AddMemberGroupForm(self.valid_form_data)
        form.save(group_id=1)

        task_group = models.AddMemberGroup.objects.get(id=1)
        self.assertEqual(task_group.gitlab_group_id, 1)


class AddMemberFormTests(LoginMethods):
    valid_form_data = {
        'username': "username",
        'access_level': models.AddMember.ACCESS_GUEST,
    }

    def test_init(self):
        AddMemberForm()

    def test_valid_data(self):
        form = AddMemberForm(self.valid_form_data)
        self.assertTrue(form.is_valid())
        for key, value in self.valid_form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = AddMemberForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

    def test_save_in_gitlab_not_valid(self):
        form = AddMemberForm({})
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(user_id=1, group_id=1)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = AddMemberForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url(raise_error=GitlabCreateError('{"username": ["Does not exist"]}'))
    def test_save_in_gitlab_error(self):
        form = AddMemberForm(self.valid_form_data)
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(user_id=self.user.id, group_id=1)
        all_errors = form.errors
        self.assertIn('Does not exist', all_errors['username'][-1])

    def test_save_in_task_not_valid(self):
        form = AddMemberForm({})
        with self.assertRaises(WrongFormError):
            form.save(user_id=1, task_group_id=1)

    @LoginMethods.create_user_wrapper
    def test_save_in_task(self):
        form = AddMemberForm(self.valid_form_data)
        task_group = AddMemberCreateMethods().create_task_group()
        form.save(user_id=self.user.id, task_group_id=task_group.id)

        task = models.AddMember.objects.get(task_group=task_group)
        for key, value in self.valid_form_data.items():
            self.assertEqual(getattr(task, key), value)
        self.assertEqual(task.owner_id, self.user.id)
