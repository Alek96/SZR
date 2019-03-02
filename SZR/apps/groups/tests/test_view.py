import unittest

from django.urls import reverse, resolve
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.tests.test_view import SimpleUrlsTestsCases
from authentication.tests.test_view import LoginMethods
from GitLabApi import mock_all_gitlab_url


class GitlabWrapperAppNameCase:
    class GitlabWrapperAppNameTest(SimpleUrlsTestsCases.SimpleUrlsTests, LoginMethods):
        app_name = 'groups'


class GroupIndexPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'index'

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/groups_index.html')
        self.assertIn('group_list', response.context)


class GroupDetailIndexPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'group_detail_index'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/group_detail_index.html')
        self.assertIn('group', response.context)


class GroupMembersIndexPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'group_members'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/group_detail_members.html')
        self.assertIn('group', response.context)
