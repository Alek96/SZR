from core.models import *


class FakeTaskStatus(AbstractTaskStatus):
    pass


class FakeTaskGroup(AbstractTaskGroup):
    _parent_task = 'FakeTask'

    def create_task(self, **kwargs):
        return self.tasks_set.create(
            owner=GitlabUser.objects.create(),
            **kwargs
        )


class FakeTask(AbstractTask):
    _task_group_model = FakeTaskGroup

    def _get_task_path(self):
        return 'core.tests.tasks.FakeTask'


class FakeRaiseTaskGroup(AbstractTaskGroup):
    _parent_task = 'FakeRaiseTask'


class FakeRaiseTask(AbstractTask):
    _task_group_model = FakeRaiseTaskGroup
