from core.models import *


class FakeTaskStatus(AbstractTaskStatus):
    pass


class FakeTaskGroup(AbstractTaskGroup):
    pass


class FakeTask(AbstractTask):
    _task_group_model = FakeTaskGroup

    def _get_task_path(self):
        return 'core.tests.tasks.FakeTask'


class FakeRaiseTaskGroup(AbstractTaskGroup):
    pass


class FakeRaiseTask(AbstractTask):
    _task_group_model = FakeRaiseTaskGroup
