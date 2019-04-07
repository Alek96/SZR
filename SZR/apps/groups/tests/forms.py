from groups.forms import BaseTaskGroupForm
from groups.tests.models import FakeTaskGroup, FakeAddSubgroup


class FakeTaskGroupForm(BaseTaskGroupForm):
    _parent_task_model = FakeAddSubgroup

    class Meta(BaseTaskGroupForm.Meta):
        model = FakeTaskGroup
