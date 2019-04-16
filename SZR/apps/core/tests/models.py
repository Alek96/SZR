from core import models


class FakeBaseModel(models.BaseModel):
    pass


class FakeAccessLevel(models.AbstractAccessLevel):
    pass


class FakeVisibilityLevel(models.AbstractVisibilityLevel):
    pass


class FakeTaskDates(models.AbstractTaskDates):
    pass


class FakeStatus(models.AbstractStatus):
    pass


class FakeTaskGroup(models.AbstractTaskGroup):
    _parent_task_model = 'FakeTask'


class FakeRaiseTask(models.AbstractTask):
    _parent_task_model = 'FakeRaiseTask'
    _task_group_model = FakeTaskGroup


class FakeTask(models.AbstractTask):
    _parent_task_model = 'FakeTask'
    _task_group_model = FakeTaskGroup

    def _get_task_path(self):
        return 'core.tests.tasks.FakeTask'
