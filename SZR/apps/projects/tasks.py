from GitLabApi import GitLabApi
from GitLabApi.exceptions import GitlabGetError
from core.exceptions import DoesNotContainGitlabId
from core.models import GitlabUser
from core.tasks import BaseTask as core_BaseTask
from groups.tasks import BaseTask as groups_BaseTask

from SZR.celery import app as celery_app
from . import models


def create_project(user_id, name, path, group_id=None, **kwargs):
    new_project = GitLabApi(user_id).projects.create({
        'name': name,
        'path': path,
        'namespace_id': group_id,
        **kwargs
    })

    return new_project.id


def add_or_update_member(user_id, project_id, username, access_level, **kwargs):
    gitlab_api = GitLabApi(user_id)
    new_user_id = gitlab_api.users.get(username=username).id

    try:
        user = gitlab_api.projects.get(project_id).members.get(new_user_id)
        user.access_level = access_level
        user.save()
    except GitlabGetError:
        gitlab_api.projects.get(project_id).members.create({
            'user_id': new_user_id,
            'access_level': access_level,
            **kwargs
        })

    return new_user_id


class AddProjectTask(groups_BaseTask):
    _task_model = models.AddProject

    def _run(self, **kwargs):
        super()._run(**kwargs)

        new_project_id = create_project(
            user_id=self._task.owner.user_id,
            group_id=self._task.gitlab_group.gitlab_id,
            name=self._task.name,
            path=self._task.path,
            description=self._task.description,
            visibility=self._task.visibility,
        )
        self._task.new_gitlab_project.gitlab_id = new_project_id

    def _finnish(self):
        super()._finnish()
        self._task.new_gitlab_project.save()


celery_app.register_task(AddProjectTask())


class BaseTask(core_BaseTask):
    def _run(self, **kwargs):
        if not self._task.gitlab_project.gitlab_id:
            raise DoesNotContainGitlabId('Gitlab project {0}'.format(self._task.gitlab_project_id))


class AddMemberTask(BaseTask):
    _task_model = models.AddMember

    def _run(self, **kwargs):
        super()._run(**kwargs)

        new_user_id = add_or_update_member(
            user_id=self._task.owner.user_id,
            project_id=self._task.gitlab_project.gitlab_id,
            username=self._task.username,
            access_level=self._task.access_level
        )
        self._task.new_gitlab_user, _ = GitlabUser.objects.get_or_create(gitlab_id=new_user_id)


celery_app.register_task(AddMemberTask())
