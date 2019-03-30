from django.test import TestCase
from django import forms
from django.utils import timezone
from django.core.exceptions import NON_FIELD_ERRORS as django_NON_FIELD_ERRORS

from core.tests.forms import *
from GitLabApi.exceptions import NON_FIELD_ERRORS as GitLabApi_NON_FIELD_ERRORS


class FormMethodsTest(TestCase):
    def test_add_error_dict(self):
        dict = {
            'name': 'error 1',
            GitLabApi_NON_FIELD_ERRORS: 'error 2',
        }
        form = FakeFormMethods({})
        form.add_error_dict(dict)
        all_errors = form.errors.as_data()

        self.assertIn(dict['name'], str(all_errors['name'][-1]))
        self.assertIn(dict[GitLabApi_NON_FIELD_ERRORS], str(all_errors[django_NON_FIELD_ERRORS][-1]))

    def test_add_error_dict_list(self):
        dict = {
            'name': ['error 1.1', 'error 1.2'],
            GitLabApi_NON_FIELD_ERRORS: ['error 2.1', 'error 2.2'],
        }
        form = FakeFormMethods({})
        form.add_error_dict(dict)
        all_errors = form.errors.as_data()

        self.assertIn(dict['name'][0], str(all_errors['name'][-2]))
        self.assertIn(dict['name'][1], str(all_errors['name'][-1]))
        self.assertIn(dict[GitLabApi_NON_FIELD_ERRORS][0], str(all_errors[django_NON_FIELD_ERRORS][-2]))
        self.assertIn(dict[GitLabApi_NON_FIELD_ERRORS][1], str(all_errors[django_NON_FIELD_ERRORS][-1]))


class BaseTaskFormTest(TestCase):
    pass


class BaseTaskGroupFormTest(TestCase):
    pass
