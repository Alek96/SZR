from django import forms
from django.contrib.admin import widgets
from django.utils.translation import ugettext as _

from GitLabApi import *
from GitLabApi.exceptions import *
from core.exceptions import WrongFormError
from groups import models
from core.models import GitlabUser


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
            # 'execute_date': forms.SplitDateTimeWidget,
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
        if self.is_valid():
            data = dict(self.cleaned_data)
            try:
                gitlab_api = GitLabApi(user_id)
                new_user_id = gitlab_api.users.get(username=data['username']).id
                gitlab_api.groups.get(group_id).members.create({
                    'user_id': new_user_id,
                    'access_level': data['access_level']
                })
                return
            except GitlabOperationError as error:
                self.add_error_dict(error.get_error_dict())
        raise WrongFormError(self.errors.as_data())

    def save_in_task(self, user_id, task_group_id):
        if self.is_valid():
            task = self.save(commit=False)
            task.owner = GitlabUser.objects.get(auth_user_id=user_id)
            task.task_group = models.AddGroupMemberTaskGroup.objects.get(id=task_group_id)
            task.save()
        else:
            raise WrongFormError(self.errors.as_data())
