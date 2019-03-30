from django import forms
from django.contrib.admin import widgets
from django.utils.translation import ugettext as _

from core.forms import BaseTaskGroupForm, BaseTaskForm
from groups import models
from groups import tasks


class AddSubgroupGroupForm(BaseTaskGroupForm):
    class Meta(BaseTaskGroupForm.Meta):
        model = models.AddSubgroupGroup

    def _save(self, model, group_id, **kwargs):
        super()._save(model=model, group_id=group_id, **kwargs)
        model.gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)


class AddSubgroupForm(BaseTaskForm):
    class Meta:
        model = models.AddSubgroup
        fields = ['name', 'path', 'description', 'visibility']

    def _save_in_gitlab(self, data, user_id, group_id=None, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, group_id=group_id, **kwargs)
        tasks.create_subgroup(user_id=user_id, group_id=group_id, **data, **kwargs)


class AddMemberGroupForm(BaseTaskGroupForm):
    class Meta(BaseTaskGroupForm.Meta):
        model = models.AddMemberGroup

    def _save(self, model, group_id, **kwargs):
        super()._save(model=model, group_id=group_id, **kwargs)
        model.gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)


class AddMemberForm(BaseTaskForm):
    class Meta:
        model = models.AddMember
        fields = ['username', 'access_level']

    def _save_in_gitlab(self, data, user_id, group_id, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, group_id=group_id, **kwargs)
        tasks.add_or_update_member(user_id=user_id, group_id=group_id, **data, **kwargs)
