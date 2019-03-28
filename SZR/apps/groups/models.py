from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from core.models import AbstractGitlabModel
from core.models import GitlabUser
from core.models import AbstractTaskGroup, AbstractTask


class GitlabGroup(AbstractGitlabModel):
    def __str__(self):
        return "<Group: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()


class AbstractAccessLevel(models.Model):
    ACCESS_GUEST = 10
    ACCESS_REPORTER = 20
    ACCESS_DEVELOPER = 30
    ACCESS_MASTER = 40
    ACCESS_OWNER = 50
    ACCESS_LEVEL_CHOICES = (
        (ACCESS_GUEST, 'Guest'),
        (ACCESS_REPORTER, 'Reporter'),
        (ACCESS_DEVELOPER, 'Developer'),
        (ACCESS_MASTER, 'Master'),
        (ACCESS_OWNER, 'Owner'),
    )

    access_level = models.IntegerField(choices=ACCESS_LEVEL_CHOICES, default=ACCESS_GUEST)

    class Meta:
        abstract = True


class AddGroupMemberTaskGroup(AbstractTaskGroup):
    gitlab_group = models.ForeignKey(GitlabGroup, on_delete=models.CASCADE)


class AddGroupMemberTask(AbstractTask, AbstractAccessLevel):
    _task_group_model = AddGroupMemberTaskGroup

    username = models.CharField(max_length=100)
    new_user = models.ForeignKey(GitlabUser, on_delete=models.CASCADE, null=True, blank=True)

    def _get_task_path(self):
        return 'groups.tasks.AddGroupMemberTask'
