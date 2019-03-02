import unittest
from django.test import TestCase

from authentication.models import GitlabUser
from .test_models import GitlabUserModelMethod


class GitlabUserSignalsTests(TestCase, GitlabUserModelMethod):
    def equal(self, gitlab_user, auth_user, social_auth):
        self.assertEqual(gitlab_user.auth_user, auth_user)
        self.assertEqual(gitlab_user.social_auth, social_auth)
        self.assertEqual(gitlab_user.gitlab_id, social_auth.uid)

    def test_after_creating_social_auth_with_provider_not_gitlab_do_nothing(self):
        auth_user, social_auth = self.create_auth_user_and_social_auth(provider='test')
        with self.assertRaises(GitlabUser.DoesNotExist):
            GitlabUser.objects.get(social_auth=social_auth)

    def test_after_creating_social_auth_create_user(self):
        auth_user, social_auth = self.create_auth_user_and_social_auth()
        user = GitlabUser.objects.get(social_auth=social_auth)
        self.equal(user, auth_user, social_auth)

    def test_after_saving_social_auth_create_user_if_not_exist(self):
        auth_user, social_auth = self.create_auth_user_and_social_auth()
        GitlabUser.objects.get(social_auth=social_auth).delete()
        social_auth.save()
        user = GitlabUser.objects.get(social_auth=social_auth)
        self.equal(user, auth_user, social_auth)

    def test_after_creating_social_auth_connect_him_to_existing_user(self):
        gitlab_id = 10
        user = self.create_gitlab_user(gitlab_id=gitlab_id)
        auth_user, social_auth = self.create_auth_user_and_social_auth(uid=gitlab_id)
        user.refresh_from_db()
        self.equal(user, auth_user, social_auth)

    @unittest.skip("GiLabUser does not contain mutable attributes")
    def test_after_saving_social_auth_update_user(self):
        auth_user, social_auth = self.create_auth_user_and_social_auth()
        social_auth.uid = 400
        social_auth.save()
        user = GitlabUser.objects.get(social_auth=social_auth)
        self.equal(user, auth_user, social_auth)
