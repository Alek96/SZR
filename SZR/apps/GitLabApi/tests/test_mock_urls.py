import json
import unittest

import requests
from GitLabApi import MockUrls
from GitLabApi.exceptions import NoMockedUrlError
from httmock import HTTMock


class MockUrlsTestsCases:
    class TestBase(unittest.TestCase, MockUrls.MockUrlBase):
        url_prefix = "{}://{}{}".format(MockUrls.MockUrlBase.scheme, MockUrls.MockUrlBase.netloc,
                                        MockUrls.MockUrlBase.path_prefix)

        def request_check(self, request, **kwargs):
            pass

        def _test_get_all_mock_urls(self):
            pass

        def test_get_all_mock_urls(self):
            with HTTMock(*self.get_all_mocked_urls()):
                self._test_get_all_mock_urls()

    class TestList(TestBase, MockUrls.MockUrlList):

        def _test_list(self):
            url = self.get_list_url()
            resp = requests.get(url)
            resp_dict = json.loads(str(resp.content, 'utf-8'))
            self.assertEqual(resp_dict, self.list_content)

        def test_list(self):
            with HTTMock(self.get_mock_for_list_url()):
                self._test_list()

        def get_list_url(self):
            return "{}{}".format(self.url_prefix, self.path).replace('[0-9]+', '98')

    class TestGet(TestBase, MockUrls.MockUrlGet):
        def _test_get(self):
            url = self.get_get_url()
            resp = requests.get(url)
            resp_dict = json.loads(str(resp.content, 'utf-8'))
            self.assertEqual(resp_dict, self.get_content)

        def test_get(self):
            with HTTMock(self.get_mock_for_get_url()):
                self._test_get()

        def get_get_url(self):
            return "{}{}/76".format(self.url_prefix, self.path).replace('[0-9]+', '98')

    class TestCreate(TestBase, MockUrls.MockUrlCreate):
        def _test_create(self):
            url = self.get_create_url()
            resp = requests.post(url)
            resp_dict = json.loads(str(resp.content, 'utf-8'))
            self.assertEqual(resp_dict, self.create_content)

        def test_create(self):
            with HTTMock(self.get_mock_for_create_url()):
                self._test_create()

        def get_create_url(self):
            return "{}{}".format(self.url_prefix, self.path).replace('[0-9]+', '98')

    class TestDelete(TestBase, MockUrls.MockUrlDelete):
        def _test_delete(self):
            url = self.get_delete_url()
            resp = requests.delete(url)
            resp_dict = json.loads(str(resp.content, 'utf-8'))
            self.assertEqual(resp_dict, self.delete_content)

        def test_delete(self):
            with HTTMock(self.get_mock_for_delete_url()):
                self._test_delete()

        def get_delete_url(self):
            return "{}{}/76".format(self.url_prefix, self.path).replace('[0-9]+', '98')

    class TestAll(TestBase, MockUrls.MockUrlAll):

        def _test_all(self):
            url = self.get_all_url()
            resp = requests.get(url)
            resp_dict = json.loads(str(resp.content, 'utf-8'))
            self.assertEqual(resp_dict, self.all_content)

        def test_all(self):
            with HTTMock(self.get_mock_for_all_url()):
                self._test_all()

        def get_all_url(self):
            return "{}{}/all".format(self.url_prefix, self.path).replace('[0-9]+', '98')

    class TestCRUD(TestList, TestGet, TestCreate, TestDelete):
        pass

    class TestSaveObj(TestBase, MockUrls.MockUrlSave):
        def _test_save_obj(self):
            url = self.get_save_url()
            resp = requests.put(url)
            resp_dict = json.loads(str(resp.content, 'utf-8'))
            self.assertEqual(resp_dict, self.save_content)

        def test_save_obj(self):
            with HTTMock(self.get_mock_for_save_url()):
                self._test_save_obj()

        def get_save_url(self):
            return "{}{}/76".format(self.url_prefix, self.path).replace('[0-9]+', '98')

    class TestDeleteObj(TestBase, MockUrls.MockUrlDelete):
        def _test_delete_obj(self):
            url = self.get_delete_url()
            resp = requests.delete(url)
            resp_dict = json.loads(str(resp.content, 'utf-8'))
            self.assertEqual(resp_dict, self.delete_content)

        def test_delete_obj(self):
            with HTTMock(self.get_mock_for_delete_url()):
                self._test_delete_obj()

        def get_delete_url(self):
            return "{}{}/76".format(self.url_prefix, self.path).replace('[0-9]+', '98')


class TestMockUrlsTestsCases(MockUrlsTestsCases.TestCRUD,
                             MockUrlsTestsCases.TestSaveObj,
                             MockUrlsTestsCases.TestDeleteObj):
    pass


class TestMockGroupSubgroupUrls(MockUrlsTestsCases.TestList, MockUrls.MockGroupSubgroupsUrls):
    def _test_get_all_mock_urls(self):
        self._test_list()

    def test_get_all_mock_urls(self):
        with HTTMock(*self.get_all_mocked_urls()):
            self._test_get_all_mock_urls()


class TestMockGroupProjectsUrls(MockUrlsTestsCases.TestList, MockUrls.MockGroupProjectsUrls):

    def _test_get_all_mock_urls(self):
        self._test_list()


class TestMockGroupMemberObjUrls(MockUrlsTestsCases.TestSaveObj, MockUrlsTestsCases.TestDeleteObj,
                                 MockUrls.MockGroupMemberObjUrls):

    def _test_get_all_mock_urls(self):
        self._test_save_obj()
        self._test_delete_obj()


