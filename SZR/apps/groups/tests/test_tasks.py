import unittest
from unittest import mock
from django.test import TestCase
from httmock import HTTMock
import json

from core.models import GitlabUser
from core.tests.test_view import LoginMethods
from core.tests.test_tasks import BaseTaskTests
from groups import models
from GitLabApi import mock_all_gitlab_url
from groups.tasks import *
from groups.tests.test_models import AddMemberCreateMethods, AddSubgroupCreateMethods
from GitLabApi.tests.test_gitlab_api import *


class CreateSubgroup(LoginMethods):
    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_create_user(self):
        args_dict = {
            'name': 'name',
            'path': 'path',
            'parent_id': 1,
        }

        with HTTMock(mock_all_urls_and_raise_error):
            with HTTMock(TestGitLabGroupsApi().get_mock_create_url(args=args_dict)):
                self.assertTrue(create_subgroup(
                    user_id=self.user.id,
                    name='name',
                    path='path',
                    group_id=1
                ))


class AddOrUpdateMemberTests(LoginMethods):
    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_update_user(self):
        with HTTMock(mock_all_urls_and_raise_error):
            with HTTMock(TestGitLabGroupsApi().get_mock_get_url()):
                with HTTMock(TestGitLabUsersApi().get_mock_list_url()):
                    with HTTMock(TestGitLabGroupMembersApi().get_mock_get_url()):
                        with HTTMock(TestGitLabGroupMemberObjApi().get_mock_save_url(args={'access_level': 10})):
                            self.assertTrue(add_or_update_member(
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
                            self.assertTrue(add_or_update_member(
                                user_id=self.user.id,
                                group_id=1,
                                username='name',
                                access_level=10
                            ))


class AddSubgroupTaskTests(LoginMethods):
    @LoginMethods.create_user_wrapper
    def setUp(self):
        self.task_model = AddSubgroupCreateMethods().create_task(
            owner=GitlabUser.objects.get(user_social_auth=self.user_social_auth)
        )
        self.gitlab_group = self.task_model.task_group.gitlab_group

    def get_run_args(self):
        return json.loads(self.task_model.celery_task.kwargs)

    @mock_all_gitlab_url
    def test_gitlab_group_does_not_have_gitlab_id(self):
        self.gitlab_group.gitlab_id = None
        self.gitlab_group.save()

        AddSubgroupTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.assertEqual(self.task_model.status, self.task_model.FAILED)
        self.assertNotEqual(self.task_model.error_msg, "")

    @mock_all_gitlab_url
    def test_run_correctly(self):
        self.gitlab_group.gitlab_id = 2
        self.gitlab_group.save()

        AddSubgroupTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.task_model.new_gitlab_group.refresh_from_db()
        self.assertEqual(self.task_model.error_msg, None)
        self.assertNotEqual(self.task_model.new_gitlab_group.gitlab_id, None)
        self.assertEqual(self.task_model.status, self.task_model.SUCCEED)


class AddMemberTaskTests(LoginMethods):

    @LoginMethods.create_user_wrapper
    def setUp(self):
        self.task_model = AddMemberCreateMethods().create_task(
            owner=GitlabUser.objects.get(user_social_auth=self.user_social_auth)
        )
        self.gitlab_group = self.task_model.task_group.gitlab_group

    def get_run_args(self):
        return json.loads(self.task_model.celery_task.kwargs)

    @mock_all_gitlab_url
    def test_gitlab_group_does_not_have_gitlab_id(self):
        self.gitlab_group.gitlab_id = None
        self.gitlab_group.save()

        AddMemberTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.assertEqual(self.task_model.status, self.task_model.FAILED)
        self.assertNotEqual(self.task_model.error_msg, "")

    @mock_all_gitlab_url
    def test_run_correctly(self):
        self.gitlab_group.gitlab_id = 1
        self.gitlab_group.save()

        AddMemberTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.assertEqual(self.task_model.error_msg, None)
        self.assertNotEqual(self.task_model.new_gitlab_user, None)
        self.assertEqual(self.task_model.status, self.task_model.SUCCEED)
