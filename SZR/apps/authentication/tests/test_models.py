from django.test import TestCase
import unittest
from unittest import mock
from django.conf import settings
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User as Auth_user
from social_django.models import UserSocialAuth

from authentication.models import GitlabUser

module_path = 'authentication.models'


class GitlabUserModelMethod:

    @staticmethod
    def create_gitlab_user(gitlab_id=42, save=True, **kwargs):
        user = GitlabUser(gitlab_id=gitlab_id, **kwargs)
        if save:
            user.save()
        return user

    @staticmethod
    def create_auth_user_and_social_auth(username='userTest', password='password', email='email@example.com',
                                         first_name='name', last_name='', provider='gitlab', uid=500, extra_data=None):

        if not extra_data:
            extra_data = {"auth_time": 0, "id": uid, "expires": None, "refresh_token": "aaa", "access_token": "bbb",
                          "token_type": "bearer"}

        auth_user = Auth_user.objects.create(username=username, email=email, password=password,
                                             first_name=first_name, last_name=last_name)
        social_auth = UserSocialAuth.objects.create(provider=provider, uid=uid, user_id=auth_user.id,
                                                    extra_data=extra_data)

        return auth_user, social_auth


class GitlabUserModelUnitTests(unittest.TestCase, GitlabUserModelMethod):
    def test_representation(self):
        user = self.create_gitlab_user(save=False)
        self.assertEqual(repr(user), "<User: {}>".format(user.id))

    def test_string_representation(self):
        user = self.create_gitlab_user(save=False)
        self.assertEqual(str(user), "<User: {}>".format(user.id))

    def test_social_auth_does_not_exists_and_does_not_has_access_token(self):
        user = self.create_gitlab_user(save=False)
        self.assertFalse(user.has_access_token())
        with self.assertRaises(RuntimeError):
            self.assertEqual(user.get_access_token(), None)

    def test_social_auth_does_not_has_access_token(self):
        user = self.create_gitlab_user(save=False)
        user.social_auth = UserSocialAuth()
        self.assertFalse(user.has_access_token())
        with self.assertRaises(RuntimeError):
            self.assertEqual(user.get_access_token(), None)

    def test_social_auth_has_access_token(self):
        access_token = 'token'
        user = self.create_gitlab_user(save=False)
        user.social_auth = UserSocialAuth()
        user.social_auth.extra_data['access_token'] = access_token
        self.assertTrue(user.has_access_token())
        self.assertEqual(user.get_access_token(), access_token)
