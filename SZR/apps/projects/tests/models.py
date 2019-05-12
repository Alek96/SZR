from core import models as core_models
from core.tests import models as core_test_models
from groups.tests.models import AddProjectCreateMethods
from projects import models


class FakeTask(models.AbstractTask):
    _parent_task_model = 'groups.AddProject'

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
