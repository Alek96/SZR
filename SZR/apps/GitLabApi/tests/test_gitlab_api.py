import json
import unittest
from unittest import mock

import gitlab
from GitLabApi import *
from GitLabApi import GitLabContent
from GitLabApi import MockUrls
from GitLabApi.exceptions import GitlabGetError
from GitLabApi.objects import GroupManager, UserManager, ProjectManager
from core.models import GitlabUser
from core.tests.test_models import GitlabUserModelMethod
from django.conf import settings
from django.test import TestCase
from httmock import HTTMock


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
    class TestBase(unittest.TestCase, MockUrls.MockUrlBase):
        _gitlab_api_mgr = None

        def setUp(self):
            user_id = 1
            with mock.patch.object(GitLabApi, '_get_gitlab_connection',
                                   return_value=gitlab.Gitlab("{}://{}".format(self.scheme, self.netloc),
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

    class TestList(TestBase, MockUrls.MockUrlList):
        def test_list(self):
            content = self.list_content

            with HTTMock(self.get_mock_for_list_url()):
                list = self._gitlab_api_mgr.list()
                self.assertGreater(len(list), 0)
                for cont, obj in zip(content, list):
                    for key, value in cont.items():
                        self.assertEqual(getattr(obj, key), value)

    class TestGet(TestBase, MockUrls.MockUrlGet):
        def test_get(self):
            content = self.get_content

            with HTTMock(self.get_mock_for_get_url()):
                obj = self._gitlab_api_mgr.get(content['id'])
                self.assertTrue(obj)
                for key, value in content.items():
                    self.assertEqual(getattr(obj, key), value)

    class TestCreate(TestBase, MockUrls.MockUrlCreate):
        def test_create(self):
            args = self.get_create_args()
            content = self.create_content

            with HTTMock(self.get_mock_for_create_url(args=args)):
                obj = self._gitlab_api_mgr.create(args)
                self.assertTrue(obj)
                for key, value in content.items():
                    self.assertEqual(getattr(obj, key), value)

        def get_create_args(self):
            return {}

    class TestDelete(TestBase, MockUrls.MockUrlDelete):
        def test_delete(self):
            id = 1
            with HTTMock(self.get_mock_for_delete_url()):
                self._gitlab_api_mgr.delete(id)

    class TestCRUD(TestList, TestGet, TestCreate, TestDelete):
        pass

    class TestAll(TestBase, MockUrls.MockUrlAll):
        def _test_all(self, **kwargs):
            content = self.all_content

            with HTTMock(self.get_mock_for_all_url()):
                member_list = self._gitlab_api_mgr.all(**kwargs)
                self.assertGreater(len(member_list), 0)
                for member_info, member in zip(content, member_list):
                    for key, value in member_info.items():
                        self.assertEqual(getattr(member, key), value)

        def test_all(self):
            self._test_all()

        def test_all_single_content_element(self):
            self._test_all(as_list=False)

    class TestSaveObj(TestBase, MockUrls.MockUrlSave):
        def test_save_obj(self, **kwargs):
            content = self.save_content

            with HTTMock(self.get_mock_for_save_url(**kwargs)):
                obj = self._gitlab_api_mgr.save()
                self.assertFalse(obj)

    class TestDeleteObj(TestBase, MockUrls.MockUrlDelete):
        def test_delete_obj(self):
            with HTTMock(self.get_mock_for_delete_url()):
                self._gitlab_api_mgr.delete()


class TestGitLabGroupsApi(GitLabApiTestsCases.TestCRUD, MockUrls.MockGroupsUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.groups

    def get_create_args(self):
        return GitLabContent.get_new_group_args()

    def test_groups_get_roots(self):
        content = self.roots_content

        with HTTMock(self.get_mock_for_list_url()):
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
        mock_get_url = MockUrls.MockGroupsUrls().get_mock_for_get_url()
        with HTTMock(mock_get_url):
            self._gitlab_groups = self.gitlab_api.groups.get(self._group_id)


class TestGitLabGroupObjApi(TestGitLabGroupsChildren,
                            GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj,
                            MockUrls.MockGroupObjUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_groups

    def test_save_obj(self, **kwargs):
        super().test_save_obj(args={'visibility': self._gitlab_api_mgr.visibility})


class TestGitLabGroupSubgroupApi(TestGitLabGroupsChildren,
                                 GitLabApiTestsCases.TestList, MockUrls.MockGroupSubgroupsUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_groups.subgroups


class TestGitLabGroupProjectsApi(TestGitLabGroupsChildren,
                                 GitLabApiTestsCases.TestList, MockUrls.MockGroupProjectsUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_groups.projects


class TestGitLabGroupMembersApi(TestGitLabGroupsChildren,
                                GitLabApiTestsCases.TestCRUD, GitLabApiTestsCases.TestAll,
                                MockUrls.MockGroupMembersUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_groups.members

    def get_create_args(self):
        return GitLabContent.get_new_group_member_args()

    def test_external(self):
        content_list = self.list_content
        content_all = self.all_content

        with HTTMock(self.get_mock_for_all_url(), self.get_mock_for_list_url()):
            group_ext = self._gitlab_api_mgr.external()
            self.assertGreater(len(group_ext), 0)
            for group in group_ext:
                for content in content_list:
                    self.assertNotEqual(group.id, content['id'])


class TestGitLabGroupMemberObjApi(TestGitLabGroupsChildren,
                                  GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj,
                                  MockUrls.MockGroupMemberObjUrls):

    def setUp(self):
        super().setUp()
        mock_get_url = MockUrls.MockGroupMembersUrls().get_mock_for_get_url()
        with HTTMock(mock_get_url):
            self._gitlab_api_mgr = self._gitlab_groups.members.get(1)

    def test_save_obj(self, **kwargs):
        super().test_save_obj(args={'access_level': self._gitlab_api_mgr.access_level})


class TestGitLabUsersApi(GitLabApiTestsCases.TestCRUD, MockUrls.MockUsersUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.users

    def get_create_args(self):
        return GitLabContent.get_new_user_args()

    def test_get_user_with_username(self):
        content = self.get_content

        with HTTMock(self.get_mock_for_list_url()):
            obj = self._gitlab_api_mgr.get(username=content['username'])
            self.assertTrue(obj)
            for key, value in content.items():
                self.assertEqual(getattr(obj, key), value)

    def test_get_user_with_username_does_not_exist(self):
        with self.assertRaises(GitlabGetError) as error:
            with mock.patch.object(self._gitlab_api_mgr, 'list', return_value=[]):
                obj = self._gitlab_api_mgr.get(username='username')
        self.assertEqual(error.exception.get_error_dict(), {"username": ["Does not exist"]})


class TestGitLabUserObjApi(GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj,
                           MockUrls.MockUserObjUrls):
    _user_id = 1

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.users.get(self._user_id, lazy=True)

    def test_save_obj(self):
        with self.assertRaises(NotImplementedError):
            super().test_save_obj()


class TestGitLabProjectsApi(GitLabApiTestsCases.TestCRUD, MockUrls.MockProjectsUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self.gitlab_api.projects

    def get_create_args(self):
        return GitLabContent.get_new_project_args()


class TestGitLabProjectChildren(GitLabApiTestsCases.TestBase):
    _project_id = 1

    def setUp(self):
        super().setUp()
        mock_get_url = MockUrls.MockProjectsUrls().get_mock_for_get_url()
        with HTTMock(mock_get_url):
            self._gitlab_project = self.gitlab_api.projects.get(self._project_id)


class TestGitLabProjectObjApi(TestGitLabProjectChildren,
                              GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj,
                              MockUrls.MockProjectObjUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_project

    def test_save_obj(self, **kwargs):
        super().test_save_obj(args={'visibility': self._gitlab_api_mgr.visibility})


class TestGitLabProjectMembersApi(TestGitLabProjectChildren,
                                  GitLabApiTestsCases.TestCRUD, GitLabApiTestsCases.TestAll,
                                  MockUrls.MockProjectMembersUrls):

    def setUp(self):
        super().setUp()
        self._gitlab_api_mgr = self._gitlab_project.members

    def get_create_args(self):
        return GitLabContent.get_new_project_member_args()

    def test_external(self):
        content_list = self.list_content
        content_all = self.all_content

        with HTTMock(self.get_mock_for_all_url(), self.get_mock_for_list_url()):
            project_ext = self._gitlab_api_mgr.external()
            self.assertGreater(len(project_ext), 0)
            for project in project_ext:
                for content in content_list:
                    self.assertNotEqual(project.id, content['id'])


class TestGitLabProjectMemberObjApi(TestGitLabProjectChildren,
                                    GitLabApiTestsCases.TestSaveObj, GitLabApiTestsCases.TestDeleteObj,
                                    MockUrls.MockProjectMemberObjUrls):

    def setUp(self):
        super().setUp()
        mock_get_url = MockUrls.MockProjectMembersUrls().get_mock_for_get_url()
        with HTTMock(mock_get_url):
            self._gitlab_api_mgr = self._gitlab_project.members.get(1)

    def test_save_obj(self, **kwargs):
        super().test_save_obj(args={'access_level': self._gitlab_api_mgr.access_level})


class TestGitLabApi(GitLabApiTestsCases.TestBase):
    def test_inheritance(self):
        self.assertIsInstance(self.gitlab_api.groups, GroupManager)
        self.assertIsInstance(self.gitlab_api.users, UserManager)
        self.assertIsInstance(self.gitlab_api.projects, ProjectManager)
