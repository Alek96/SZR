import unittest
from unittest import mock
from django.test import TestCase
from django.conf import settings

from GitLabApi import *
from GitLabApi.MockUrls import *
from GitLabApi.exceptions import *
from GitLabApi.objects import *
from core.tests.test_models import GitlabUserModelMethod
from core.models import GitlabUser

import gitlab
import json


class TestIntegrationGitLabApi(TestCase, GitlabUserModelMethod):

    def test_can_not_create_connection_if_access_token_is_not_provided(self):
        auth_user, social_auth = self.create_user_and_user_social_auth(extra_data={'id': 1})
        with self.assertRaises(RuntimeError):
            GitLabApi(auth_user.id)

    def test_can_create_connection(self):
        user, user_social_auth = self.create_user_and_user_social_auth()
        gitlab_user = GitlabUser.objects.get(user_social_auth=user_social_auth)

        gitlab_api = GitLabApi(user.id)
        self.assertIsInstance(gitlab_api._gitlab, gitlab.Gitlab)
        self.assertEqual(gitlab_api._gitlab.url, settings.SOCIAL_AUTH_GITLAB_API_URL)
        self.assertEqual(gitlab_api._gitlab.oauth_token, gitlab_user.get_access_token())


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
                self.assertNotEqual(body, None)
                body_dict = json.loads(body.decode("utf-8"))
                for key, value in args.items():
                    self.assertEqual(body_dict[key], value)

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
        def test_save_obj(self, **kwargs):
            content = self.get_save_content()

            with HTTMock(self.get_mock_save_url(**kwargs)):
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


class TestGitLabGroupsChildren(GitLabApiTestsCases.TestBase):
    _group_id = 1

    def setUp(self):
        super().setUp()
        mock_get_url = MockGroupsUrls().get_mock_get_url()
        with HTTMock(mock_get_url):
            self._gitlab_groups = self.gitlab_api.groups.get(self._group_id)


