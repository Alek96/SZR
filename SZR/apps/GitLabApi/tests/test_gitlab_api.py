import unittest
from unittest import mock
from django.test import TestCase
from django.conf import settings

from GitLabApi import *
from GitLabApi.MockUrls import *
from core.tests.test_models import GitlabUserModelMethod
from core.models import GitlabUser

import gitlab
import json


class TestIntegrationGitLabApi(TestCase, GitlabUserModelMethod):

    def test_can_not_create_connection_if_access_token_is_not_provided(self):
        auth_user, social_auth = self.create_auth_user_and_social_auth(extra_data={'id': 1})
        with self.assertRaises(RuntimeError):
            GitLabApi(auth_user.id)

    def test_can_create_connection(self):
        auth_user, social_auth = self.create_auth_user_and_social_auth()
        user = GitlabUser.objects.get(social_auth=social_auth)

        gitlab_api = GitLabApi(auth_user.id)
        self.assertIsInstance(gitlab_api._gitlab, gitlab.Gitlab)
        self.assertEqual(gitlab_api._gitlab.url, settings.SOCIAL_AUTH_GITLAB_API_URL)
        self.assertEqual(gitlab_api._gitlab.oauth_token, user.get_access_token())


class GitLabApiTestsCases:
    class TestBase(unittest.TestCase, MockUrlBase):
        _gitlab_api_mgr = None

        def setUp(self):
            user_id = 1
            with mock.patch.object(GitLabApi, '_get_gitlab_connection',
                                   return_value=gitlab.Gitlab("{}://{}".format(self._scheme, self._netloc),
                                                              private_token="private_token")
                                   ) as mock_get_gitlab_connection:
                self.gitlab_api = GitLabApi(user_id)
            mock_get_gitlab_connection.assert_called_once_with(user_id)

        def request_check(self, request, args=None, **kwargs):
            super().request_check(request, **kwargs)
            body = request.body
            if not args:
                self.assertEqual(body, None)
            else:
                body_dcit = json.loads(body)
                for key, value in args.items():
                    self.assertEqual(body_dcit[key], value)

    class TestList(TestBase, MockUrlList):
        def test_list(self):
            content = self.get_list_content()

            with HTTMock(self.get_mock_list_url()):
                list = self._gitlab_api_mgr.list()
                self.assertGreater(len(list), 0)
                for cont, obj in zip(content, list):
                    for key, value in cont.items():
                        self.assertEqual(getattr(obj, key), value)

    class TestGet(TestBase, MockUrlGet):
        def test_get(self):
            content = self.get_get_content()

            with HTTMock(self.get_mock_get_url()):
                obj = self._gitlab_api_mgr.get(content['id'])
                self.assertTrue(obj)
                for key, value in content.items():
                    self.assertEqual(getattr(obj, key), value)

    class TestCreate(TestBase, MockUrlCreate):
        def test_create(self):
            args = self.get_create_args()
            content = self.get_create_content()

            with HTTMock(self.get_mock_create_url(args=args)):
                obj = self._gitlab_api_mgr.create(args)
                self.assertTrue(obj)
                for key, value in content.items():
                    self.assertEqual(getattr(obj, key), value)

        def get_create_args(self):
            return {}

    class TestDelete(TestBase, MockUrlDelete):
        def test_delete(self):
            id = 1
            with HTTMock(self.get_mock_delete_url()):
                self._gitlab_api_mgr.delete(id)

    class TestCRUD(TestList, TestGet, TestCreate, TestDelete):
        pass

    class TestSaveObj(TestBase, MockUrlSave):
        def test_save_obj(self):
            content = self.get_save_content()

            with HTTMock(self.get_mock_save_url()):
                obj = self._gitlab_api_mgr.save()
                self.assertFalse(obj)

    class TestDeleteObj(TestBase, MockUrlDelete):
        def test_delete_obj(self):
            with HTTMock(self.get_mock_delete_url()):
                self._gitlab_api_mgr.delete()


class TestGitLabGroupsApi(GitLabApiTestsCases.TestCRUD, MockGroupsUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.groups

    def get_create_args(self):
        return GitLabContent.get_new_group_args()

    def test_groups_get_roots(self):
        content = self.get_roots_content()

        with HTTMock(self.get_mock_list_url()):
            group_list = self.gitlab_api.groups.get_roots()
            self.assertGreater(len(group_list), 0)
            for group_info, group in zip(content, group_list):
                self.assertEqual(group.parent_id, None)
                for key, value in group_info.items():
                    self.assertEqual(getattr(group, key), value)


class TestGitLabGroupObjApi(GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj, MockGroupObjUrls):
    _group_id = 1

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.groups.get(self._group_id, lazy=True)


class TestGitLabGroupSubgroupApi(GitLabApiTestsCases.TestList, MockGroupSubgroupsUrls):
    _group_id = 1

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.groups.get(self._group_id, lazy=True).subgroups


class TestGitLabGroupProjectsApi(GitLabApiTestsCases.TestList, MockGroupProjectsUrls):
    _group_id = 1

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.groups.get(self._group_id, lazy=True).projects


class TestGitLabGroupMembersApi(GitLabApiTestsCases.TestCRUD, MockGroupMembersUrls):
    _group_id = 1

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.groups.get(self._group_id, lazy=True).members

    def get_create_args(self):
        return GitLabContent.get_new_member_args()

    def test_all(self):
        content = self.get_all_content()

        with HTTMock(self.get_mock_all_url()):
            group_list = self._gitlab_api_mgr.all()
            self.assertGreater(len(group_list), 0)
            for group_info, group in zip(content, group_list):
                for key, value in group_info.items():
                    self.assertEqual(getattr(group, key), value)

    def test_external(self):
        content_list = self.get_list_content()
        content_all = self.get_all_content()

        with HTTMock(self.get_mock_all_url(), self.get_mock_list_url()):
            group_ext = self._gitlab_api_mgr.external()
            self.assertGreater(len(group_ext), 0)
            for group in group_ext:
                for content in content_list:
                    self.assertNotEqual(group.id, content['id'])
