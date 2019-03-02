from django import forms

from GitLabApi import *


class VisibilityLevelForm(forms.Form):
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

    def save_in_gitlab(self, user_id, group_id):
        if self.is_valid():
            data = dict(self.cleaned_data)
            data['parent_id'] = group_id
            GitLabApi(user_id).groups.create(data)

# class ProjectForm(forms.ModelForm):
#     class Meta:
#         model = Project
#         fields = ['name', 'path', 'description', 'visibility']
