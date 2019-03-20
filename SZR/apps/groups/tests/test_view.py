import unittest

from django.urls import reverse, resolve
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.tests.test_view import SimpleUrlsTestsCases
from core.tests.test_view import LoginMethods
from GitLabApi import mock_all_gitlab_url
from GitLabApi import objects
from groups.tests.test_forms import *


class GitlabWrapperAppNameCase:
    class GitlabWrapperAppNameTest(SimpleUrlsTestsCases.SimpleUrlsTests):
        app_name = 'groups'


class InitSidebarPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'init_sidebar'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/sidebar.html')

        self.assertIn('group', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)


class IndexPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'index'

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/index.html')

        self.assertIn('group_list', response.context)
        all(self.assertIsInstance(group, objects.Group) for group in response.context['group_list'])


class GroupDetailPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'group_detail'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/group_detail.html')

        self.assertIn('group', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)


class GroupMembersPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'group_members'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/group_members.html')

        self.assertIn('group', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)


class AjaxLoadSubgroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'ajax_load_subgroups'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/ajax_load_subgroups_and_projects.html')

        self.assertIn('group_list', response.context)
        self.assertIsInstance(response.context['group_list'], list)
        all(self.assertIsInstance(group, objects.GroupSubgroup) for group in response.context['group_list'])

        self.assertIn('project_list', response.context)
        self.assertEqual(response.context['project_list'], [])


class AjaxLoadSubgroupAndProjectsPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'ajax_load_subgroups_and_projects'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/ajax_load_subgroups_and_projects.html')

        self.assertIn('group_list', response.context)
        self.assertIsInstance(response.context['group_list'], list)
        all(self.assertIsInstance(group, objects.GroupSubgroup) for group in response.context['group_list'])

        self.assertIn('project_list', response.context)
        all(self.assertIsInstance(project, objects.GroupProject) for project in response.context['project_list'])


class NewGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_group'

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), GroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:index'))


class NewSubgroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_subgroup'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), GroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:group_detail', args=(self.args['group_id'],)))


class NewGroupMemberPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_group_member'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), GroupMemberFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:group_members', args=(self.args['group_id'],)))


class GroupTasksPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'group_tasks'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    @mock_all_gitlab_url
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/group_tasks.html')

        self.assertIn('group', response.context)
        self.assertIn('tasks', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)
        self.assertIsInstance(response.context['tasks'], list)


class NewAddGroupMemberTaskGroupTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_add_group_member_task_group'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), GroupMemberGroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:group_tasks', args=(self.args['group_id'],)))


class NewAddGroupMemberTaskTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_add_group_member_task'
    args = {'group_id': 1, 'task_group_id': 1}

    def setUp(self):
        super().setUp()
        gitlab_group = models.GitlabGroup.objects.create(gitlab_id=self.args['group_id'])
        self.args['task_group_id'] = gitlab_group.id
        self.group_task = models.AddGroupMemberTaskGroup.objects.create(
            gitlab_group=gitlab_group
        )

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_group_id'] = self.args['task_group_id'] + 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_template.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), GroupMemberFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:group_tasks', args=(self.args['group_id'],)))
