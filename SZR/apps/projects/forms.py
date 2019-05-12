from core import forms
from groups.forms import BaseTaskForm as groups_BaseTaskForm

from . import models
from . import tasks


class AddProjectForm(groups_BaseTaskForm):
    # ONE = 'One'
    # ONE_FOR_ALL_USER = 'one_for_all_users'
    # PER_USER = 'per_user'
    # HOW_MANY_CHOICES = (
    #     (ONE, _('One')),
    #     (ONE_FOR_ALL_USER, _('One for all users')),
    #     (PER_USER, _('One per user')),
    # )
    #
    # how_many = django_forms.ChoiceField(choices=HOW_MANY_CHOICES, initial=ONE)

    class Meta(forms.BaseTaskForm.Meta):
        model = models.AddProject
        fields = ['name', 'path', 'description', 'visibility'] + forms.BaseTaskForm.Meta.fields

    def _save_in_gitlab(self, data, user_id, group_id=None, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, group_id=group_id, **kwargs)
        tasks.create_project(
            user_id=user_id,
            group_id=group_id,
            name=data['name'],
            path=data['path'],
            description=data['description'],
            visibility=data['visibility'],
            # import_url=data['import_url'],
            **kwargs)


class TaskGroupForm(forms.BaseTaskGroupForm):
    class Meta(forms.BaseTaskGroupForm.Meta):
        model = models.TaskGroup

    def _pre_save(self, model, project_id=None, parent_task=None, **kwargs):
        super()._pre_save(model=model, project_id=project_id, parent_task=parent_task, **kwargs)
        if parent_task and project_id:
            raise ValueError("project_id and task_id cannot be specified at the same time")

        if parent_task:
            model.parent_task = parent_task
        elif project_id:
            model.gitlab_project, _ = models.GitlabProject.objects.get_or_create(gitlab_id=project_id)
        else:
            raise ValueError("project_id or task_id must be specified")


class BaseTaskForm(forms.BaseTaskForm):
    def _pre_save(self, model, project_id=None, parent_task=None, **kwargs):
        super()._pre_save(model=model, project_id=project_id, parent_task=parent_task, **kwargs)
        if not project_id and not parent_task and not model.task_group:
            raise ValueError("project_id, parent_task or task_group must be specified")

        model.parent_task = parent_task
        if project_id:
            model.gitlab_project, _ = models.GitlabProject.objects.get_or_create(gitlab_id=project_id)


class AddMemberForm(BaseTaskForm):
    class Meta(forms.BaseTaskForm.Meta):
        model = models.AddMember
        fields = ['username', 'access_level'] + forms.BaseTaskForm.Meta.fields

    def _save_in_gitlab(self, data, user_id, project_id, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, project_id=project_id, **kwargs)
        tasks.add_or_update_member(
            user_id=user_id,
            project_id=project_id,
            username=data['username'],
            access_level=data['access_level'],
            **kwargs)
