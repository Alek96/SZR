from __future__ import absolute_import, unicode_literals

from core.tasks import BaseTask
from SZR.celery import app as celery_app
from GitLabApi import *
from groups import models
from core.exceptions import DoesNotContainGitlabId


class AddGroupMemberTask(BaseTask):
    _task_model = models.AddGroupMemberTask

    def _run(self, **kwargs):
        gitlab_api = GitLabApi(self._task.owner.auth_user_id)
        new_user_id = gitlab_api.users.get(username=self._task.username).id
        new_gitlab_user, _ = models.GitlabUser.objects.get_or_create(gitlab_id=new_user_id)
        self._task.new_user = new_gitlab_user

        if not self._task.gitlab_group.gitlab_id:
            raise DoesNotContainGitlabId('Gitlab group {0}'.format(self._task.gitlab_group_id))

        gitlab_api.groups.get(self._task.gitlab_group.gitlab_id).members.create({
            'user_id': new_user_id,
            'access_level': self._task.access_level,
        })


celery_app.register_task(AddGroupMemberTask())
