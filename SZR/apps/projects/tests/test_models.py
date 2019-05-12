from core.tests import test_models as core_test_models
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from projects import models
from projects.tests.models import AddProjectCreateMethods, AbstractTaskCreateMethods, AddMemberCreateMethods


class GitlabProjectModelUnitTests(TestCase):
    def test_representation(self):
        project = models.GitlabProject.objects.create()
        self.assertEqual(repr(project), "<Project: {}>".format(project.id))

    def test_string_representation(self):
        project = models.GitlabProject.objects.create()
        self.assertEqual(str(project), "<Project: {}>".format(project.id))

    def _prepare_task_groups(self, create_class, gitlab_project):
        task_group_list = [
            create_class().create_task(
                gitlab_project=gitlab_project,
                status=models.AddMember.WAITING),
            create_class().create_task(
                gitlab_project=gitlab_project,
                status=models.AddMember.READY),
            create_class().create_task(
                gitlab_project=gitlab_project,
                status=models.AddMember.RUNNING),
            create_class().create_task(
                gitlab_project=gitlab_project,
                status=models.AddMember.SUCCEED,
                finished_date=timezone.now()),
            create_class().create_task(
                gitlab_project=gitlab_project,
                status=models.AddMember.FAILED,
                finished_date=timezone.now()),
        ]
        # check statuses
        self.assertEqual(task_group_list[0].status, task_group_list[0].WAITING)
        self.assertEqual(task_group_list[1].status, task_group_list[1].READY)
        self.assertEqual(task_group_list[2].status, task_group_list[2].RUNNING)
        self.assertEqual(task_group_list[3].status, task_group_list[3].SUCCEED)
        self.assertEqual(task_group_list[4].status, task_group_list[4].FAILED)
        # check execute_date
        self.assertLess(task_group_list[0].execute_date, task_group_list[1].execute_date)
        self.assertLess(task_group_list[1].execute_date, task_group_list[2].execute_date)
        self.assertLess(task_group_list[2].execute_date, task_group_list[3].execute_date)
        self.assertLess(task_group_list[3].execute_date, task_group_list[4].execute_date)
        # check finished_date
        self.assertEqual(task_group_list[0].finished_date, None)
        self.assertEqual(task_group_list[1].finished_date, None)
        self.assertEqual(task_group_list[2].finished_date, None)
        self.assertLess(task_group_list[3].finished_date, task_group_list[4].finished_date)

        return task_group_list

    def test_get_unfinished_task_list_with_model(self):
        gitlab_project = models.GitlabProject.objects.create()
        subgroup_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_project)

        unfinished_task_list = gitlab_project.get_unfinished_task_list(model=models.AddMember)
        self.assertEqual(len(unfinished_task_list), 3)
        # sorted by execute_date in descending order
        self.assertEqual(unfinished_task_list[0].id, subgroup_list[2].id)
        self.assertEqual(unfinished_task_list[1].id, subgroup_list[1].id)
        self.assertEqual(unfinished_task_list[2].id, subgroup_list[0].id)

    def test_get_unfinished_task_list(self):
        gitlab_project = models.GitlabProject.objects.create()
        member_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_project)

        unfinished_task_list = gitlab_project.get_unfinished_task_list()
        self.assertEqual(len(unfinished_task_list), 3)
        # sorted by execute_date in descending order
        self.assertEqual(unfinished_task_list[0].id, member_list[2].id)
        self.assertEqual(unfinished_task_list[1].id, member_list[1].id)
        self.assertEqual(unfinished_task_list[2].id, member_list[0].id)

    def test_get_finished_task_list_with_model(self):
        gitlab_project = models.GitlabProject.objects.create()
        subgroup_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_project)

        finished_task_list = gitlab_project.get_finished_task_list(model=models.AddMember)
        self.assertEqual(len(finished_task_list), 2)
        # sorted by finished_date
        self.assertEqual(finished_task_list[0].id, subgroup_list[3].id)
        self.assertEqual(finished_task_list[1].id, subgroup_list[4].id)

    def test_get_finished_task_list(self):
        gitlab_project = models.GitlabProject.objects.create()
        member_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_project)

        finished_task_list = gitlab_project.get_finished_task_list()
        self.assertEqual(len(finished_task_list), 2)
        # sorted by finished_date
        self.assertEqual(finished_task_list[0].id, member_list[3].id)
        self.assertEqual(finished_task_list[1].id, member_list[4].id)


class AddProjectTests(AddProjectCreateMethods, core_test_models.AbstractTaskTests):
    def test_creating_obj_create_new_gitlab_project(self):
        task = self.create_task()
        self.assertTrue(task.new_gitlab_project)

    def test_creating_with_new_gitlab_project_does_not_create_new_gitlab_project(self):
        gitlab_project = models.GitlabProject.objects.create()
        task = self.create_task(new_gitlab_project=gitlab_project)
        self.assertEqual(task.new_gitlab_project, gitlab_project)

    def test_task_name(self):
        task = self.create_task()
        self.assertEqual(task.get_name, 'Create project: {}'.format(task.name))

    def test_edit_url(self):
        task = self.create_task()
        self.assertEqual(
            task.edit_url,
            reverse('groups:edit_project_task', kwargs={'task_id': task.id}))

    def test_delete_url(self):
        task = self.create_task()
        self.assertEqual(task.delete_url, '#')

    def test_set_create_type_to_not_blank_without_import_url_raise_error(self):
        with self.assertRaises(ValidationError):
            self.create_task(create_type=models.AddProject.FORK)

    def test_set_create_type_to_blank_set_import_url_to_None(self):
        task = self.create_task(create_type=models.AddProject.BLANK, import_url='http://example.com')
        self.assertEqual(task.import_url, None)


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
