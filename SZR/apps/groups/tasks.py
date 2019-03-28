from __future__ import absolute_import, unicode_literals

from core.tasks import BaseTask
from SZR.celery import app as celery_app
from GitLabApi import GitLabApi
from GitLabApi.exceptions import *
from groups import models
from core.exceptions import DoesNotContainGitlabId


def add_or_update_group_member(user_id, group_id, username, access_level, **kwargs):
    gitlab_api = GitLabApi(user_id)
    new_user_id = gitlab_api.users.get(username=username).id

    try:
        user = gitlab_api.groups.get(group_id).members.get(new_user_id)
        user.access_level = access_level
        user.save()
    except GitlabGetError:
        gitlab_api.groups.get(group_id).members.create({
            'user_id': new_user_id,
            'access_level': access_level,
            **kwargs
        })

    return new_user_id


class AddGroupMemberTask(BaseTask):
    _task_model = models.AddGroupMemberTask

    def _run(self, **kwargs):
        if not self._task.task_group.gitlab_group.gitlab_id:
            raise DoesNotContainGitlabId('Gitlab group {0}'.format(self._task.task_group.gitlab_group_id))

        new_user_id = add_or_update_group_member(
            user_id=self._task.owner.user_id,
            group_id=self._task.task_group.gitlab_group.gitlab_id,
            username=self._task.username,
            access_level=self._task.access_level
        )
        self._task.new_user, _ = models.GitlabUser.objects.get_or_create(gitlab_id=new_user_id)


celery_app.register_task(AddGroupMemberTask())
