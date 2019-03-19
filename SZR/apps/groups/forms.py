from django import forms

from GitLabApi import *
from GitLabApi.exceptions import *
from core.exceptions import WrongFormError
from groups import models


class FormMethods(forms.Form):
    def add_error_dict(self, error_dict):
        for field, err_msg in error_dict.items():
            if isinstance(err_msg, list):
                for err in err_msg:
                    self.add_error(field, "{0}: {1}".format(field.capitalize(), err))
            else:
                self.add_error(field, "{0}: {1}".format(field.capitalize(), err_msg))


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


class GroupMemberForm(forms.ModelForm, FormMethods):
    class Meta:
        model = models.AddGroupMemberTask
        fields = ['username', 'access_level']

    def save_in_gitlab(self, user_id, group_id=None):
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
