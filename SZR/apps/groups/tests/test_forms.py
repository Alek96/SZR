from django.test import TestCase
from django import forms

from groups.forms import *
from GitLabApi import mock_all_gitlab_url
from GitLabApi.exceptions import GitlabCreateError
from core.tests.test_view import LoginMethods


class FakeFormMethods(FormMethods):
    name = forms.CharField(label='Name', max_length=50, initial='name')
    path = forms.SlugField(label='Path', max_length=50, initial='path')


class FormMethodsTest(TestCase):
    def test_add_error_dict(self):
        dict = {
            'name': 'error 1',
            'path': 'error 2',
        }
        form = FakeFormMethods({})
        form.add_error_dict(dict)
        all_errors = form.errors.as_data()

        for key, value in dict.items():
            self.assertIn(value, str(all_errors[key][-1]))

    def test_add_error_dict_list(self):
        dict = {
            'name': ['error 1.1', 'error 1.2'],
            'path': ['error 2.1', 'error 2.2'],
        }
        form = FakeFormMethods({})
        form.add_error_dict(dict)
        all_errors = form.errors.as_data()

        for key, value in dict.items():
            self.assertIn(value[0], str(all_errors[key][-2]))
            self.assertIn(value[1], str(all_errors[key][-1]))


class VisibilityLevelTest(TestCase):
    def test_init(self):
        VisibilityLevelForm()


class GroupFormTests(LoginMethods):
    valid_form_data = {
        'name': "Group_name",
        'path': "Group_path",
        'description': "Description",
        'visibility': GroupForm.PRIVATE,
    }

    def test_init(self):
        GroupForm()

    def test_valid_data(self):
        form = GroupForm(self.valid_form_data)
        self.assertTrue(form.is_valid())
        for key, value in self.valid_form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = GroupForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])
        self.assertEqual(form.errors['path'], ['This field is required.'])

    def test_save_in_gitlab_not_valid(self):
        form = GroupForm({})
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(1, 1)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = GroupForm(self.valid_form_data)
        form.save_in_gitlab(self.user.id, 1)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url(raise_error=GitlabCreateError('{"path": ["has already been taken"]}'))
    def test_save_in_gitlab_error(self):
        form = GroupForm(self.valid_form_data)
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(self.user.id, 1)
        all_errors = form.errors
        self.assertIn('has already been taken', all_errors['path'][-1])


class GroupMemberFormTests(LoginMethods):
    valid_form_data = {
        'username': "username",
        'access_level': models.AddGroupMemberTask.ACCESS_GUEST,
    }

    def test_init(self):
        GroupMemberForm()

    def test_valid_data(self):
        form = GroupMemberForm(self.valid_form_data)
        self.assertTrue(form.is_valid())
        for key, value in self.valid_form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = GroupMemberForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

    def test_save_in_gitlab_not_valid(self):
        form = GroupMemberForm({})
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(1, 1)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = GroupMemberForm(self.valid_form_data)
        form.save_in_gitlab(self.user.id, 1)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url(raise_error=GitlabCreateError('{"username": ["Does not exist"]}'))
    def test_save_in_gitlab_error(self):
        form = GroupMemberForm(self.valid_form_data)
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(self.user.id, 1)
        all_errors = form.errors
        self.assertIn('Does not exist', all_errors['username'][-1])
