from itertools import chain

from core import models as core_models
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class GitlabGroup(core_models.AbstractGitlabModel):
    def __str__(self):
        return "<Group: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()

    def get_unfinished_task_list(self, include_groups=False):
        task_group_list = self.get_unfinished_task_group_list() if include_groups else []
        add_subgroup_list = self.get_unfinished_add_subgroup_list(include_groups)
        add_project_list = self.get_unfinished_add_project_list(include_groups)
        add_member_list = self.get_unfinished_add_member_list(include_groups)

        return sorted(
            chain(task_group_list, add_subgroup_list, add_project_list, add_member_list),
            key=lambda instance: instance.execute_date,
            reverse=True)

    def get_unfinished_task_group_list(self):
        return TaskGroup.objects.filter(Q(gitlab_group=self) & Q(finished_date__isnull=True)).order_by('-execute_date')

    def get_unfinished_add_subgroup_list(self, include_groups=False):
        return self._get_unfinished_task_list(AddSubgroup, include_groups)

    def get_unfinished_add_project_list(self, include_groups=False):
        return self._get_unfinished_task_list(AddProject, include_groups)

    def get_unfinished_add_member_list(self, include_groups=False):
        return self._get_unfinished_task_list(AddMember, include_groups)

    def _get_unfinished_task_list(self, model, include_groups=False):
        if include_groups:
            return model.objects.filter(
                Q(gitlab_group=self) & (
                    Q(status=model.WAITING) |
                    Q(status=model.READY) |
                    Q(status=model.RUNNING)) &
                Q(task_group_id__isnull=True)).order_by('-execute_date')
        else:
            return model.objects.filter(
                Q(gitlab_group=self) & (
                    Q(status=model.WAITING) |
                    Q(status=model.READY) |
                    Q(status=model.RUNNING))).order_by('-execute_date')

    def get_finished_task_list(self, include_groups=False):
        task_group_list = self.get_finished_task_group_list() if include_groups else []
        add_subgroup_list = self.get_finished_add_subgroup_list(include_groups)
        add_project_list = self.get_finished_add_project_list(include_groups)
        add_member_list = self.get_finished_add_member_list(include_groups)

        return sorted(
            chain(task_group_list, add_subgroup_list, add_project_list, add_member_list),
            key=lambda instance: instance.finished_date)

    def get_finished_task_group_list(self):
        return TaskGroup.objects.filter(Q(gitlab_group=self) & Q(finished_date__isnull=False))

    def get_finished_add_subgroup_list(self, include_groups=False):
        return self._get_finished_task_list(AddSubgroup, include_groups)

    def get_finished_add_project_list(self, include_groups=False):
        return self._get_finished_task_list(AddProject, include_groups)

    def get_finished_add_member_list(self, include_groups=False):
        return self._get_finished_task_list(AddMember, include_groups)

    def _get_finished_task_list(self, model, include_groups=False):
        if include_groups:
            return model.objects.filter(
                Q(gitlab_group=self) & (
                    Q(status=model.SUCCEED) |
                    Q(status=model.FAILED) &
                    Q(task_group_id__isnull=True)))
        else:
            return model.objects.filter(
                Q(gitlab_group=self) & (
                    Q(status=model.SUCCEED) |
                    Q(status=model.FAILED)
                ))


class GitlabProject(core_models.AbstractGitlabModel):
    def __str__(self):
        return "<Project: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()


