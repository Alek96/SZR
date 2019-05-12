from itertools import chain

from core import models as core_models
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from groups import models as group_models


class GitlabProject(core_models.AbstractGitlabModel):
    def __str__(self):
        return "<Project: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()

    def get_unfinished_task_list(self, model=None, include_groups=False):
        if model:
            return self._get_unfinished_task_list(model, include_groups)

        tasks_model = [AddMember]
        task_lists = []
        if include_groups:
            task_lists.append(self.get_unfinished_task_group_list())
        for task_model in tasks_model:
            task_lists.append(self._get_unfinished_task_list(task_model, include_groups))

        return sorted(
            chain(*task_lists),
            key=lambda instance: instance.execute_date,
            reverse=True)

    def get_unfinished_task_group_list(self):
        return TaskGroup.objects.filter(Q(gitlab_project=self) & Q(finished_date__isnull=True)).order_by(
            '-execute_date')

    def _get_unfinished_task_list(self, model, include_groups=False):
        if include_groups:
            return model.objects.filter(
                Q(gitlab_project=self) & (
                    Q(status=model.WAITING) |
                    Q(status=model.READY) |
                    Q(status=model.RUNNING)) &
                Q(task_group_id__isnull=True)).order_by('-execute_date')
        else:
            return model.objects.filter(
                Q(gitlab_project=self) & (
                    Q(status=model.WAITING) |
                    Q(status=model.READY) |
                    Q(status=model.RUNNING))).order_by('-execute_date')

    def get_finished_task_list(self, model=None, include_groups=False):
        if model:
            return self._get_finished_task_list(model, include_groups)

        tasks_model = [AddMember]
        task_lists = []
        if include_groups:
            task_lists.append(self.get_finished_task_group_list())
        for task_model in tasks_model:
            task_lists.append(self._get_finished_task_list(task_model, include_groups))

        return sorted(
            chain(*task_lists),
            key=lambda instance: instance.finished_date)

    def get_finished_task_group_list(self):
        return TaskGroup.objects.filter(Q(gitlab_project=self) & Q(finished_date__isnull=False))

    def _get_finished_task_list(self, model, include_groups=False):
        if include_groups:
            return model.objects.filter(
                Q(gitlab_project=self) & (
                    Q(status=model.SUCCEED) |
                    Q(status=model.FAILED) &
                    Q(task_group_id__isnull=True)))
        else:
            return model.objects.filter(
                Q(gitlab_project=self) & (
                    Q(status=model.SUCCEED) |
                    Q(status=model.FAILED)
                ))


class AddProject(group_models.AbstractTask, core_models.AbstractVisibilityLevel):
    BLANK = 'blank'
    FORK = 'fork'
    COPY = 'copy'
    CREATE_TYPE_CHOICES = (
        (BLANK, _('Blank')),
        (FORK, _('Fork')),
        (COPY, _('Copy')),
    )

    create_type = models.CharField(max_length=10, choices=CREATE_TYPE_CHOICES, default=BLANK)
    name = models.CharField(max_length=100)
    path = models.SlugField(max_length=100)
    description = models.TextField(max_length=2000, null=True, blank=True)
    import_url = models.URLField(max_length=200, null=True, blank=True)
    new_gitlab_project = models.OneToOneField(GitlabProject, on_delete=models.CASCADE, blank=True)

    def clean(self):
        super().clean()

        if self.create_type != self.BLANK and not self.import_url:
            raise ValidationError(
                {'import_url': _('Import_url must be specified')})
        else:
            self.import_url = None

    def _pre_save(self, *args, **kwargs):
        super()._pre_save(*args, **kwargs)

        if self.pk is None:
            if getattr(self, 'new_gitlab_project', None) is None:
                self.new_gitlab_project = GitlabProject.objects.create()

    @property
    def get_name(self):
        return _('Create project: {}'.format(self.name))

    @property
    def edit_url(self):
        kwargs = {
            'task_id': self.id,
        }
        return reverse('groups:edit_project_task', kwargs=kwargs)

    @property
    def delete_url(self):
        return '#'

    def _get_task_path(self):
        return 'projects.tasks.AddProjectTask'


class TaskGroup(core_models.AbstractTaskGroup):
    _parent_task_model = 'projects.AddProject'

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
    _parent_task_model = 'projects.AddProject'
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
