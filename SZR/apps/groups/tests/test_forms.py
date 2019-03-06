from django.test import TestCase

from groups.forms import *
from GitLabApi import mock_all_gitlab_url
from GitLabApi.exceptions import GitlabCreateError
from core.tests.test_view import LoginMethods


class AbstractVisibilityLevelTest(TestCase):
    def test_init(self):
        VisibilityLevelForm()


class GroupFormTestAttributes:
    valid_form_data = {
        'name': "Group_name",
        'path': "Group_path",
        'description': "Description",
        'visibility': "private",
    }


class GroupFormTests(GroupFormTestAttributes, LoginMethods):
    def test_init(self):
        GroupForm()

    def test_valid_data(self):
        form_data = self.valid_form_data
        form = GroupForm(form_data)
        self.assertTrue(form.is_valid())
        for key, value in form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = GroupForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])
        self.assertEqual(form.errors['path'], ['This field is required.'])

    def test_add_error_dict(self):
        dict = {
            'name': 'error 1',
            'path': 'error 2',
        }
        form = GroupForm(self.valid_form_data)
        form.add_error_dict(dict)
        all_errors = form.errors.as_data()

        for key, value in dict.items():
            self.assertIn(value, str(all_errors[key][-1]))

    def test_add_error_dict_list(self):
        dict = {
            'name': ['error 1.1', 'error 1.2'],
            'path': ['error 2.1', 'error 2.2'],
        }
        form = GroupForm(self.valid_form_data)
        form.add_error_dict(dict)
        all_errors = form.errors.as_data()

        for key, value in dict.items():
            self.assertIn(value[0], str(all_errors[key][-2]))
            self.assertIn(value[1], str(all_errors[key][-1]))

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
    @mock_all_gitlab_url(raise_error=get_gitlab_create_error_on_group())
    def test_save_in_gitlab_error(self):
        form = GroupForm(self.valid_form_data)
        with self.assertRaises(WrongFormError):
            form.save_in_gitlab(self.user.id, 1)
        all_errors = form.errors
        self.assertIn('has already been taken', all_errors['path'][-1])