class TaskGroup(core_models.AbstractTaskGroup):
    _parent_task_model = 'AddSubgroup'

    gitlab_group = models.ForeignKey(GitlabGroup, on_delete=models.CASCADE, blank=True)

    def clean(self):
        super().clean()

        if self.pk is None:
            if getattr(self, 'parent_task', None) and getattr(self, 'gitlab_group', None):
                raise ValidationError(
                    {'gitlab_group': _(
                        'Do not set gitlab_group with parent_task. It is set from parent_task if parent_task exist')})

    def _pre_save(self, *args, **kwargs):
        super()._pre_save(*args, **kwargs)

        if self.parent_task:
            self.gitlab_group = self.parent_task.new_gitlab_group

    @property
    def edit_url(self):
        return reverse('groups:edit_task_group', kwargs={'task_group_id': self.id})

    @property
    def delete_url(self):
        return '#'

    @property
    def tasks_page_url(self):
        if self.gitlab_group.gitlab_id:
            return reverse('groups:tasks', kwargs={'group_id': self.gitlab_group.gitlab_id})
        else:
            return reverse('groups:future_group_tasks', kwargs={'task_id': self.parent_task.id})


class AbstractTask(core_models.AbstractTask):
    _parent_task_model = 'AddSubgroup'
    _task_group_model = TaskGroup

    gitlab_group = models.ForeignKey(GitlabGroup, on_delete=models.CASCADE, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if self.pk is None:
            if getattr(self, 'task_group', None) and getattr(self, 'gitlab_group', None):
                raise ValidationError(
                    {'gitlab_group': _(
                        'Do not set gitlab_group with task_group. It is set from task_group if task_group exist')})

            if getattr(self, 'parent_task', None) and getattr(self, 'gitlab_group', None):
                raise ValidationError(
                    {'gitlab_group': _(
                        'Do not set gitlab_group with parent_task. It is set from parent_task if parent_task exist')})

    def _pre_save(self, *args, **kwargs):
        super()._pre_save(*args, **kwargs)

        if self.task_group:
            self.gitlab_group = self.task_group.gitlab_group
        elif self.parent_task:
            self.gitlab_group = self.parent_task.new_gitlab_group

    @property
    def tasks_page_url(self):
        if self.gitlab_group.gitlab_id:
            return reverse('groups:tasks', kwargs={'group_id': self.gitlab_group.gitlab_id})
        else:
            return reverse('groups:future_group_tasks', kwargs={'task_id': self.parent_task.id})


class AddSubgroup(AbstractTask, core_models.AbstractVisibilityLevel):
    name = models.CharField(max_length=100)
    path = models.SlugField(max_length=100)
    description = models.TextField(max_length=2000, null=True, blank=True)
    new_gitlab_group = models.OneToOneField(GitlabGroup, on_delete=models.CASCADE, blank=True,
                                            related_name='task_creator')

    def _pre_save(self, *args, **kwargs):
        super()._pre_save(*args, **kwargs)

        if self.pk is None:
            if getattr(self, 'new_gitlab_group', None) is None:
                self.new_gitlab_group = GitlabGroup.objects.create()

    @property
    def get_name(self):
        return _('Create subgroup: {}'.format(self.name))

    @property
    def edit_url(self):
        kwargs = {
            'task_id': self.id,
        }
        return reverse('groups:edit_subgroup_task', kwargs=kwargs)

    @property
    def delete_url(self):
        return '#'

    def _get_task_path(self):
        return 'groups.tasks.AddSubgroupTask'


class AddProject(AbstractTask, core_models.AbstractVisibilityLevel):
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

        # if self.create_type != self.BLANK:
        #     if not self.import_url:
        #         raise ValidationError(
        #             {'import_url': _('Import_url must be specified')})
        # else:
        #     self.import_url = ''

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
        return 'groups.tasks.AddProjectTask'


class AddMember(AbstractTask, core_models.AbstractAccessLevel):
    username = models.CharField(max_length=100)
    new_gitlab_user = models.ForeignKey(core_models.GitlabUser, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def get_name(self):
        return _('Add user: {}'.format(self.username))

    @property
    def edit_url(self):
        kwargs = {
            'task_id': self.id,
        }
        return reverse('groups:edit_member_task', kwargs=kwargs)

    @property
    def delete_url(self):
        return '#'

    def _get_task_path(self):
        return 'groups.tasks.AddMemberTask'
