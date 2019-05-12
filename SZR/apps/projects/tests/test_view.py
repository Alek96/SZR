from GitLabApi import objects
from core.tests.test_view import LoginMethods
from core.tests.test_view import SimpleUrlsTestsCases
from django.db.models import QuerySet
from django.urls import reverse
from projects import models
from projects.sidebar import ProjectSidebar, FutureProjectSidebar
from projects.tests import test_forms
from projects.tests import models as test_models


class GitlabWrapperAppNameCase:
    class GitlabWrapperAppNameTest(SimpleUrlsTestsCases.SimpleUrlsTests):
        app_name = 'projects'


class InitSidebarPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'init_sidebar'
    args = {'project_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sidebar.html')

        self.assertIn('project', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIsInstance(response.context['project'], objects.Project)
        self.assertIsInstance(response.context['sidebar'], ProjectSidebar)


class IndexPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'index'

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/index.html')

        self.assertIn('project_list', response.context)
        all(self.assertIsInstance(project, objects.Project) for project in response.context['project_list'])


class DetailPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'detail'
    args = {'project_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/detail.html')

        self.assertIn('project', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIsInstance(response.context['project'], objects.Project)
        self.assertIsInstance(response.context['sidebar'], ProjectSidebar)


class MembersPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'members'
    args = {'project_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/members.html')

        self.assertIn('project', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIsInstance(response.context['project'], objects.Project)
        self.assertIsInstance(response.context['sidebar'], ProjectSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], QuerySet)


class TasksPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'tasks'
    args = {'project_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/tasks.html')

        self.assertIn('project', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIn('finished_task_list', response.context)
        self.assertIn('new_project_links', response.context)
        self.assertIsInstance(response.context['project'], objects.Project)
        self.assertIsInstance(response.context['sidebar'], ProjectSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], list)
        self.assertIsInstance(response.context['finished_task_list'], list)
        self.assertIsInstance(response.context['new_project_links'], list)

        new_project_links = [
            ('New Task Group', reverse('projects:new_task_group', kwargs=self.args)),
            ('New Member', reverse('projects:new_member_task', kwargs=self.args))
        ]
        for group_link in response.context['new_project_links']:
            self.assertIn(group_link, new_project_links)


class NewTaskGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_task_group'
    args = {'project_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), test_forms.TaskGroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:tasks', kwargs=self.args))
        model = models.TaskGroup.objects.get(
            gitlab_project=models.GitlabProject.objects.get(
                gitlab_id=self.args['project_id']))
        for key, value in test_forms.TaskGroupFormTests.valid_form_data.items():
            self.assertEqual(getattr(model, key), value)


class FutureTaskGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_task_group'
    args = {'task_id': None}

    def setUp(self):
        super().setUp()
        self.parent_task = test_models.TaskGroupMethods().create_parent_task()
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
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), test_forms.TaskGroupFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         reverse('projects:future_project_tasks', kwargs=self.args))
        model = models.TaskGroup.objects.get(parent_task=self.parent_task)
        for key, value in test_forms.TaskGroupFormTests.valid_form_data.items():
            self.assertEqual(getattr(model, key), value)


class EditTaskGroupPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'edit_task_group'
    args = {'task_group_id': 1}

    def setUp(self):
        super().setUp()
        self.parent_task = test_models.TaskGroupMethods().create_parent_task()
        self.task_group = test_models.TaskGroupMethods().create_task_group(
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
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

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
        self.task_group.gitlab_project.gitlab_id = 42
        self.task_group.gitlab_project.save()

        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('projects:tasks', kwargs={'project_id': self.task_group.gitlab_project.gitlab_id}))

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_future_tasks(self):
        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('projects:future_project_tasks', kwargs={'task_id': self.parent_task.id}))


class NewMemberPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'new_member'
    args = {'project_id': '1'}

    @LoginMethods.login_wrapper
    def test_page_get(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), test_forms.AddMemberFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:members', kwargs=self.args))


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
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

    @LoginMethods.login_wrapper
    def test_page_post_not_valid_data(self):
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

    def _test_page_post_valid_data(self):
        response = self.client.post(self.get_url(), test_forms.AddMemberFormTests.valid_form_data)
        self.assertEqual(response.status_code, 302)

        model = models.AddMember.objects.get(task_group=self.task_group)
        for key, value in test_forms.AddMemberFormTests.valid_form_data.items():
            self.assertEqual(getattr(model, key), value)

        return response

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        self.task_group.gitlab_project.gitlab_id = 42
        self.task_group.gitlab_project.save()

        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('projects:tasks', kwargs={'project_id': self.task_group.gitlab_project.gitlab_id}))

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_tasks(self):
        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('projects:future_project_tasks', kwargs={'task_id': self.parent_task.id}))


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
        self.assertTemplateUsed(response, 'projects/form_base_site.html')

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
        self.task.gitlab_project.gitlab_id = 42
        self.task.gitlab_project.save()

        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('projects:tasks', kwargs={'project_id': self.task.gitlab_project.gitlab_id}))

    @LoginMethods.login_wrapper
    def test_page_post_valid_data_redirect_to_future_tasks(self):
        response = self._test_page_post_valid_data()

        self.assertEqual(response.url,
                         reverse('projects:future_project_tasks', kwargs={'task_id': self.parent_task.id}))


class FutureGProjectDetailPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'future_project_detail'
    args = {'task_id': None}

    def setUp(self):
        super().setUp()
        self.task = test_models.AddProjectCreateMethods().create_task()
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
        self.assertTemplateUsed(response, 'projects/tasks/detail.html')

        self.assertIn('task', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIsInstance(response.context['task'], models.AddProject)
        self.assertIsInstance(response.context['sidebar'], FutureProjectSidebar)


class FutureProjectMembersPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'future_project_members'
    args = {'task_id': None}

    def setUp(self):
        super().setUp()
        self.task = test_models.AddProjectCreateMethods().create_task()
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
        self.assertTemplateUsed(response, 'projects/tasks/members.html')

        self.assertIn('task', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIsInstance(response.context['task'], models.AddProject)
        self.assertIsInstance(response.context['sidebar'], FutureProjectSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], QuerySet)


class FutureProjectTasksPageTest(GitlabWrapperAppNameCase.GitlabWrapperAppNameTest):
    name = 'future_project_tasks'
    args = {'task_id': None}

    def setUp(self):
        super().setUp()
        self.task = test_models.AddProjectCreateMethods().create_task()
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
        self.assertTemplateUsed(response, 'projects/tasks/tasks.html')

        self.assertIn('task', response.context)
        self.assertIn('sidebar', response.context)
        self.assertIn('unfinished_task_list', response.context)
        self.assertIn('finished_task_list', response.context)
        self.assertIn('new_project_links', response.context)
        self.assertIsInstance(response.context['task'], models.AddProject)
        self.assertIsInstance(response.context['sidebar'], FutureProjectSidebar)
        self.assertIsInstance(response.context['unfinished_task_list'], list)
        self.assertIsInstance(response.context['finished_task_list'], list)
        self.assertIsInstance(response.context['new_project_links'], list)

        new_project_links = [
            ('New Task Group', reverse('projects:new_task_group', kwargs=self.args)),
            ('New Member', reverse('projects:new_member_task', kwargs=self.args))
        ]
        for group_link in response.context['new_project_links']:
            self.assertIn(group_link, new_project_links)
