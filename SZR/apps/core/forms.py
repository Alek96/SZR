from GitLabApi.exceptions import NON_FIELD_ERRORS, GitlabOperationError
from core import models
from core.exceptions import FormError, FormNotValidError
from django import forms
from django.contrib.admin import widgets


class BaseForm(forms.ModelForm):
    _readonly_fields = []

    class Meta:
        model = models.AbstractStatus
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self._readonly_fields:
            self.fields[field].disabled = True

        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            if instance.is_finished():
                for name, field in self.fields.items():
                    field.disabled = True
        else:
            for field in self._readonly_fields:
                self.fields[field].widget = forms.HiddenInput()

    def add_error_dict(self, error_dict):
        for field, err_msg in error_dict.items():
            if isinstance(err_msg, list):
                for err in err_msg:
                    self._add_error(field, "{0}: {1}".format(field.capitalize(), err))
            else:
                self._add_error(field, "{0}: {1}".format(field.capitalize(), err_msg))

    def _add_error(self, field, msg):
        if field == NON_FIELD_ERRORS:
            self.add_error(None, msg)
        else:
            self.add_error(field, msg)

    def save(self, **kwargs):
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            raise FormError(error_msg='Cannot save existing model. Use update method instance.')

        if not self.is_valid():
            raise FormNotValidError(self.errors.as_data())

        model = super().save(commit=False)
        self._pre_save(model=model, **kwargs)
        model.save()
        self._post_save(model=model, **kwargs)
        return model

    def _pre_save(self, **kwargs):
        """
        Here Children class can set special attributes to creating model

        :param task: task that is being created
        :param kwargs: special parameters
        :return: None
        """

    def _post_save(self, **kwargs):
        """
        Here Children class can set special action to creating model

        :param task: task that is being created
        :param kwargs: special parameters
        :return: None
        """

    def update(self, **kwargs):
        instance = getattr(self, 'instance', None)
        if not instance or not instance.id:
            raise FormError(error_msg='Cannot update not existing model. Use save method instance.')

        if not self.is_valid():
            raise FormNotValidError(self.errors.as_data())

        model = super().save(commit=False)
        self._update(model=model, **kwargs)
        model.save()
        return model

    def _update(self, **kwargs):
        """
        Here Children class can set special attributes to updating model

        :param task: task that is being created
        :param kwargs: special parameters
        :return: None
        """


class BaseTaskGroupForm(BaseForm):
    _readonly_fields = ['status', 'finished_date', 'tasks_number', 'finished_tasks_number']

    status = forms.CharField(max_length=20, disabled=True, required=False)
    tasks_number = forms.IntegerField(disabled=True, required=False)
    finished_tasks_number = forms.IntegerField(disabled=True, required=False)

    class Meta:
        model = models.AbstractTaskGroup
        fields = ['name', 'execute_date', 'finished_date']
        widgets = {
            'execute_date': widgets.AdminSplitDateTime,
        }
        field_classes = {
            'execute_date': forms.SplitDateTimeField,
        }

    fields_order = ['name', 'execute_date',
                    'finished_date', 'status', 'tasks_number', 'finished_tasks_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['status'].initial = instance.status
            self.fields['tasks_number'].initial = instance.tasks_number
            self.fields['finished_tasks_number'].initial = instance.finished_tasks_number


class BaseTaskForm(BaseForm):
    _readonly_fields = ['status', 'error_msg', 'finished_date']

    class Meta:
        model = models.AbstractTask
        fields = ['status', 'error_msg', 'execute_date', 'finished_date']
        widgets = {
            'execute_date': widgets.AdminSplitDateTime,
        }
        field_classes = {
            'execute_date': forms.SplitDateTimeField,
        }

    def save_in_gitlab(self, user_id, **kwargs):
        if not self.is_valid():
            raise FormNotValidError(self.errors.as_data())

        data = dict(self.cleaned_data)
        try:
            self._save_in_gitlab(data=data, user_id=user_id, **kwargs)
        except GitlabOperationError as error:
            self.add_error_dict(error.get_error_dict())
            raise FormNotValidError(self.errors.as_data())

    def _save_in_gitlab(self, **kwargs):
        """
        Here Children class run function that will save in form GitLab

        :param data: Data extracted from forms
        :param user_id: User id that make request
        :param kwargs: special parameters
        :return: None
        """

    def _pre_save(self, model, user_id, task_group=None, **kwargs):
        model.owner = models.GitlabUser.objects.get(user_id=user_id)
        model.task_group = task_group
