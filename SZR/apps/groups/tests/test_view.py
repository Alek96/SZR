from GitLabApi import objects
from core.tests.test_view import LoginMethods
from core.tests.test_view import SimpleUrlsTestsCases
from django.db.models import QuerySet
from django.urls import reverse
from groups import models
from groups.sidebar import GroupSidebar, FutureGroupSidebar
from groups.tests import test_forms
from groups.tests import test_models


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
        self.assertTemplateUsed(response, 'sidebar.html')

        self.assertIn('group', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)
        self.assertIsInstance(response.context['sidebar'], GroupSidebar)


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
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)
        self.assertIsInstance(response.context['sidebar'], GroupSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], QuerySet)


class MembersPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'members'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/members.html')

        self.assertIn('group', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)
        self.assertIsInstance(response.context['sidebar'], GroupSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], QuerySet)


class TasksPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'tasks'
    args = {'group_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/tasks.html')

        self.assertIn('group', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIn('finished_task_list', response.context)
        self.assertIn('new_group_links', response.context)
        self.assertIsInstance(response.context['group'], objects.Group)
        self.assertIsInstance(response.context['sidebar'], GroupSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], list)
        self.assertIsInstance(response.context['finished_task_list'], list)
        self.assertIsInstance(response.context['new_group_links'], list)

        new_group_links = [
            ('New Task Group', reverse('groups:new_task_group', kwargs=self.args)),
            ('New Subgroup', reverse('groups:new_subgroup_task', kwargs=self.args)),
            ('New Member', reverse('groups:new_member_task', kwargs=self.args))
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
        response = self.client.post(self.get_url(), test_forms.AddSubgroupFormTests.valid_form_data)
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
        response = self.client.post(self.get_url(), test_forms.AddSubgroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:detail', kwargs=self.args))


class NewTaskGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_task_group'
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
        response = self.client.post(self.get_url(), test_forms.TaskGroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:tasks', kwargs=self.args))
        model = models.TaskGroup.objects.get(
            gitlab_group=models.GitlabGroup.objects.get(
                gitlab_id=self.args['group_id']))
        for key, value in test_forms.TaskGroupFormTests.valid_form_data.items():
            self.assertEqual(getattr(model, key), value)


class FutureTaskGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_task_group'
    args = {'task_id': None}

    def setUp(self):
        super().setUp()
        self.parent_task = test_models.AddSubgroupCreateMethods().create_parent_task()
        self.args['task_id'] = self.parent_task.id

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
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), test_forms.TaskGroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         reverse('groups:future_group_tasks', kwargs=self.args))
        model = models.TaskGroup.objects.get(parent_task=self.parent_task)
        for key, value in test_forms.TaskGroupFormTests.valid_form_data.items():
            self.assertEqual(getattr(model, key), value)


class EditTaskGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'edit_task_group'
    args = {'task_group_id': 1}

    def setUp(self):
        super().setUp()
        self.parent_task = test_models.AddSubgroupCreateMethods().create_parent_task()
        self.task_group = test_models.AddSubgroupCreateMethods().create_task_group(
            parent_task=self.parent_task
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

    def _test_page_post_valid_data(self):
        data = self.get_initial_form_data()
        self.assertEqual(data['name'], self.task_group.name)
        data['name'] = 'Another Name'

        response = self.client.post(self.get_url(), data)
        self.assertEqual(response.status_code, 302)

        self.task_group.refresh_from_db()
        self.assertEqual(self.task_group.name, data['name'])

        return response

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        self.task_group.gitlab_group.gitlab_id = 42
        self.task_group.gitlab_group.save()

        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:tasks', kwargs={'group_id': self.task_group.gitlab_group.gitlab_id}))

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_future_tasks(self):
        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:future_group_tasks', kwargs={'task_id': self.parent_task.id}))


class NewSubgroupTaskPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_subgroup_task'
    args = {'task_group_id': 1}

    def setUp(self):
        super().setUp()
        self.parent_task = test_models.AddSubgroupCreateMethods().create_parent_task()
        self.task_group = test_models.AddSubgroupCreateMethods().create_task_group(
            parent_task=self.parent_task
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

    def _test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), test_forms.AddSubgroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)

        model = models.AddSubgroup.objects.get(task_group=self.task_group)
        for key, value in test_forms.AddSubgroupFormTests.valid_form_data.items():
            self.assertEqual(getattr(model, key), value)

        return response

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        self.task_group.gitlab_group.gitlab_id = 42
        self.task_group.gitlab_group.save()

        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:tasks', kwargs={'group_id': self.task_group.gitlab_group.gitlab_id}))

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:future_group_tasks', kwargs={'task_id': self.parent_task.id}))


class EditSubgroupTaskPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'edit_subgroup_task'
    args = {'task_id': 1}

    def setUp(self):
        super().setUp()
        self.parent_task = test_models.AddSubgroupCreateMethods().create_parent_task()
        self.task = test_models.AddSubgroupCreateMethods().create_task(
            parent_task=self.parent_task)
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

    def _test_page_post_valid_data(self):
        data = self.get_initial_form_data()
        self.assertEqual(data['name'], self.task.name)
        data['name'] = 'Another Name'
        data['description'] = 'Description'

        response = self.client.post(self.get_url(), data)
        self.assertEqual(response.status_code, 302)

        self.task.refresh_from_db()
        self.assertEqual(self.task.name, data['name'])
        self.assertEqual(self.task.description, data['description'])

        return response

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        self.task.gitlab_group.gitlab_id = 42
        self.task.gitlab_group.save()

        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:tasks', kwargs={'group_id': self.task.gitlab_group.gitlab_id}))

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_future_tasks(self):
        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:future_group_tasks', kwargs={'task_id': self.parent_task.id}))


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
        response = self.client.post(self.get_url(), test_forms.AddMemberFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('groups:members', kwargs=self.args))


class NewMemberTaskPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_member_task'
    args = {'task_group_id': 1}

    def setUp(self):
        super().setUp()
        self.parent_task = test_models.AddMemberCreateMethods().create_parent_task()
        self.task_group = test_models.AddMemberCreateMethods().create_task_group(
            parent_task=self.parent_task
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

    def _test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), test_forms.AddMemberFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)

        model = models.AddMember.objects.get(task_group=self.task_group)
        for key, value in test_forms.AddMemberFormTests.valid_form_data.items():
            self.assertEqual(getattr(model, key), value)

        return response

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        self.task_group.gitlab_group.gitlab_id = 42
        self.task_group.gitlab_group.save()

        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:tasks', kwargs={'group_id': self.task_group.gitlab_group.gitlab_id}))

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:future_group_tasks', kwargs={'task_id': self.parent_task.id}))


class EditMemberTaskPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'edit_member_task'
    args = {'task_id': 1}

    def setUp(self):
        super().setUp()
        self.parent_task = test_models.AddMemberCreateMethods().create_parent_task()
        self.task = test_models.AddMemberCreateMethods().create_task(
            parent_task=self.parent_task)
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

    def _test_page_post_valid_data(self):
        data = self.get_initial_form_data()
        self.assertEqual(data['username'], self.task.username)
        data['username'] = 'Another username'

        response = self.client.post(self.get_url(), data)
        self.assertEqual(response.status_code, 302)

        self.task.refresh_from_db()
        self.assertEqual(self.task.username, data['username'])

        return response

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        self.task.gitlab_group.gitlab_id = 42
        self.task.gitlab_group.save()

        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:tasks', kwargs={'group_id': self.task.gitlab_group.gitlab_id}))

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_future_tasks(self):
        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('groups:future_group_tasks', kwargs={'task_id': self.parent_task.id}))


class FutureGroupDetailPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'future_group_detail'
    args = {'task_id': None}

    def setUp(self):
        super().setUp()
        self.task = test_models.AddSubgroupCreateMethods().create_task()
        self.args['task_id'] = self.task.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/tasks/detail.html')

        self.assertIn('task', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIsInstance(response.context['task'], models.AddSubgroup)
        self.assertIsInstance(response.context['sidebar'], FutureGroupSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], QuerySet)


class FutureGroupMembersPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'future_group_members'
    args = {'task_id': None}

    def setUp(self):
        super().setUp()
        self.task = test_models.AddSubgroupCreateMethods().create_task()
        self.args['task_id'] = self.task.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/tasks/members.html')

        self.assertIn('task', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIsInstance(response.context['task'], models.AddSubgroup)
        self.assertIsInstance(response.context['sidebar'], FutureGroupSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], QuerySet)


class FutureGroupTasksPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'future_group_tasks'
    args = {'task_id': None}

    def setUp(self):
        super().setUp()
        self.task = test_models.AddSubgroupCreateMethods().create_task()
        self.args['task_id'] = self.task.id

    @LoginMethods.login_wrapper
    def test_page_not_found(self):
        self.args['task_id'] += 1
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/tasks/tasks.html')

        self.assertIn('task', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIn('finished_task_list', response.context)
        self.assertIn('new_group_links', response.context)
        self.assertIsInstance(response.context['task'], models.AddSubgroup)
        self.assertIsInstance(response.context['sidebar'], FutureGroupSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], list)
        self.assertIsInstance(response.context['finished_task_list'], list)
        self.assertIsInstance(response.context['new_group_links'], list)

        new_group_links = [
            ('New Task Group', reverse('groups:new_task_group', kwargs=self.args)),
            ('New Subgroup', reverse('groups:new_subgroup_task', kwargs=self.args)),
            ('New Member', reverse('groups:new_member_task', kwargs=self.args))
        ]
        for group_link in response.context['new_group_links']:
            self.assertIn(group_link, new_group_links)


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
