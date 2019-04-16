from core import forms
from groups import models
from groups import tasks


class TaskGroupForm(forms.BaseTaskGroupForm):
    class Meta(forms.BaseTaskGroupForm.Meta):
        model = models.TaskGroup

    def _save(self, model, group_id=None, parent_task=None, **kwargs):
        super()._save(model=model, group_id=group_id, parent_task=parent_task, **kwargs)
        if parent_task and group_id:
            raise ValueError("group_id and task_id cannot be specified at the same time")

        if parent_task:
            model.parent_task = parent_task
        elif group_id:
            model.gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)
        else:
            raise ValueError("group_id or task_id must be specified")


class BaseTaskForm(forms.BaseTaskForm):
    def _save(self, model, group_id=None, parent_task=None, **kwargs):
        super()._save(model=model, group_id=group_id, parent_task=parent_task, **kwargs)
        if not group_id and not parent_task and not model.task_group:
            raise ValueError("group_id, parent_task or task_group must be specified")

        model.parent_task = parent_task
        if group_id:
            model.gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)


class AddSubgroupForm(BaseTaskForm):
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


class AddMemberForm(BaseTaskForm):
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
