import unittest
from unittest import mock
from django.test import TestCase
from httmock import HTTMock
import json

from core.models import GitlabUser
from core.tests.test_view import LoginMethods
from groups import models
from GitLabApi import mock_all_gitlab_url
from groups.tasks import *
from GitLabApi.tests.test_gitlab_api import *


class AddOrUpdateGroupMemberTests(LoginMethods):
    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_update_user(self):
        with HTTMock(mock_all_urls_and_raise_error):
            with HTTMock(TestGitLabGroupsApi().get_mock_get_url()):
                with HTTMock(TestGitLabUsersApi().get_mock_list_url()):
                    with HTTMock(TestGitLabGroupMembersApi().get_mock_get_url()):
                        with HTTMock(TestGitLabGroupMemberObjApi().get_mock_save_url(args={'access_level': 10})):
                            self.assertTrue(add_or_update_group_member(
                                user_id=self.user.id,
                                group_id=1,
                                username='name',
                                access_level=10
                            ))

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_create_user(self):
        args_dict = {
            'user_id': self.user.id,
            'access_level': 10,
        }

        with HTTMock(mock_all_urls_and_raise_error):
            with HTTMock(TestGitLabGroupsApi().get_mock_get_url()):
                with HTTMock(TestGitLabUsersApi().get_mock_list_url()):
                    with HTTMock(TestGitLabGroupMembersApi().get_mock_get_url(raise_error=GitlabGetError())):
                        with HTTMock(TestGitLabGroupMembersApi().get_mock_create_url(args=args_dict)):
                            self.assertTrue(add_or_update_group_member(
                                user_id=self.user.id,
                                group_id=1,
                                username='name',
                                access_level=10
                            ))


class AddGroupMemberTaskTests(LoginMethods):

    @LoginMethods.create_user_wrapper
    def setUp(self):
        self.gitlab_user = GitlabUser.objects.get(user_social_auth=self.user_social_auth)
        self.gitlab_group = models.GitlabGroup.objects.create(gitlab_id=1)
        self.task_group_model = models.AddGroupMemberTaskGroup.objects.create(
            gitlab_group=self.gitlab_group
        )
        self.task_model = models.AddGroupMemberTask.objects.create(
            owner=self.gitlab_user,
            task_group=self.task_group_model,
            username='username',
        )

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
        self.assertEqual(self.task_model.error_msg, None)
        self.assertNotEqual(self.task_model.new_user, None)
        self.assertEqual(self.task_model.status, self.task_model.SUCCEED)
