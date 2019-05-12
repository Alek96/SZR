from GitLabApi import GitLabApi
from GitLabApi.exceptions import GitlabGetError
from core.exceptions import DoesNotContainGitlabId
from core.models import GitlabUser
from core.tasks import BaseTask as core_BaseTask

from SZR.celery import app as celery_app
from . import models


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
