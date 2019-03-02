from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User as Auth_user
from social_django.models import UserSocialAuth
from django.core.exceptions import ValidationError

from core.models import AbstractGitlabModel


class GitlabUser(AbstractGitlabModel):
    auth_user = models.OneToOneField(Auth_user, on_delete=models.SET_NULL, null=True, blank=True)
    social_auth = models.OneToOneField(UserSocialAuth, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='SZR_user')

    def has_access_token(self):
        if self.social_auth:
            return 'access_token' in self.social_auth.extra_data
        return False

    def get_access_token(self):
        if self.has_access_token():
            return self.social_auth.extra_data['access_token']
        raise RuntimeError("User {} does not have access token".format(self))

    def __str__(self):
        return "<User: {}>".format(self.id)

    def __repr__(self):
        return self.__str__()
