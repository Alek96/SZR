import unittest
from unittest import mock
from django.test import TestCase

from GitLabApi.MockUrls import *
from GitLabApi.exceptions import *

import requests
import json


class MockUrlsTestsCases:
    class TestBase(unittest.TestCase, MockUrlBase):
        url_prefix = "{}://{}{}".format(MockUrlBase._scheme, MockUrlBase._netloc, MockUrlBase._path_prefix)

        def request_check(self, request, **kwargs):
            pass

        def _test_get_all_mock_urls(self):
            pass

        def test_get_all_mock_urls(self):
            with HTTMock(*self.get_all_mock_urls()):
                self._test_get_all_mock_urls()

    class TestList(TestBase, MockUrlList):

        def _test_list(self):
            url = self.get_list_url()
            resp = requests.get(url)
            resp_dict = json.loads(resp.content)
            self.assertEqual(resp_dict, self.get_list_content())

        def test_list(self):
            with HTTMock(self.get_mock_list_url()):
                self._test_list()

        def get_list_url(self):
            return "{}{}".format(self.url_prefix, self._path).replace('[0-9]+', '98')

    class TestGet(TestBase, MockUrlGet):
        def _test_get(self):
            url = self.get_get_url()
            resp = requests.get(url)
            resp_dict = json.loads(resp.content)
            self.assertEqual(resp_dict, self.get_get_content())

        def test_get(self):
            with HTTMock(self.get_mock_get_url()):
                self._test_get()

        def get_get_url(self):
            return "{}{}/76".format(self.url_prefix, self._path).replace('[0-9]+', '98')

    class TestCreate(TestBase, MockUrlCreate):
        def _test_create(self):
            url = self.get_create_url()
            resp = requests.post(url)
            resp_dict = json.loads(resp.content)
            self.assertEqual(resp_dict, self.get_create_content())

        def test_create(self):
            with HTTMock(self.get_mock_create_url()):
                self._test_create()

        def get_create_url(self):
            return "{}{}".format(self.url_prefix, self._path).replace('[0-9]+', '98')

    class TestDelete(TestBase, MockUrlDelete):
        def _test_delete(self):
            url = self.get_delete_url()
            resp = requests.delete(url)
            resp_dict = json.loads(resp.content)
            self.assertEqual(resp_dict, self.get_delete_content())

        def test_delete(self):
            with HTTMock(self.get_mock_delete_url()):
                self._test_delete()

        def get_delete_url(self):
            return "{}{}/76".format(self.url_prefix, self._path).replace('[0-9]+', '98')

    class TestCRUD(TestList, TestGet, TestCreate, TestDelete):
        pass

    class TestSaveObj(TestBase, MockUrlSave):
        def _test_save_obj(self):
            url = self.get_save_url()
            resp = requests.put(url)
            resp_dict = json.loads(resp.content)
            self.assertEqual(resp_dict, self.get_save_content())

        def test_save_obj(self):
            with HTTMock(self.get_mock_save_url()):
                self._test_save_obj()

        def get_save_url(self):
            return "{}{}/76".format(self.url_prefix, self._path).replace('[0-9]+', '98')

    class TestDeleteObj(TestBase, MockUrlDelete):
        def _test_delete_obj(self):
            url = self.get_delete_url()
            resp = requests.delete(url)
            resp_dict = json.loads(resp.content)
            self.assertEqual(resp_dict, self.get_delete_content())

        def test_delete_obj(self):
            with HTTMock(self.get_mock_delete_url()):
                self._test_delete_obj()

        def get_delete_url(self):
            return "{}{}/76".format(self.url_prefix, self._path).replace('[0-9]+', '98')


class TestMockUrlsTestsCases(MockUrlsTestsCases.TestCRUD,
                             MockUrlsTestsCases.TestSaveObj,
                             MockUrlsTestsCases.TestDeleteObj):
    pass


class TestMockGroupSubgroupUrls(MockUrlsTestsCases.TestList, MockGroupSubgroupsUrls):
    def _test_get_all_mock_urls(self):
        self._test_list()

    def test_get_all_mock_urls(self):
        with HTTMock(*self.get_all_mock_urls()):
            self._test_get_all_mock_urls()


