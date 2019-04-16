from core.forms import BaseForm, BaseTaskGroupForm, BaseTaskForm
from core.tests import models as test_models
from django import forms


class FakeBaseForm(BaseForm):
    _readonly_fields = ['status']

    class Meta:
        model = test_models.FakeStatus
        fields = ['status']

    name = forms.CharField(label='Name', max_length=50, initial='name')


class FakeTaskGroupForm(BaseTaskGroupForm):
    class Meta(BaseTaskGroupForm.Meta):
        model = test_models.FakeTaskGroup


class FakeTaskForm(BaseTaskForm):
    class Meta(BaseTaskForm.Meta):
        model = test_models.FakeTask

    name = forms.CharField(label='Name', max_length=50, initial='name')
