import unittest
from unittest import mock
from django.test import TestCase
from httmock import HTTMock
import json

from core.models import GitlabUser
from core.tests.test_models import GitlabUserModelMethod
from groups import models
from groups.tasks import AddGroupMemberTask
from GitLabApi import mock_all_gitlab_url


class AddGroupMemberTaskTests(TestCase, GitlabUserModelMethod):
    def setUp(self):
        self.gitlab_user = self.create_gitlab_user()
        self.gitlab_group = models.GitlabGroup.objects.create(gitlab_id=1)
        self.task_group_model = models.AddGroupMemberTaskGroup.objects.create(
            gitlab_group=self.gitlab_group
        )
        self.task_model = models.AddGroupMemberTask.objects.create(
            owner=self.gitlab_user,
            task_group=self.task_group_model,
            username='username',
        )

    def create_gitlab_user(self, **kwargs):
        auth_user, social_auth = self.create_auth_user_and_social_auth()
        return GitlabUser.objects.get(social_auth=social_auth)

    def get_run_args(self):
        return json.loads(self.task_model.celery_task.kwargs)

    @mock_all_gitlab_url
    def test_gitlab_group_does_not_have_gitlab_id(self):
        self.gitlab_group.gitlab_id = None
        self.gitlab_group.save()

        AddGroupMemberTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.assertEqual(self.task_model.status, self.task_model.FAILED)
        self.assertNotEqual(self.task_model.error_msg, "")

    @mock_all_gitlab_url
    def test_run_correctly(self):
        from GitLabApi.tests.test_gitlab_api import TestGitLabGroupMembersApi

        args_dict = {
            'user_id': 1,
            'access_level': self.task_model.access_level,
        }

        with HTTMock(TestGitLabGroupMembersApi().get_mock_create_url(args=args_dict)):
            AddGroupMemberTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.assertNotEqual(self.task_model.new_user, None)
        self.assertEqual(self.task_model.status, self.task_model.COMPLETED)
