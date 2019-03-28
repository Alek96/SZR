import unittest
from django.test import TestCase

from core.models import GitlabUser
from core.tests.test_models import GitlabUserModelMethod


class GitlabUserSignalsTests(TestCase, GitlabUserModelMethod):
    def equal(self, gitlab_user, user, user_social_auth):
        self.assertEqual(gitlab_user.user, user)
        self.assertEqual(gitlab_user.user_social_auth, user_social_auth)
        self.assertEqual(gitlab_user.gitlab_id, user_social_auth.uid)

    def test_after_creating_user_social_auth_with_provider_not_gitlab_do_nothing(self):
        user, user_social_auth = self.create_user_and_user_social_auth(provider='test')
        with self.assertRaises(GitlabUser.DoesNotExist):
            GitlabUser.objects.get(user_social_auth=user_social_auth)

    def test_after_creating_user_social_auth_create_user(self):
        user, user_social_auth = self.create_user_and_user_social_auth()
        gitlab_user = GitlabUser.objects.get(user_social_auth=user_social_auth)
        self.equal(gitlab_user, user, user_social_auth)

    def test_after_saving_social_auth_create_user_if_not_exist(self):
        user, user_social_auth = self.create_user_and_user_social_auth()
        GitlabUser.objects.get(user_social_auth=user_social_auth).delete()
        user_social_auth.save()
        gitlab_user = GitlabUser.objects.get(user_social_auth=user_social_auth)
        self.equal(gitlab_user, user, user_social_auth)

    def test_after_creating_social_auth_connect_him_to_existing_user(self):
        gitlab_id = 10
        gitlab_user = self.create_gitlab_user(gitlab_id=gitlab_id)
        user, user_social_auth = self.create_user_and_user_social_auth(uid=gitlab_id)
        gitlab_user.refresh_from_db()
        self.equal(gitlab_user, user, user_social_auth)

    @unittest.skip("GiLabUser does not contain mutable attributes")
    def test_after_saving_social_auth_update_user(self):
        user, user_social_auth = self.create_user_and_user_social_auth()
        user_social_auth.uid = 400
        user_social_auth.save()
        gitlab_user = GitlabUser.objects.get(user_social_auth=user_social_auth)
        self.equal(gitlab_user, user, user_social_auth)
