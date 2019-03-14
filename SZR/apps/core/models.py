from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AbstractGitlabModel(models.Model):
    gitlab_id = models.PositiveIntegerField(unique=True, null=True, blank=True)
    gitlab_web_url = models.URLField(null=True, blank=True)

    class Meta:
        abstract = True
