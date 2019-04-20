from core import models
from core.models import GitlabUser


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


class TaskGroupCreateMethods:
    def create_task_group(self, name='Name', **kwargs):
        return FakeTaskGroup.objects.create(
            name=name,
            **kwargs
        )


class TaskCreateMethods(TaskGroupCreateMethods):
    def create_task(self, owner=None, task_group=None, **kwargs):
        return FakeTask.objects.create(
            owner=owner or GitlabUser.objects.create(),
            task_group=task_group,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return self.create_task(**kwargs)
