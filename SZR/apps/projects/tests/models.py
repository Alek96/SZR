from core import models as core_models
from core.tests import models as core_test_models
from groups.models import GitlabGroup
from groups.tests.models import AbstractTaskCreateMethods as groups_AbstractTaskCreateMethods
from projects import models


class AddProjectCreateMethods(groups_AbstractTaskCreateMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_group=None, name='name', path='path',
                    **kwargs):
        return models.AddProject.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_group=gitlab_group or (None if (task_group or parent_task) else GitlabGroup.objects.create()),
            parent_task=parent_task,
            name=name,
            path=path,
            **kwargs
        )


class FakeTask(models.AbstractTask):
    def _get_task_path(self):
        return 'projects.tests.tasks.FakeTask'


class TaskGroupMethods(core_test_models.TaskGroupCreateMethods):
    def create_task_group(self, name='Name', gitlab_project=None, parent_task=None, **kwargs):
        return models.TaskGroup.objects.create(
            name=name,
            gitlab_project=gitlab_project or (None if parent_task else models.GitlabProject.objects.create()),
            parent_task=parent_task,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return AddProjectCreateMethods().create_task(**kwargs)


class AbstractTaskCreateMethods(TaskGroupMethods, core_test_models.TaskCreateMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_project=None, **kwargs):
        return FakeTask.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_project=gitlab_project or (
                None if (task_group or parent_task) else models.GitlabProject.objects.create()),
            parent_task=parent_task,
            **kwargs
        )


class AddMemberCreateMethods(AbstractTaskCreateMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_project=None, username='username',
                    **kwargs):
        return models.AddMember.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_project=gitlab_project or (
                None if (task_group or parent_task) else models.GitlabProject.objects.create()),
            parent_task=parent_task,
            username=username,
            **kwargs
        )
