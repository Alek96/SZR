from unittest import mock

from GitLabApi.exceptions import GitlabCreateError
from GitLabApi.exceptions import NON_FIELD_ERRORS as GitLabApi_NON_FIELD_ERRORS
from core.exceptions import FormError, FormNotValidError
from core.tests import forms as test_forms
from core.tests import models as test_models
from core.tests.test_view import LoginMethods
from django.core.exceptions import NON_FIELD_ERRORS as django_NON_FIELD_ERRORS
from django.forms import HiddenInput


class BaseFormTest(LoginMethods):
    form_class = test_forms.FakeBaseForm
    model_class = test_models.FakeStatus
    model_methods = None
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = ['name']
    readonly_fields = ['status']

    # def setUpClass(self):
    #     super().setUpClass()
    #     self.assertEqual(self.model_class, self.form_class.Meta.model)
    #     self.assertEqual(self.readonly_fields, self.form_class._readonly_fields)

    def create_model(self, **kwargs):
        return self.model_class.objects.create(**kwargs)

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

    def test_readonly_fields_are_disabled(self):
        def test(instance=None):
            form = self.form_class(self.valid_form_data, instance=instance)
            for field_name in self.readonly_fields:
                self.assertTrue(form.fields[field_name].disabled)

        test()
        test(self.create_model())

    def test_readonly_fields_are_hidden_for_new_model(self):
        form = self.form_class(self.valid_form_data)
        for field_name in self.readonly_fields:
            self.assertIsInstance(form.fields[field_name].widget, HiddenInput)

        self.assertEqual(self.form_class._readonly_fields, self.readonly_fields)

    def test_if_status_is_finished_disable_all_fields(self):
        model = self.create_model(status=self.model_class.SUCCEED)
        form = self.form_class(self.valid_form_data, instance=model)

        for name, field in form.fields.items():
            self.assertTrue(form.fields[name].disabled, 'Field - {0}'.format(name))

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
        model = self.create_model()
        form = self.form_class(self.valid_form_data, instance=model)
        with self.assertRaises(FormError) as err:
            form.save()
        self.assertIn('Cannot save', str(err.exception))

    def test_update(self):
        model = self.create_model()
        form = self.form_class(self.valid_form_data, instance=model)
        with mock.patch.object(form, '_update') as mock_save:
            new_model = form.update()
        mock_save.assert_called_once_with(model=new_model)
        self.assertIsInstance(new_model, self.model_class)
        self.assertEqual(model.id, new_model.id)

    def test_update_raise_FormNotValidError_if_not_valid(self):
        model = self.create_model()
        form = self.form_class(instance=model)
        with self.assertRaises(FormNotValidError):
            form.update()

    def test_save_raise_FormError_if_try_saving_not_existing_model(self):
        form = self.form_class(self.valid_form_data)
        with self.assertRaises(FormError) as err:
            form.update()
        self.assertIn('Cannot update', str(err.exception))

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


class BaseTaskGroupFormTest(BaseFormTest):
    form_class = test_forms.FakeTaskGroupForm
    model_class = test_models.FakeTaskGroup
    model_methods = test_models.TaskCreateMethods()
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = ['name']
    readonly_fields = ['finished_date']

    def create_model(self, status=None, **kwargs):
        task_group = self.model_methods.create_task_group(**kwargs)

        if status == self.model_class.SUCCEED:
            self.model_methods.create_task(task_group=task_group, status=status)

        return task_group

    def test_field_status_is_hidden_for_new_model(self):
        form = self.form_class(self.valid_form_data)
        self.assertIsInstance(form.fields['status'].widget, HiddenInput)

    def test_field_tasks_number_is_hidden_for_new_model(self):
        form = self.form_class(self.valid_form_data)
        self.assertIsInstance(form.fields['tasks_number'].widget, HiddenInput)

    def test_field_finished_tasks_number_is_hidden_for_new_model(self):
        form = self.form_class(self.valid_form_data)
        self.assertIsInstance(form.fields['finished_tasks_number'].widget, HiddenInput)

    def test_field_status_has_initial_value_copied_from_model(self):
        model = self.create_model()
        form = self.form_class(self.valid_form_data, instance=model)
        self.assertEqual(form.fields['status'].initial, model.status)

    def test_field_tasks_number_has_initial_value_copied_from_model(self):
        model = self.create_model()
        form = self.form_class(self.valid_form_data, instance=model)
        self.assertEqual(form.fields['tasks_number'].initial, model.tasks_number)

    def test_field_finished_tasks_number_has_initial_value_copied_from_model(self):
        model = self.create_model()
        form = self.form_class(self.valid_form_data, instance=model)
        self.assertEqual(form.fields['finished_tasks_number'].initial, model.finished_tasks_number)


class BaseTaskFormTest(BaseFormTest):
    form_class = test_forms.FakeTaskForm
    model_class = test_models.FakeTask
    model_methods = test_models.TaskCreateMethods()
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = []
    readonly_fields = ['status', 'error_msg', 'execute_date', 'finished_date']

    def create_model(self, **kwargs):
        return self.model_methods.create_task(**kwargs)

    @LoginMethods.create_user_wrapper
    def test_save(self):
        form = self.form_class(self.valid_form_data)
        task = form.save(user_id=self.user.id)
        self.assertIsInstance(task, self.model_class)

    @LoginMethods.create_user_wrapper
    def test_save_with_task_group(self):
        task_group = self.model_methods.create_task_group()
        form = self.form_class(self.valid_form_data)
        task = form.save(user_id=self.user.id, task_group=task_group)

        self.assertIsInstance(task, self.model_class)
        self.assertTrue(task.id)
        self.assertEqual(task.task_group.id, task_group.id)
        self.assertEqual(task.owner_id, self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_in_gitlab(self):
        form = self.form_class(self.valid_form_data)
        with mock.patch.object(form, '_save_in_gitlab') as mock_save:
            form.save_in_gitlab(user_id=self.user.id)
        mock_save.assert_called_once_with(
            data=dict(form.cleaned_data),
            user_id=self.user.id
        )

    @LoginMethods.create_user_wrapper
    def test_save_in_gitlab_raise_FormNotValidError_if_not_valid(self):
        form = self.form_class({})
        with self.assertRaises(FormNotValidError):
            form.save_in_gitlab(user_id=self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_in_gitlab_raise_FormNotValidError_if_error_while_saving(self):
        error_msg = '{"' + str(next(iter(self.valid_form_data.keys()))) + '": ["has already been taken"]}'
        form = self.form_class(self.valid_form_data)
        with mock.patch.object(form, '_save_in_gitlab',
                               side_effect=GitlabCreateError(error_msg)):
            with self.assertRaises(FormNotValidError):
                form.save_in_gitlab(user_id=self.user.id)
