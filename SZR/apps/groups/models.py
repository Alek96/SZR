from itertools import chain
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse

from core.models import AbstractGitlabModel
from core.models import GitlabUser
from core.models import AbstractTaskGroup, AbstractTask
from core.models import AbstractAccessLevel, AbstractVisibilityLevel


class GitlabGroup(AbstractGitlabModel):
    def __str__(self):
        return "<Group: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()

    def get_unfinished_task_list(self):
        add_subgroup_group = AddSubgroupGroup.objects.filter(
            Q(gitlab_group=self) & (
                Q(status=AddSubgroupGroup.WAITING) |
                Q(status=AddSubgroupGroup.READY) |
                Q(status=AddSubgroupGroup.RUNNING)
            ))

        add_member_group = AddMemberGroup.objects.filter(
            Q(gitlab_group=self) & (
                Q(status=AddMemberGroup.WAITING) |
                Q(status=AddMemberGroup.READY) |
                Q(status=AddMemberGroup.RUNNING)
            ))

        return sorted(
            chain(add_subgroup_group, add_member_group),
            key=lambda instance: instance.execute_date,
            reverse=True)

    def get_finished_task_list(self):
        add_subgroup_group = AddSubgroupGroup.objects.filter(
            Q(gitlab_group=self) & (
                Q(status=AddSubgroupGroup.SUCCEED) |
                Q(status=AddSubgroupGroup.FAILED)
            ))

        add_member_group = AddMemberGroup.objects.filter(
            Q(gitlab_group=self) & (
                Q(status=AddMemberGroup.SUCCEED) |
                Q(status=AddMemberGroup.FAILED)
            ))

        return sorted(
            chain(add_subgroup_group, add_member_group),
            key=lambda instance: instance.finished_date)


class AbstractParentTaskAddSubgroup(AbstractTaskGroup):
    gitlab_group = models.ForeignKey(GitlabGroup, on_delete=models.CASCADE, blank=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        if self.pk is None:
            if self.parent_task and getattr(self, 'gitlab_group', None):
                raise ValidationError({
                    'gitlab_group':
                        _('gitlab_group cannot be set if parent_task is set. Value is being copied from it')
                })

    def _save(self, *args, **kwargs):
        super()._save(*args, **kwargs)

        if self.pk is None:
            if self.parent_task and not getattr(self, 'gitlab_group', None):
                self.gitlab_group = self.parent_task.new_gitlab_group


class AbstractAddSubgroup(AbstractTask):
    new_gitlab_group = models.ForeignKey(GitlabGroup, on_delete=models.CASCADE, blank=True)

    def _save(self, *args, **kwargs):
        super()._save(*args, **kwargs)

        if self.pk is None:
            if getattr(self, 'new_gitlab_group', None) is None:
                self.new_gitlab_group = GitlabGroup.objects.create()

    class Meta:
        abstract = True


class AddSubgroupGroup(AbstractParentTaskAddSubgroup):
    _parent_task_model = 'AddSubgroup'

    @property
    def link_to_edit(self):
        kwargs = {
            'task_group_id': self.id,
        }
        return reverse('groups:edit_subgroup_group', kwargs=kwargs)

    @property
    def link_to_delete(self):
        return '#'

    @property
    def link_to_tasks_page(self):
        kwargs = {
            'group_id': self.gitlab_group.gitlab_id,
        }
        return reverse('groups:tasks', kwargs=kwargs)

    @property
    def link_to_new_task(self):
        kwargs = {
            'group_id': self.gitlab_group.gitlab_id,
            'task_group_id': self.id,
        }
        return reverse('groups:new_subgroup_task', kwargs=kwargs)


class AddSubgroup(AbstractAddSubgroup, AbstractVisibilityLevel):
    _task_group_model = AddSubgroupGroup

    name = models.CharField(max_length=100)
    path = models.SlugField(max_length=100)
    description = models.TextField(max_length=2000, null=True, blank=True)

    @property
    def task_name(self):
        return _('Create subgroup: {}'.format(self.name))

    @property
    def link_to_edit(self):
        kwargs = {
            'task_id': self.id,
        }
        return reverse('groups:edit_subgroup_task', kwargs=kwargs)

    @property
    def link_to_delete(self):
        return '#'

    @property
    def link_to_tasks_page(self):
        kwargs = {
            'group_id': self.task_group.gitlab_group.gitlab_id,
        }
        return reverse('groups:tasks', kwargs=kwargs)

    def _get_task_path(self):
        return 'groups.tasks.AddSubgroupTask'


class AddMemberGroup(AbstractParentTaskAddSubgroup):
    _parent_task_model = 'AddSubgroup'

    @property
    def link_to_edit(self):
        kwargs = {
            'task_group_id': self.id,
        }
        return reverse('groups:edit_member_group', kwargs=kwargs)

    @property
    def link_to_delete(self):
        return '#'

    @property
    def link_to_tasks_page(self):
        kwargs = {
            'group_id': self.gitlab_group.gitlab_id,
        }
        return reverse('groups:tasks', kwargs=kwargs)

    @property
    def link_to_new_task(self):
        kwargs = {
            'group_id': self.gitlab_group.gitlab_id,
            'task_group_id': self.id,
        }
        return reverse('groups:new_member_task', kwargs=kwargs)


class AddMember(AbstractTask, AbstractAccessLevel):
    _task_group_model = AddMemberGroup

    username = models.CharField(max_length=100)
    new_gitlab_user = models.ForeignKey(GitlabUser, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def task_name(self):
        return _('Add user: {}'.format(self.username))

    @property
    def link_to_edit(self):
        kwargs = {
            'task_id': self.id,
        }
        return reverse('groups:edit_member_task', kwargs=kwargs)

    @property
    def link_to_delete(self):
        return '#'

    @property
    def link_to_tasks_page(self):
        kwargs = {
            'group_id': self.task_group.gitlab_group.gitlab_id,
        }
        return reverse('groups:tasks', kwargs=kwargs)

    def _get_task_path(self):
        return 'groups.tasks.AddMemberTask'
