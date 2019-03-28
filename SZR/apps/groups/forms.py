from django import forms
from django.contrib.admin import widgets
from django.utils.translation import ugettext as _

from GitLabApi import *
from GitLabApi.exceptions import *
from core.exceptions import WrongFormError
from groups import models
from core.models import GitlabUser
from groups import tasks


class FormMethods(forms.Form):
    def _add_error(self, field, msg):
        if field == NON_FIELD_ERRORS:
            self.add_error(None, msg)
        else:
            self.add_error(field, msg)

    def add_error_dict(self, error_dict):
        for field, err_msg in error_dict.items():
            if isinstance(err_msg, list):
                for err in err_msg:
                    self._add_error(field, "{0}: {1}".format(field.capitalize(), err))
            else:
                self._add_error(field, "{0}: {1}".format(field.capitalize(), err_msg))


class VisibilityLevelForm(FormMethods):
    PRIVATE = 'private'
    Internal = 'internal'
    PUBLIC = 'public'
    VISIBILITY_CHOICES = (
        (PRIVATE, 'Private'),
        (Internal, 'Internal'),
        (PUBLIC, 'Public'),
    )

    visibility = forms.ChoiceField(label="Visibility", choices=VISIBILITY_CHOICES, initial=PRIVATE,
                                   widget=forms.Select())


class GroupForm(VisibilityLevelForm):
    name = forms.CharField(label='Name', max_length=50)
    path = forms.SlugField(label='Path', max_length=50)
    description = forms.CharField(label='Description', max_length=2000, required=False, widget=forms.Textarea)

    field_order = ['name', 'path', 'description', 'visibility']

    def save_in_gitlab(self, user_id, group_id=None):
        if self.is_valid():
            data = dict(self.cleaned_data)
            data['parent_id'] = group_id
            try:
                GitLabApi(user_id).groups.create(data)
                return
            except GitlabCreateError as error:
                self.add_error_dict(error.get_error_dict())
        raise WrongFormError(self.errors.as_data())


class GroupMemberGroupForm(forms.ModelForm, FormMethods):
    class Meta:
        model = models.AddGroupMemberTaskGroup
        fields = ['name', 'execute_date']
        widgets = {
            'execute_date': widgets.AdminSplitDateTime,
        }
        field_classes = {
            'execute_date': forms.SplitDateTimeField,
        }

    def save_in_task_group(self, group_id):
        if self.is_valid():
            task_group = self.save(commit=False)
            task_group.gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)
            task_group.save()
        else:
            raise WrongFormError(self.errors.as_data())


class GroupMemberForm(forms.ModelForm, FormMethods):
    class Meta:
        model = models.AddGroupMemberTask
        fields = ['username', 'access_level']

    def save_in_gitlab(self, user_id, group_id):
        if not self.is_valid():
            raise WrongFormError(self.errors.as_data())

        data = dict(self.cleaned_data)
        try:
            tasks.add_or_update_group_member(user_id=user_id, group_id=group_id, **data)
        except GitlabOperationError as error:
            self.add_error_dict(error.get_error_dict())
            raise WrongFormError(self.errors.as_data())

    def save_in_task(self, user_id, task_group_id):
        if self.is_valid():
            task = self.save(commit=False)
            task.owner = GitlabUser.objects.get(user_id=user_id)
            task.task_group = models.AddGroupMemberTaskGroup.objects.get(id=task_group_id)
            task.save()
        else:
            raise WrongFormError(self.errors.as_data())
