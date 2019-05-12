from core.tests import test_models as core_test_models
from django.core.exceptions import ValidationError
from django.urls import reverse
from projects import models
from projects.tests.models import AbstractTaskCreateMethods, AddMemberCreateMethods


class TaskGroupTests(AbstractTaskCreateMethods, core_test_models.AbstractTaskGroupTests):
    def test_creating_with_gitlab_project_and_parent_task_raise_error(self):
        gitlab_project = models.GitlabProject.objects.create()
        parent_task = self.create_parent_task()
        with self.assertRaises(ValidationError):
            self.create_task_group(gitlab_project=gitlab_project, parent_task=parent_task)

    def test_edit_url(self):
        task_group = self.create_task_group()
        self.assertEqual(
            task_group.edit_url,
            reverse('projects:edit_task_group', kwargs={'task_group_id': task_group.id}))

    def test_delete_url(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.delete_url, '#')

    def test_tasks_page_url_points_tasks(self):
        task_group = self.create_task_group(
            gitlab_project=models.GitlabProject.objects.create(gitlab_id=1)
        )
        self.assertEqual(
            task_group.tasks_page_url,
            reverse('projects:tasks', kwargs={'project_id': task_group.gitlab_project.gitlab_id}))

    def test_tasks_page_url_points_future_tasks(self):
        parent_task = self.create_parent_task()
        task_group = self.create_task_group(parent_task=parent_task)

        self.assertEqual(
            task_group.tasks_page_url,
            reverse('projects:future_project_tasks', kwargs={'task_id': parent_task.id}))


class AbstractTaskTests(AbstractTaskCreateMethods, core_test_models.AbstractTaskTests):
    def test_creating_with_gitlab_project_and_task_group_raise_error(self):
        gitlab_project = models.GitlabProject.objects.create()
        task_group = self.create_task_group()
        with self.assertRaises(ValidationError):
            self.create_task(gitlab_project=gitlab_project, task_group=task_group)

    def test_creating_with_gitlab_project_and_parent_task_raise_error(self):
        gitlab_project = models.GitlabProject.objects.create()
        parent_task = self.create_parent_task()
        with self.assertRaises(ValidationError):
            self.create_task(gitlab_project=gitlab_project, parent_task=parent_task)

    def test_tasks_page_url_points_tasks(self):
        task = self.create_task(
            gitlab_project=models.GitlabProject.objects.create(gitlab_id=1)
        )
        self.assertEqual(
            task.tasks_page_url,
            reverse('projects:tasks', kwargs={'project_id': task.gitlab_project.gitlab_id}))

    def test_tasks_page_url_points_future_tasks(self):
        parent_task = self.create_parent_task()
        task = self.create_task(parent_task=parent_task)

        self.assertEqual(
            task.tasks_page_url,
            reverse('projects:future_project_tasks', kwargs={'task_id': parent_task.id}))

    def test_creating_with_parent_task_set_gitlab_project(self):
        parent_task = self.create_parent_task()
        task = self.create_task(parent_task=parent_task)
        self.assertEqual(task.gitlab_project, parent_task.new_gitlab_project)

    def test_creating_with_task_group_set_gitlab_project(self):
        task_group = self.create_task_group()
        task = self.create_task(task_group=task_group)
        self.assertEqual(task.gitlab_project, task_group.gitlab_project)

    def test_creating_with_task_group_set_parent_task_if_exist(self):
        parent_task = self.create_parent_task()
        task_group = self.create_task_group(parent_task=parent_task)
        task = self.create_task(task_group=task_group)
        self.assertEqual(task.parent_task.id, parent_task.id)


class AddMemberTests(AddMemberCreateMethods, core_test_models.AbstractTaskTests):
    def test_task_name(self):
        task = self.create_task()
        self.assertEqual(task.get_name, 'Add user: {}'.format(task.username))

    def test_edit_url(self):
        task = self.create_task()
        self.assertEqual(
            task.edit_url,
            reverse('projects:edit_member_task', kwargs={'task_id': task.id}))

    def test_delete_url(self):
        task = self.create_task()
        self.assertEqual(task.delete_url, '#')
