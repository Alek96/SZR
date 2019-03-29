from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from core.models import AbstractGitlabModel
from core.models import GitlabUser
from core.models import AbstractTaskGroup, AbstractTask
from core.models import AbstractAccessLevel, AbstractVisibilityLevel


class GitlabGroup(AbstractGitlabModel):
    def __str__(self):
        return "<Group: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()


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


class AddSubgroup(AbstractAddSubgroup, AbstractVisibilityLevel):
    _task_group_model = AddSubgroupGroup

    name = models.CharField(max_length=100)
    path = models.SlugField(max_length=100)
    description = models.TextField(max_length=2000, null=True, blank=True)

    def _get_task_path(self):
        return 'groups.tasks.AddSubgroupTask'


class AddMemberGroup(AbstractParentTaskAddSubgroup):
    _parent_task_model = 'AddSubgroup'


class AddMember(AbstractTask, AbstractAccessLevel):
    _task_group_model = AddMemberGroup

    username = models.CharField(max_length=100)
    new_gitlab_user = models.ForeignKey(GitlabUser, on_delete=models.CASCADE, null=True, blank=True)

    def _get_task_path(self):
        return 'groups.tasks.AddMemberTask'