class TestMockGroupMembersUrls(MockUrlsTestsCases.TestCRUD, MockUrlsTestsCases.TestAll, MockUrls.MockGroupMembersUrls):
    _test_mock_group_member_obj_urls = TestMockGroupMemberObjUrls()

    def _test_get_all_mock_urls(self):
        self._test_list()
        self._test_get()
        self._test_create()
        self._test_delete()
        self._test_all()

        self._test_mock_group_member_obj_urls._test_get_all_mock_urls()


class TestMockGroupObjUrls(MockUrlsTestsCases.TestSaveObj, MockUrlsTestsCases.TestDeleteObj, MockUrls.MockGroupObjUrls):
    _test_mock_group_subgroups_url = TestMockGroupSubgroupUrls()
    _test_mock_group_projects_url = TestMockGroupProjectsUrls()
    _test_mock_group_members_url = TestMockGroupMembersUrls()

    def _test_get_all_mock_urls(self):
        self._test_save_obj()
        self._test_delete_obj()

        self._test_mock_group_subgroups_url._test_get_all_mock_urls()
        self._test_mock_group_projects_url._test_get_all_mock_urls()
        self._test_mock_group_members_url._test_get_all_mock_urls()


class TestMockGroupsUrls(MockUrlsTestsCases.TestCRUD, MockUrls.MockGroupsUrls):
    _test_mock_group_obj_urls = TestMockGroupObjUrls()

    def _test_get_all_mock_urls(self):
        self._test_list()
        self._test_get()
        self._test_create()
        self._test_delete()

        self._test_mock_group_obj_urls._test_get_all_mock_urls()


class TestMockUserObjUrls(MockUrlsTestsCases.TestSaveObj, MockUrlsTestsCases.TestDeleteObj, MockUrls.MockUserObjUrls):

    def _test_get_all_mock_urls(self):
        self._test_save_obj()
        self._test_delete_obj()


class TestMockUsersUrls(MockUrlsTestsCases.TestCRUD, MockUrls.MockUsersUrls):
    _test_mock_user_obj_urls = TestMockUserObjUrls()

    def _test_get_all_mock_urls(self):
        self._test_list()
        self._test_get()
        self._test_create()
        self._test_delete()

        self._test_mock_user_obj_urls._test_get_all_mock_urls()


class TestMockProjectMemberObjUrls(MockUrlsTestsCases.TestSaveObj, MockUrlsTestsCases.TestDeleteObj,
                                   MockUrls.MockProjectMemberObjUrls):

    def _test_get_all_mock_urls(self):
        self._test_save_obj()
        self._test_delete_obj()


class TestMockProjectMembersUrls(MockUrlsTestsCases.TestCRUD, MockUrlsTestsCases.TestAll,
                                 MockUrls.MockProjectMembersUrls):
    _test_mock_project_member_obj_urls = TestMockProjectMemberObjUrls()

    def _test_get_all_mock_urls(self):
        self._test_list()
        self._test_get()
        self._test_create()
        self._test_delete()
        self._test_all()

        self._test_mock_project_member_obj_urls._test_get_all_mock_urls()


class TestMockProjectObjUrls(MockUrlsTestsCases.TestSaveObj, MockUrlsTestsCases.TestDeleteObj,
                             MockUrls.MockProjectObjUrls):
    _test_mock_project_members_url = TestMockProjectMembersUrls()

    def _test_get_all_mock_urls(self):
        self._test_save_obj()
        self._test_delete_obj()

        self._test_mock_project_members_url._test_get_all_mock_urls()


class TestMockProjectsUrls(MockUrlsTestsCases.TestCRUD, MockUrls.MockProjectsUrls):
    _test_mock_project_obj_urls = TestMockProjectObjUrls()

    def _test_get_all_mock_urls(self):
        self._test_list()
        self._test_get()
        self._test_create()
        self._test_delete()

        self._test_mock_project_obj_urls._test_get_all_mock_urls()


class TestMockGitLabUrl(unittest.TestCase, MockUrls.MockGitLabUrl):
    _test_mock_groups_url = TestMockGroupsUrls()
    _test_mock_users_url = TestMockUsersUrls()
    _test_mock_projects_url = TestMockProjectsUrls()

    def test_external_url_raise_error(self):
        with self.assertRaises(NoMockedUrlError):
            with HTTMock(*self.get_all_mocked_urls()):
                requests.get("http://sth")

    def _test_get_all_mock_urls(self):
        self._test_mock_groups_url._test_get_all_mock_urls()
        self._test_mock_users_url._test_get_all_mock_urls()
        self._test_mock_projects_url._test_get_all_mock_urls()


class TestMockAllGitlabUrl(unittest.TestCase):

    def test_mock_all_gitlab_url(self):
        @MockUrls.mock_all_gitlab_url
        def all_urls():
            TestMockGitLabUrl()._test_get_all_mock_urls()
            return "ok"

        self.assertEqual(all_urls(), "ok")

    def test_mock_all_gitlab_url_parenthesis(self):
        @MockUrls.mock_all_gitlab_url()
        def all_urls():
            TestMockGitLabUrl()._test_get_all_mock_urls()
            return "ok"

        self.assertEqual(all_urls(), "ok")

    def test_mock_all_gitlab_url_raise_error(self):
        error = RuntimeError("error")

        @MockUrls.mock_all_gitlab_url(raise_error=error)
        def all_urls():
            TestMockGitLabUrl()._test_get_all_mock_urls()

        with self.assertRaises(RuntimeError):
            self.assertEqual(all_urls(), "ok")
