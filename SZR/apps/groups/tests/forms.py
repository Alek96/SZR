from django import forms
from groups.forms import BaseTaskForm
from groups.tests.models import FakeTask


class FakeTaskForm(BaseTaskForm):
    class Meta(BaseTaskForm.Meta):
        model = FakeTask

    name = forms.CharField(label='Name', max_length=50, initial='name')