class TestGitLabGroupObjApi(TestGitLabGroupsChildren,
                            GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj, MockGroupObjUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_groups

    def test_save_obj(self, **kwargs):
        super().test_save_obj(args={'visibility': self._gitlab_api_mgr.visibility})


class TestGitLabGroupSubgroupApi(TestGitLabGroupsChildren,
                                 GitLabApiTestsCases.TestList, MockGroupSubgroupsUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_groups.subgroups


class TestGitLabGroupProjectsApi(TestGitLabGroupsChildren,
                                 GitLabApiTestsCases.TestList, MockGroupProjectsUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_groups.projects


class TestGitLabGroupMembersApi(TestGitLabGroupsChildren,
                                GitLabApiTestsCases.TestCRUD, MockGroupMembersUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_groups.members

    def get_create_args(self):
        return GitLabContent.get_new_group_member_args()

    def _test_all(self, **kwargs):
        content = self.get_all_content()

        with HTTMock(self.get_mock_all_url()):
            group_list = self._gitlab_api_mgr.all(**kwargs)
            self.assertGreater(len(group_list), 0)
            for group_info, group in zip(content, group_list):
                for key, value in group_info.items():
                    self.assertEqual(getattr(group, key), value)

    def test_all(self):
        self._test_all()

    def test_all_single_content_element(self):
        self._test_all(as_list=False)

    def test_external(self):
        content_list = self.get_list_content()
        content_all = self.get_all_content()

        with HTTMock(self.get_mock_all_url(), self.get_mock_list_url()):
            group_ext = self._gitlab_api_mgr.external()
            self.assertGreater(len(group_ext), 0)
            for group in group_ext:
                for content in content_list:
                    self.assertNotEqual(group.id, content['id'])


class TestGitLabGroupMemberObjApi(TestGitLabGroupsChildren,
                                  GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj,
                                  MockGroupMemberObjUrls):

    def setUp(self):
        super().setUp()
        mock_get_url = MockGroupMembersUrls().get_mock_get_url()
        with HTTMock(mock_get_url):
            self._gitlab_api_mgr = self._gitlab_groups.members.get(1)

    def test_save_obj(self, **kwargs):
        super().test_save_obj(args={'access_level': self._gitlab_api_mgr.access_level})


class TestGitLabUsersApi(GitLabApiTestsCases.TestCRUD, MockUsersUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.users

    def get_create_args(self):
        return GitLabContent.get_new_user_args()

    def test_get_user_with_username(self):
        content = self.get_get_content()

        with HTTMock(self.get_mock_list_url()):
            obj = self._gitlab_api_mgr.get(username=content['username'])
            self.assertTrue(obj)
            for key, value in content.items():
                self.assertEqual(getattr(obj, key), value)

    def test_get_user_with_username_does_not_exist(self):
        with self.assertRaises(GitlabGetError) as error:
            with mock.patch.object(self._gitlab_api_mgr, 'list', return_value=[]):
                obj = self._gitlab_api_mgr.get(username='username')
        self.assertEqual(error.exception.get_error_dict(), {"username": ["Does not exist"]})


class TestGitLabUserObjApi(GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj, MockUserObjUrls):
    _user_id = 1

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.users.get(self._user_id, lazy=True)

    def test_save_obj(self):
        with self.assertRaises(NotImplementedError):
            super().test_save_obj()


class TestGitLabProjectsApi(GitLabApiTestsCases.TestCRUD, MockProjectsUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.projects

    def get_create_args(self):
        return GitLabContent.get_new_project_args()


class TestGitLabProjectChildren(GitLabApiTestsCases.TestBase):
    _project_id = 1

    def setUp(self):
        super().setUp()
        mock_get_url = MockProjectsUrls().get_mock_get_url()
        with HTTMock(mock_get_url):
            self._gitlab_project = self.gitlab_api.projects.get(self._project_id)


class TestGitLabProjectObjApi(TestGitLabProjectChildren,
                              GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj, MockProjectObjUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_project

    def test_save_obj(self, **kwargs):
        super().test_save_obj(args={'visibility': self._gitlab_api_mgr.visibility})


class TestGitLabProjectMembersApi(TestGitLabProjectChildren,
                                  GitLabApiTestsCases.TestCRUD, MockProjectMembersUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_project.members

    def get_create_args(self):
        return GitLabContent.get_new_project_member_args()

    def _test_all(self, **kwargs):
        content = self.get_all_content()

        with HTTMock(self.get_mock_all_url()):
            project_list = self._gitlab_api_mgr.all(**kwargs)
            self.assertGreater(len(project_list), 0)
            for project_info, project in zip(content, project_list):
                for key, value in project_info.items():
                    self.assertEqual(getattr(project, key), value)

    def test_all(self):
        self._test_all()

    def test_all_single_content_element(self):
        self._test_all(as_list=False)

    def test_external(self):
        content_list = self.get_list_content()
        content_all = self.get_all_content()

        with HTTMock(self.get_mock_all_url(), self.get_mock_list_url()):
            project_ext = self._gitlab_api_mgr.external()
            self.assertGreater(len(project_ext), 0)
            for project in project_ext:
                for content in content_list:
                    self.assertNotEqual(project.id, content['id'])


class TestGitLabProjectMemberObjApi(TestGitLabProjectChildren,
                                    GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj,
                                    MockProjectMemberObjUrls):

    def setUp(self):
        super().setUp()
        mock_get_url = MockProjectMembersUrls().get_mock_get_url()
        with HTTMock(mock_get_url):
            self._gitlab_api_mgr = self._gitlab_project.members.get(1)

    def test_save_obj(self, **kwargs):
        super().test_save_obj(args={'access_level': self._gitlab_api_mgr.access_level})


class TestGitLabApi(GitLabApiTestsCases.TestBase):
    def test_inheritance(self):
        self.assertIsInstance(self.gitlab_api.groups, GroupManager)
        self.assertIsInstance(self.gitlab_api.users, UserManager)
        self.assertIsInstance(self.gitlab_api.projects, ProjectManager)
