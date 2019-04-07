from groups.models import AbstractTaskGroup, AbstractAddSubgroup


class FakeTaskGroup(AbstractTaskGroup):
    _parent_task_model = 'FakeAddSubgroup'


class FakeAddSubgroup(AbstractAddSubgroup):
    _task_group_model = FakeTaskGroup

    def _get_task_path(self):
        return 'groups.tests.tasks.FakeTask'
