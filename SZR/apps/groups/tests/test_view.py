import unittest

from django.urls import reverse, resolve
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.tests.test_view import SimpleUrlsTestsCases
from core.tests.test_view import LoginMethods
from GitLabApi import objects
from groups.tests.test_forms import *


class GitlabWrapperAppNameCase:
    class GitlabWrapperAppNameTest(SimpleUrlsTestsCases.SimpleUrlsTests):
        app_name = 'groups'


class InitSidebarPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'init_sidebar'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/sidebar.html')

        self.assertIn('group', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)


class IndexPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'index'

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/index.html')

        self.assertIn('group_list', response.context)
        all(self.assertIsInstance(group, objects.Group) for group in response.context['group_list'])


class DetailPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'detail'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/detail.html')

        self.assertIn('group', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)


class MembersPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'members'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/members.html')

        self.assertIn('group', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)


class TasksPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'tasks'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/tasks.html')

        self.assertIn('group', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIn('finished_task_list', response.context)
        self.assertIn('new_group_links', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)
        self.assertIsInstance(response.context['unfinished_task_list'], list)
        self.assertIsInstance(response.context['finished_task_list'], list)
        self.assertIsInstance(response.context['new_group_links'], list)

        new_group_links = [
            ('New Subgroup Group', reverse('groups:new_subgroup_group', kwargs=self.args)),
            ('New Member Group', reverse('groups:new_member_group', kwargs=self.args))
        ]
        for group_link in response.context['new_group_links']:
            self.assertIn(group_link, new_group_links)


class NewGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_group'

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), AddSubgroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:index'))


class NewSubgroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_subgroup'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), AddSubgroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:detail', args=(self.args['group_id'],)))


class NewSubgroupGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_subgroup_group'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), AddMemberGroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:tasks', args=(self.args['group_id'],)))


class EditSubgroupGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'edit_subgroup_group'
    args = {'task_group_id': 1}

    def setUp(self):
        super().setUp()
        self.task_group = AddSubgroupCreateMethods().create_task_group(
            gitlab_group=models.GitlabGroup.objects.create(gitlab_id=42)
        )
        self.args['task_group_id'] = self.task_group.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_group_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        data = self.client.get(self.get_url()).context['form'].initial
        self.assertEqual(data['name'], self.task_group.name)
        data['name'] = 'Another Name'

        response = self.client.post(self.get_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.task_group.link_to_tasks_page)
        self.task_group.refresh_from_db()
        self.assertEqual(self.task_group.name, data['name'])


class NewSubgroupTaskPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_subgroup_task'
    args = {'group_id': 42, 'task_group_id': 1}

    def setUp(self):
        super().setUp()
        self.task_group = AddSubgroupCreateMethods().create_task_group(
            gitlab_group=models.GitlabGroup.objects.create(gitlab_id=self.args['group_id'])
        )
        self.args['task_group_id'] = self.task_group.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_group_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), AddSubgroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:tasks', args=(self.args['group_id'],)))


class EditSubgroupTaskPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'edit_subgroup_task'
    args = {'task_id': 1}

    def setUp(self):
        super().setUp()
        self.task = AddSubgroupCreateMethods().create_task(
            task_group=AddSubgroupCreateMethods().create_task_group(
                gitlab_group=models.GitlabGroup.objects.create(gitlab_id=42)))
        self.args['task_id'] = self.task.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        data = self.client.get(self.get_url()).context['form'].initial
        self.assertEqual(data['name'], self.task.name)
        data['name'] = 'Another Name'
        data['description'] = 'Description'

        response = self.client.post(self.get_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.task.link_to_tasks_page)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, data['name'])
        self.assertEqual(self.task.description, data['description'])


class NewMemberPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_member'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), AddMemberFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:members', args=(self.args['group_id'],)))


class NewMemberGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_member_group'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), AddMemberGroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:tasks', args=(self.args['group_id'],)))


class EditMemberGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'edit_member_group'
    args = {'task_group_id': 1}

    def setUp(self):
        super().setUp()
        self.task_group = AddMemberCreateMethods().create_task_group(
            gitlab_group=models.GitlabGroup.objects.create(gitlab_id=42)
        )
        self.args['task_group_id'] = self.task_group.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_group_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        data = self.client.get(self.get_url()).context['form'].initial
        self.assertEqual(data['name'], self.task_group.name)
        data['name'] = 'Another Name'

        response = self.client.post(self.get_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.task_group.link_to_tasks_page)
        self.task_group.refresh_from_db()
        self.assertEqual(self.task_group.name, data['name'])


class NewMemberTaskPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_member_task'
    args = {'group_id': 1, 'task_group_id': 1}

    def setUp(self):
        super().setUp()
        self.task_group = AddMemberCreateMethods().create_task_group(
            gitlab_group=models.GitlabGroup.objects.create(gitlab_id=self.args['group_id'])
        )
        self.args['task_group_id'] = self.task_group.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_group_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), AddMemberFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:tasks', args=(self.args['group_id'],)))


class EditMemberTaskPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'edit_member_task'
    args = {'task_id': 1}

    def setUp(self):
        super().setUp()
        self.task = AddMemberCreateMethods().create_task(
            task_group=AddMemberCreateMethods().create_task_group(
                gitlab_group=models.GitlabGroup.objects.create(gitlab_id=42)))
        self.args['task_id'] = self.task.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        data = self.client.get(self.get_url()).context['form'].initial
        self.assertEqual(data['username'], self.task.username)
        data['username'] = 'Another username'

        response = self.client.post(self.get_url(), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.task.link_to_tasks_page)
        self.task.refresh_from_db()
        self.assertEqual(self.task.username, data['username'])


class AjaxLoadSubgroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'ajax_load_subgroups'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/ajax/load_subgroups_and_projects.html')

        self.assertIn('group_list', response.context)
        self.assertIsInstance(response.context['group_list'], list)
        all(self.assertIsInstance(group, objects.GroupSubgroup) for group in response.context['group_list'])

        self.assertIn('project_list', response.context)
        self.assertEqual(response.context['project_list'], [])


class AjaxLoadSubgroupAndProjectsPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'ajax_load_subgroups_and_projects'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/ajax/load_subgroups_and_projects.html')

        self.assertIn('group_list', response.context)
        self.assertIsInstance(response.context['group_list'], list)
        all(self.assertIsInstance(group, objects.GroupSubgroup) for group in response.context['group_list'])

        self.assertIn('project_list', response.context)
        all(self.assertIsInstance(project, objects.GroupProject) for project in response.context['project_list'])
