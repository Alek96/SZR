from GitLabApi import GitLabApi
from core import forms
from core.exceptions import FormNotValidError
from core.models import GitlabUser
from django import forms as django_forms
from django.utils.translation import gettext_lazy as _
from groups import forms as groups_forms

from . import models
from . import tasks


class AddProjectForm(groups_forms.BaseTaskForm):
    class Meta(forms.BaseTaskForm.Meta):
        model = models.AddProject
        fields = ['name', 'path', 'description', 'visibility', 'create_type',
                  'import_url'] + forms.BaseTaskForm.Meta.fields

    def _save_in_gitlab(self, data, user_id, group_id=None, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, group_id=group_id, **kwargs)

        tasks.create_project(
            user_id=user_id,
            group_id=group_id,
            name=data['name'],
            path=data['path'],
            description=data['description'],
            visibility=data['visibility'],
            import_url=data['import_url'],
            **kwargs)


class AddMultipleProjectForm(groups_forms.TaskGroupForm):
    SUFFIX_NUMBER = 'number'
    SUFFIX_CHOICES = (
        (SUFFIX_NUMBER, _('Number')),
    )

    suffix = django_forms.ChoiceField(choices=SUFFIX_CHOICES, initial=SUFFIX_NUMBER)

    access_level = django_forms.TypedChoiceField(coerce=int, empty_value=None,
                                                 choices=models.AddMember.ACCESS_LEVEL_CHOICES,
                                                 initial=models.AddMember.ACCESS_GUEST)

    def _post_save(self, model, user_id, project_form, **kwargs):
        try:
            owner = GitlabUser.objects.get(user_id=user_id)
            members = GitLabApi(user_id).groups.get(model.gitlab_group.gitlab_id).members.all()
            members = GitLabApi(user_id).groups.get(model.gitlab_group.gitlab_id)
            suffix = 0
            for member in members:
                project = models.AddProject.objects.create(
                    owner=owner,
                    task_group=model,
                    name=project_form.data['name'] + '_' + str(suffix),
                    path=project_form.data['path'] + '_' + str(suffix),
                    description=project_form.data['description'],
                    visibility=project_form.data['visibility'],
                    create_type=project_form.data['create_type'],
                    import_url=project_form.data['import_url']
                )

                models.AddMember.objects.create(
                    owner=owner,
                    parent_task=project,
                    username=member.username,
                    access_level=self.data['access_level']
                )

                suffix += 1
        except Exception as err:
            self.add_error(None, str(err))
            model.delete()
            raise FormNotValidError(self.errors.as_data())


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
