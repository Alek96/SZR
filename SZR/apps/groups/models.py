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

    def get_unfinished_task_list(self):
        add_subgroup_group = self.get_unfinished_add_subgroup_group()
        add_member_group = self.get_unfinished_add_member_group()

        return sorted(
            chain(add_subgroup_group, add_member_group),
            key=lambda instance: instance.execute_date,
            reverse=True)

    def get_unfinished_add_subgroup_group(self):
        return self._get_unfinished_task_list(AddSubgroup)

    def get_unfinished_add_member_group(self):
        return self._get_unfinished_task_list(AddMember)

    def _get_unfinished_task_list(self, model):
        return model.objects.filter(
            Q(gitlab_group=self) & (
                Q(status=model.WAITING) |
                Q(status=model.READY) |
                Q(status=model.RUNNING)
            )).order_by('-execute_date')

    def get_finished_task_list(self):
        add_subgroup_group = self.get_finished_add_subgroup_group()
        add_member_group = self.get_finished_add_member_group()

        return sorted(
            chain(add_subgroup_group, add_member_group),
            key=lambda instance: instance.finished_date)

    def get_finished_add_subgroup_group(self):
        return self._get_finished_task_list(AddSubgroup)

    def get_finished_add_member_group(self):
        return self._get_finished_task_list(AddMember)

    def _get_finished_task_list(self, model):
        return model.objects.filter(
            Q(gitlab_group=self) & (
                Q(status=model.SUCCEED) |
                Q(status=model.FAILED)
            ))


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
    def task_name(self):
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


class AddMember(AbstractTask, core_models.AbstractAccessLevel):
    username = models.CharField(max_length=100)
    new_gitlab_user = models.ForeignKey(core_models.GitlabUser, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def task_name(self):
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
