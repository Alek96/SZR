from GitLabApi import GitLabApi
from GitLabApi.exceptions import GitlabGetError
from core.exceptions import DoesNotContainGitlabId
from core.models import GitlabUser
from core.tasks import BaseTask
from groups import models

from SZR.celery import app as celery_app


def create_subgroup(user_id, name, path, group_id=None, **kwargs):
    new_group = GitLabApi(user_id).groups.create({
        'name': name,
        'path': path,
        'parent_id': group_id,
        **kwargs
    })

    return new_group.id


def add_or_update_member(user_id, group_id, username, access_level, **kwargs):
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


class AddSubgroupTask(BaseTask):
    _task_model = models.AddSubgroup

    def _run(self, **kwargs):
        if not self._task.gitlab_group.gitlab_id:
            raise DoesNotContainGitlabId('Gitlab group {0}'.format(self._task.gitlab_group_id))

        new_group_id = create_subgroup(
            user_id=self._task.owner.user_id,
            group_id=self._task.gitlab_group.gitlab_id,
            name=self._task.name,
            path=self._task.path,
            description=self._task.description,
            visibility=self._task.visibility,
        )
        self._task.new_gitlab_group.gitlab_id = new_group_id

    def _finnish(self):
        super()._finnish()
        self._task.new_gitlab_group.save()


celery_app.register_task(AddSubgroupTask())


class AddMemberTask(BaseTask):
    _task_model = models.AddMember

    def _run(self, **kwargs):
        if not self._task.gitlab_group.gitlab_id:
            raise DoesNotContainGitlabId('Gitlab group {0}'.format(self._task.gitlab_group_id))

        new_user_id = add_or_update_member(
            user_id=self._task.owner.user_id,
            group_id=self._task.gitlab_group.gitlab_id,
            username=self._task.username,
            access_level=self._task.access_level
        )
        self._task.new_gitlab_user, _ = GitlabUser.objects.get_or_create(gitlab_id=new_user_id)


celery_app.register_task(AddMemberTask())
