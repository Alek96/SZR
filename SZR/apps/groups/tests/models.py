from groups.models import *


class FakeParentTaskSubgroup(AbstractParentTaskAddSubgroup):
    _parent_task_model = 'FakeAddSubgroup'


class FakeAddSubgroup(AbstractAddSubgroup):
    _task_group_model = FakeParentTaskSubgroup

    def _get_task_path(self):
        return 'groups.tests.tasks.FakeTask'
