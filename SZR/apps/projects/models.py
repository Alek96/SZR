from core import models as core_models
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from groups.models import GitlabProject, AddProject


class TaskGroup(core_models.AbstractTaskGroup):
    _parent_task_model = 'groups.AddProject'

    gitlab_project = models.ForeignKey(GitlabProject, on_delete=models.CASCADE, blank=True)

    def clean(self):
        super().clean()

        if self.pk is None:
            if getattr(self, 'parent_task', None) and getattr(self, 'gitlab_project', None):
                raise ValidationError(
                    {'gitlab_project': _(
                        'Do not set gitlab_project with parent_task. It is set from parent_task if parent_task exist')})

    def _pre_save(self, *args, **kwargs):
        super()._pre_save(*args, **kwargs)

        if self.parent_task:
            self.gitlab_project = self.parent_task.new_gitlab_project

    @property
    def edit_url(self):
        return reverse('projects:edit_task_group', kwargs={'task_group_id': self.id})

    @property
    def delete_url(self):
        return '#'

    @property
    def tasks_page_url(self):
        if self.gitlab_project.gitlab_id:
            return reverse('projects:tasks', kwargs={'project_id': self.gitlab_project.gitlab_id})
        else:
            return reverse('projects:future_project_tasks', kwargs={'task_id': self.gitlab_project.id})


class AbstractTask(core_models.AbstractTask):
    _parent_task_model = 'groups.AddProject'
    _task_group_model = TaskGroup

    gitlab_project = models.ForeignKey(GitlabProject, on_delete=models.CASCADE, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if self.pk is None:
            if getattr(self, 'task_group', None) and getattr(self, 'gitlab_project', None):
                raise ValidationError(
                    {'gitlab_project': _(
                        'Do not set gitlab_project with task_group. It is set from task_group if task_group exist')})

            if getattr(self, 'parent_task', None) and getattr(self, 'gitlab_project', None):
                raise ValidationError(
                    {'gitlab_project': _(
                        'Do not set gitlab_project with parent_task. It is set from parent_task if parent_task exist')})

    def _pre_save(self, *args, **kwargs):
        super()._pre_save(*args, **kwargs)

        if self.task_group:
            self.gitlab_project = self.task_group.gitlab_project
        elif self.parent_task:
            self.gitlab_project = self.parent_task.new_gitlab_project

    @property
    def tasks_page_url(self):
        if self.gitlab_project.gitlab_id:
            return reverse('projects:tasks', kwargs={'project_id': self.gitlab_project.gitlab_id})
        else:
            return reverse('projects:future_project_tasks', kwargs={'task_id': self.parent_task.id})


class AddMember(AbstractTask, core_models.AbstractAccessLevel):
    username = models.CharField(max_length=100)
    new_gitlab_user = models.ForeignKey(core_models.GitlabUser, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='+')

    @property
    def get_name(self):
        return _('Add user: {}'.format(self.username))

    @property
    def edit_url(self):
        kwargs = {
            'task_id': self.id,
        }
        return reverse('projects:edit_member_task', kwargs=kwargs)

    @property
    def delete_url(self):
        return '#'

    def _get_task_path(self):
        return 'projects.tasks.AddMemberTask'
