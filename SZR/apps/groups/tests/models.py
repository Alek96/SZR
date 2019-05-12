from core import models as core_models
from core.tests import models as core_test_models
from groups import models
from groups.models import AbstractTask


class FakeTask(AbstractTask):
    _parent_task_model = 'groups.AddSubgroup'

    def _get_task_path(self):
        return 'groups.tests.tasks.FakeTask'


class TaskGroupMethods(core_test_models.TaskGroupCreateMethods):
    def create_task_group(self, name='Name', gitlab_group=None, parent_task=None, **kwargs):
        return models.TaskGroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or (None if parent_task else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return AddSubgroupCreateMethods().create_task(**kwargs)


class AbstractTaskCreateMethods(TaskGroupMethods, core_test_models.TaskCreateMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_group=None, **kwargs):
        return FakeTask.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_group=gitlab_group or (None if (task_group or parent_task) else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )


class AddSubgroupCreateMethods(TaskGroupMethods, core_test_models.TaskCreateMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_group=None, name='name', path='path',
                    **kwargs):
        return models.AddSubgroup.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_group=gitlab_group or (None if (task_group or parent_task) else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            name=name,
            path=path,
            **kwargs
        )


class AddProjectCreateMethods(AbstractTaskCreateMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_group=None, name='name', path='path',
                    **kwargs):
        return models.AddProject.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_group=gitlab_group or (None if (task_group or parent_task) else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            name=name,
            path=path,
            **kwargs
        )


class AddMemberCreateMethods(AbstractTaskCreateMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_group=None, username='username',
                    **kwargs):
        return models.AddMember.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_group=gitlab_group or (None if (task_group or parent_task) else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            username=username,
            **kwargs
        )
