from core.forms import *
from core.tests.test_models import *


class FakeFormMethods(FormMethods):
    name = forms.CharField(label='Name', max_length=50, initial='name')
    path = forms.SlugField(label='Path', max_length=50, initial='path')


class FakeTaskForm(BaseTaskForm):
    class Meta:
        model = FakeTask
        fields = ['error_msg']


class FakeTaskGroupForm(BaseTaskGroupForm):
    class Meta(BaseTaskGroupForm.Meta):
        model = FakeTaskGroup
