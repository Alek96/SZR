from core import forms
from groups import models
from groups import tasks


class BaseTaskGroupForm(forms.BaseTaskGroupForm):
    _parent_task_model = models.AddSubgroup

    def _save(self, model, group_id=None, task_id=None, **kwargs):
        super()._save(model=model, group_id=group_id, **kwargs)
        if task_id:
            model.parent_task = self._parent_task_model.objects.get(id=task_id)
        elif group_id:
            model.gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)
        else:
            raise ValueError("group_id or task_id must be specified")


class AddSubgroupGroupForm(BaseTaskGroupForm):
    class Meta(BaseTaskGroupForm.Meta):
        model = models.AddSubgroupGroup


class AddSubgroupForm(forms.BaseTaskForm):
    class Meta(forms.BaseTaskForm.Meta):
        model = models.AddSubgroup
        fields = ['name', 'path', 'description', 'visibility'] + forms.BaseTaskForm.Meta.fields

    def _save_in_gitlab(self, data, user_id, group_id=None, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, group_id=group_id, **kwargs)
        tasks.create_subgroup(
            user_id=user_id,
            group_id=group_id,
            name=data['name'],
            path=data['path'],
            description=data['description'],
            visibility=data['visibility'],
            **kwargs)


class AddMemberGroupForm(BaseTaskGroupForm):
    class Meta(BaseTaskGroupForm.Meta):
        model = models.AddMemberGroup


class AddMemberForm(forms.BaseTaskForm):
    class Meta(forms.BaseTaskForm.Meta):
        model = models.AddMember
        fields = ['username', 'access_level'] + forms.BaseTaskForm.Meta.fields

    def _save_in_gitlab(self, data, user_id, group_id, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, group_id=group_id, **kwargs)
        tasks.add_or_update_member(
            user_id=user_id,
            group_id=group_id,
            username=data['username'],
            access_level=data['access_level'],
            **kwargs)