class TestMockGroupProjectsUrls(MockUrlsTestsCases.TestList, MockGroupProjectsUrls):

    def _test_get_all_mock_urls(self):
        self._test_list()


class TestMockGroupMembersUrls(MockUrlsTestsCases.TestCRUD, MockGroupMembersUrls):

    def _test_all(self):
        url = self.get_all_url()
        resp = requests.get(url)
        resp_dict = json.loads(resp.content)
        self.assertEqual(resp_dict, self.get_all_content())

    def test_all(self):
        with HTTMock(self.get_mock_all_url()):
            self._test_all()

    def get_all_url(self):
        return "{}{}/all".format(self.url_prefix, self._path).replace('[0-9]+', '98')

    def _test_get_all_mock_urls(self):
        self._test_list()
        self._test_get()
        self._test_create()
        self._test_delete()
        self._test_all()


class TestMockGroupObjUrls(MockUrlsTestsCases.TestSaveObj, MockUrlsTestsCases.TestDeleteObj, MockGroupObjUrls):
    _test_mock_group_subgroups_url = TestMockGroupSubgroupUrls()
    _test_mock_group_projects_url = TestMockGroupProjectsUrls()
    _test_mock_group_members_url = TestMockGroupMembersUrls()

    def _test_get_all_mock_urls(self):
        self._test_save_obj()
        self._test_delete_obj()

        self._test_mock_group_subgroups_url._test_get_all_mock_urls()
        self._test_mock_group_projects_url._test_get_all_mock_urls()
        self._test_mock_group_members_url._test_get_all_mock_urls()


class TestMockGroupsUrls(MockUrlsTestsCases.TestCRUD, MockGroupsUrls):
    _test_mock_group_obj_urls = TestMockGroupObjUrls()

    def _test_get_all_mock_urls(self):
        self._test_list()
        self._test_get()
        self._test_create()
        self._test_delete()

        self._test_mock_group_obj_urls._test_get_all_mock_urls()


class TestMockUserObjUrls(MockUrlsTestsCases.TestSaveObj, MockUrlsTestsCases.TestDeleteObj, MockUserObjUrls):

    def _test_get_all_mock_urls(self):
        self._test_save_obj()
        self._test_delete_obj()


class TestMockUsersUrls(MockUrlsTestsCases.TestCRUD, MockUsersUrls):
    _test_mock_user_obj_urls = TestMockUserObjUrls()

    def _test_get_all_mock_urls(self):
        self._test_list()
        self._test_get()
        self._test_create()
        self._test_delete()

        self._test_mock_user_obj_urls._test_get_all_mock_urls()


class TestMockGitLabUrl(unittest.TestCase, MockGitLabUrl):
    _test_mock_groups_url = TestMockGroupsUrls()

    def test_external_url_raise_error(self):
        with self.assertRaises(NoMockedUrlError):
            with HTTMock(*self.get_all_mock_urls()):
                requests.get("http://cos")

    def _test_get_all_mock_urls(self):
        self._test_mock_groups_url._test_get_all_mock_urls()


class TestMockAllGitlabUrl(unittest.TestCase):

    def test_mock_all_gitlab_url(self):
        @mock_all_gitlab_url
        def all_urls():
            TestMockGitLabUrl()._test_get_all_mock_urls()
            return "ok"

        self.assertEqual(all_urls(), "ok")

    def test_mock_all_gitlab_url_parenthesis(self):
        @mock_all_gitlab_url()
        def all_urls():
            TestMockGitLabUrl()._test_get_all_mock_urls()
            return "ok"

        self.assertEqual(all_urls(), "ok")

    def test_mock_all_gitlab_url_raise_error(self):
        error = RuntimeError("error")

        @mock_all_gitlab_url(raise_error=error)
        def all_urls():
            TestMockGitLabUrl()._test_get_all_mock_urls()

        with self.assertRaises(RuntimeError):
            self.assertEqual(all_urls(), "ok")
