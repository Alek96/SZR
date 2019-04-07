from unittest import mock

from GitLabApi.exceptions import GitlabCreateError
from GitLabApi.exceptions import NON_FIELD_ERRORS as GitLabApi_NON_FIELD_ERRORS
from core.exceptions import FormError, FormNotValidError
from core.tests.forms import FakeBaseForm, FakeTaskForm
from core.tests.models import FakeTaskStatus
from core.tests.test_view import LoginMethods
from django.core.exceptions import NON_FIELD_ERRORS as django_NON_FIELD_ERRORS
from django.test import TestCase


class BaseFormTest(LoginMethods):
    form_class = FakeBaseForm
    model_class = FakeTaskStatus
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = ['name']
    readonly_fields = ['status']

    def test_init(self):
        self.form_class()

    def test_valid_data(self):
        form = self.form_class(self.valid_form_data)
        self.assertTrue(form.is_valid())
        for key, value in self.valid_form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = self.form_class({})
        self.assertFalse(form.is_valid())
        for field in self.mandatory_fields:
            self.assertEqual(form.errors[field], ['This field is required.'])

    def test_save(self):
        form = self.form_class(self.valid_form_data)
        with mock.patch.object(form, '_save') as mock_save:
            model = form.save()
        mock_save.assert_called_once_with(model=model)
        self.assertIsInstance(model, self.model_class)

    def test_save_raise_FormNotValidError_if_not_valid(self):
        form = self.form_class()
        with self.assertRaises(FormNotValidError):
            form.save()

    def test_save_raise_FormError_if_try_saving_existing_model(self):
        model = self.model_class.objects.create()
        form = self.form_class(self.valid_form_data, instance=model)
        with self.assertRaises(FormError) as err:
            form.save()
        self.assertIn('Cannot save', str(err.exception))

    def test_update(self):
        model = self.model_class.objects.create()
        form = self.form_class(self.valid_form_data, instance=model)
        with mock.patch.object(form, '_update') as mock_save:
            new_model = form.update()
        mock_save.assert_called_once_with(model=new_model)
        self.assertIsInstance(new_model, self.model_class)
        self.assertEqual(model.id, new_model.id)

    def test_update_raise_FormNotValidError_if_not_valid(self):
        model = self.model_class.objects.create()
        form = self.form_class(instance=model)
        with self.assertRaises(FormNotValidError):
            form.update()

    def test_save_raise_FormError_if_try_saving_not_existing_model(self):
        form = self.form_class(self.valid_form_data)
        with self.assertRaises(FormError) as err:
            form.update()
        self.assertIn('Cannot update', str(err.exception))

    def test_readonly_fields(self):
        self.assertEqual(self.form_class._readonly_fields, self.readonly_fields)

        model = self.model_class.objects.create()
        form = self.form_class(self.valid_form_data, instance=model)

        for field_name in self.readonly_fields:
            self.assertEqual(form.fields[field_name].disabled, True)

    def test_if_status_is_finished_disable_all_fields(self):
        model = self.model_class.objects.create(status=self.model_class.SUCCEED)
        form = self.form_class(self.valid_form_data, instance=model)

        for field_name in self.form_class.Meta.fields:
            self.assertEqual(form.fields[field_name].disabled, True)

    def test_add_error_dict(self):
        dict_field = next(iter(self.valid_form_data.keys()))
        dict = {
            dict_field: 'error 1',
            GitLabApi_NON_FIELD_ERRORS: 'error 2',
        }
        form = self.form_class({})
        form.add_error_dict(dict)
        all_errors = form.errors.as_data()

        self.assertIn(dict[dict_field], str(all_errors[dict_field][-1]))
        self.assertIn(dict[GitLabApi_NON_FIELD_ERRORS], str(all_errors[django_NON_FIELD_ERRORS][-1]))

    def test_add_error_dict_list(self):
        dict_field = next(iter(self.valid_form_data.keys()))
        dict = {
            dict_field: ['error 1.1', 'error 1.2'],
            GitLabApi_NON_FIELD_ERRORS: ['error 2.1', 'error 2.2'],
        }
        form = self.form_class({})
        form.add_error_dict(dict)
        all_errors = form.errors.as_data()

        self.assertIn(dict[dict_field][0], str(all_errors[dict_field][-2]))
        self.assertIn(dict[dict_field][1], str(all_errors[dict_field][-1]))
        self.assertIn(dict[GitLabApi_NON_FIELD_ERRORS][0], str(all_errors[django_NON_FIELD_ERRORS][-2]))
        self.assertIn(dict[GitLabApi_NON_FIELD_ERRORS][1], str(all_errors[django_NON_FIELD_ERRORS][-1]))


class BaseTaskGroupFormTest(TestCase):
    pass


class BaseTaskFormTest(LoginMethods):
    valid_form_data = {
        'name': "My Name",
    }

    @LoginMethods.create_user_wrapper
    def test_save_in_gitlab(self):
        form = FakeTaskForm(self.valid_form_data)
        with mock.patch.object(form, '_save_in_gitlab') as mock_save:
            form.save_in_gitlab(user_id=self.user.id)
        mock_save.assert_called_once_with(
            data=dict(form.cleaned_data),
            user_id=self.user.id
        )

    @LoginMethods.create_user_wrapper
    def test_save_in_gitlab_raise_FormNotValidError_if_not_valid(self):
        form = FakeTaskForm({})
        with self.assertRaises(FormNotValidError):
            form.save_in_gitlab(user_id=self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_in_gitlab_raise_FormNotValidError_if_error_while_saving(self):
        form = FakeTaskForm(self.valid_form_data)
        with mock.patch.object(form, '_save_in_gitlab',
                               side_effect=GitlabCreateError('{"name": ["has already been taken"]}')):
            with self.assertRaises(FormNotValidError):
                form.save_in_gitlab(user_id=self.user.id)
        all_errors = form.errors
        self.assertIn('has already been taken', all_errors['name'][-1])
