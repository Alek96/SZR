from core.forms import BaseForm, BaseTaskGroupForm, BaseTaskForm
from core.tests.test_models import *
from django import forms


class FakeBaseForm(BaseForm):
    _readonly_fields = ['status']

    class Meta:
        model = FakeTaskStatus
        fields = ['status']

    name = forms.CharField(label='Name', max_length=50, initial='name')


class FakeTaskGroupForm(BaseTaskGroupForm):
    class Meta(BaseTaskGroupForm.Meta):
        model = FakeTaskGroup


class FakeTaskForm(BaseTaskForm):
    class Meta(BaseTaskForm.Meta):
        model = FakeTask

    name = forms.CharField(label='Name', max_length=50, initial='name')
