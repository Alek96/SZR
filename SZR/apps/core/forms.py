from django import forms
from django.contrib.admin import widgets
from django.utils.translation import ugettext as _

from GitLabApi.exceptions import *
from core.exceptions import WrongFormError
from core import models


class FormMethods(forms.Form):
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


class BaseTaskForm(FormMethods, forms.ModelForm):
    def save_in_gitlab(self, user_id, **kwargs):
        if not self.is_valid():
            raise WrongFormError(self.errors.as_data())

        data = dict(self.cleaned_data)
        try:
            self._save_in_gitlab(data=data, user_id=user_id, **kwargs)
        except GitlabOperationError as error:
            self.add_error_dict(error.get_error_dict())
            raise WrongFormError(self.errors.as_data())

    def _save_in_gitlab(self, **kwargs):
        """
        Here Children class run function that will save in form GitLab

        :param data: Data extracted from forms
        :param user_id: User id that make request
        :param kwargs: special parameters
        :return: None
        """

    def save_in_db(self, user_id, task_group_id, **kwargs):
        if not self.is_valid():
            raise WrongFormError(self.errors.as_data())

        task = self.save(commit=False)
        task.owner = models.GitlabUser.objects.get(user_id=user_id)
        task.task_group = task._task_group_model.objects.get(id=task_group_id)
        self._save_in_db(task=task, **kwargs)
        task.save()

    def _save_in_db(self, **kwargs):
        """
        Here Children class can set special attributes to creating model

        :param task: task that is being created
        :param kwargs: special parameters
        :return: None
        """


class BaseTaskGroupForm(FormMethods, forms.ModelForm):
    class Meta:
        model = models.AbstractTaskGroup
        fields = ['name', 'execute_date']
        widgets = {
            'execute_date': widgets.AdminSplitDateTime,
        }
        field_classes = {
            'execute_date': forms.SplitDateTimeField,
        }

    def save_in_db(self, **kwargs):
        if not self.is_valid():
            raise WrongFormError(self.errors.as_data())

        task_group = self.save(commit=False)
        self._save_in_db(task_group=task_group, **kwargs)
        task_group.save()

    def _save_in_db(self, **kwargs):
        """
        Here Children class can set special attributes to creating model

        :param task: task that is being created
        :param kwargs: special parameters
        :return: None
        """
