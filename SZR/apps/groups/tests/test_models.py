from core import models as core_models
from core.tests import test_models as core_test_models
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from groups import models
from groups.tests import models as test_models


class GitlabGroupModelUnitTests(TestCase):
    def test_representation(self):
        group = models.GitlabGroup.objects.create()
        self.assertEqual(repr(group), "<Group: {}>".format(group.id))

    def test_string_representation(self):
        group = models.GitlabGroup.objects.create()
        self.assertEqual(str(group), "<Group: {}>".format(group.id))

    def _prepare_task_groups(self, create_class, gitlab_group):
        task_group_list = [
            create_class().create_task(
                gitlab_group=gitlab_group,
                status=models.AddSubgroup.WAITING),
            create_class().create_task(
                gitlab_group=gitlab_group,
                status=models.AddSubgroup.READY),
            create_class().create_task(
                gitlab_group=gitlab_group,
                status=models.AddSubgroup.RUNNING),
            create_class().create_task(
                gitlab_group=gitlab_group,
                status=models.AddSubgroup.SUCCEED,
                finished_date=timezone.now()),
            create_class().create_task(
                gitlab_group=gitlab_group,
                status=models.AddSubgroup.FAILED,
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

    def test_get_unfinished_add_subgroup_group(self):
        gitlab_group = models.GitlabGroup.objects.create()
        subgroup_list = self._prepare_task_groups(AddSubgroupCreateMethods, gitlab_group)

        unfinished_task_list = gitlab_group.get_unfinished_add_subgroup_group()
        self.assertEqual(len(unfinished_task_list), 3)
        # sorted by execute_date in descending order
        self.assertEqual(unfinished_task_list[0].id, subgroup_list[2].id)
        self.assertEqual(unfinished_task_list[1].id, subgroup_list[1].id)
        self.assertEqual(unfinished_task_list[2].id, subgroup_list[0].id)

    def test_get_unfinished_add_member_group(self):
        gitlab_group = models.GitlabGroup.objects.create()
        member_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_group)

        unfinished_task_list = gitlab_group.get_unfinished_add_member_group()
        self.assertEqual(len(unfinished_task_list), 3)
        # sorted by execute_date in descending order
        self.assertEqual(unfinished_task_list[0].id, member_list[2].id)
        self.assertEqual(unfinished_task_list[1].id, member_list[1].id)
        self.assertEqual(unfinished_task_list[2].id, member_list[0].id)

    def test_get_unfinished_task_list(self):
        gitlab_group = models.GitlabGroup.objects.create()
        subgroup_list = self._prepare_task_groups(AddSubgroupCreateMethods, gitlab_group)
        member_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_group)

        unfinished_task_list = gitlab_group.get_unfinished_task_list()
        self.assertEqual(len(unfinished_task_list), 6)
        # sorted by execute_date in descending order
        self.assertEqual(unfinished_task_list[0].id, member_list[2].id)
        self.assertEqual(unfinished_task_list[1].id, member_list[1].id)
        self.assertEqual(unfinished_task_list[2].id, member_list[0].id)
        self.assertEqual(unfinished_task_list[3].id, subgroup_list[2].id)
        self.assertEqual(unfinished_task_list[4].id, subgroup_list[1].id)
        self.assertEqual(unfinished_task_list[5].id, subgroup_list[0].id)

    def test_get_finished_add_subgroup_group(self):
        gitlab_group = models.GitlabGroup.objects.create()
        subgroup_list = self._prepare_task_groups(AddSubgroupCreateMethods, gitlab_group)

        finished_task_list = gitlab_group.get_finished_add_subgroup_group()
        self.assertEqual(len(finished_task_list), 2)
        # sorted by finished_date
        self.assertEqual(finished_task_list[0].id, subgroup_list[3].id)
        self.assertEqual(finished_task_list[1].id, subgroup_list[4].id)

    def test_get_finished_add_member_group(self):
        gitlab_group = models.GitlabGroup.objects.create()
        member_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_group)

        finished_task_list = gitlab_group.get_finished_add_member_group()
        self.assertEqual(len(finished_task_list), 2)
        # sorted by finished_date
        self.assertEqual(finished_task_list[0].id, member_list[3].id)
        self.assertEqual(finished_task_list[1].id, member_list[4].id)

    def test_get_finished_task_list(self):
        gitlab_group = models.GitlabGroup.objects.create()
        subgroup_list = self._prepare_task_groups(AddSubgroupCreateMethods, gitlab_group)
        member_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_group)

        finished_task_list = gitlab_group.get_finished_task_list()
        self.assertEqual(len(finished_task_list), 4)
        # sorted by finished_date
        self.assertEqual(finished_task_list[0].id, subgroup_list[3].id)
        self.assertEqual(finished_task_list[1].id, subgroup_list[4].id)
        self.assertEqual(finished_task_list[2].id, member_list[3].id)
        self.assertEqual(finished_task_list[3].id, member_list[4].id)


class TaskGroupMethods(core_test_models.TaskGroupMethods):
    def create_task_group(self, name='Name', gitlab_group=None, parent_task=None, **kwargs):
        return models.TaskGroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or (None if parent_task else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )


class AbstractTaskCreateMethods(TaskGroupMethods, core_test_models.TaskMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_group=None, **kwargs):
        return test_models.FakeTask.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_group=gitlab_group or (None if (task_group or parent_task) else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return AddSubgroupCreateMethods().create_task(**kwargs)


class TaskGroupTests(AbstractTaskCreateMethods, core_test_models.AbstractTaskGroupTests):
    def test_creating_with_gitlab_group_and_parent_task_raise_error(self):
        gitlab_group = models.GitlabGroup.objects.create()
        parent_task = self.create_parent_task()
        with self.assertRaises(ValidationError):
            self.create_task_group(gitlab_group=gitlab_group, parent_task=parent_task)

    def test_edit_url(self):
        task_group = self.create_task_group()
        self.assertEqual(
            task_group.edit_url,
            reverse('groups:edit_task_group', kwargs={'task_group_id': task_group.id}))

    def test_delete_url(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.delete_url, '#')

    def test_tasks_page_url_points_tasks(self):
        task_group = self.create_task_group(
            gitlab_group=models.GitlabGroup.objects.create(gitlab_id=1)
        )
        self.assertEqual(
            task_group.tasks_page_url,
            reverse('groups:tasks', kwargs={'group_id': task_group.gitlab_group.gitlab_id}))

    def test_tasks_page_url_points_future_tasks(self):
        parent_task = self.create_parent_task()
        task_group = self.create_task_group(parent_task=parent_task)

        self.assertEqual(
            task_group.tasks_page_url,
            reverse('groups:future_group_tasks', kwargs={'task_id': parent_task.id}))


class AbstractTaskTests(AbstractTaskCreateMethods, core_test_models.AbstractTaskTests):
    def test_creating_with_gitlab_group_and_task_group_raise_error(self):
        gitlab_group = models.GitlabGroup.objects.create()
        task_group = self.create_task_group()
        with self.assertRaises(ValidationError):
            self.create_task(gitlab_group=gitlab_group, task_group=task_group)

    def test_creating_with_gitlab_group_and_parent_task_raise_error(self):
        gitlab_group = models.GitlabGroup.objects.create()
        parent_task = self.create_parent_task()
        with self.assertRaises(ValidationError):
            self.create_task(gitlab_group=gitlab_group, parent_task=parent_task)

    def test_tasks_page_url_points_tasks(self):
        task = self.create_task(
            gitlab_group=models.GitlabGroup.objects.create(gitlab_id=1)
        )
        self.assertEqual(
            task.tasks_page_url,
            reverse('groups:tasks', kwargs={'group_id': task.gitlab_group.gitlab_id}))

    def test_tasks_page_url_points_future_tasks(self):
        parent_task = self.create_parent_task()
        task = self.create_task(parent_task=parent_task)

        self.assertEqual(
            task.tasks_page_url,
            reverse('groups:future_group_tasks', kwargs={'task_id': parent_task.id}))

    def test_creating_with_parent_task_set_gitlab_group(self):
        parent_task = self.create_parent_task()
        task = self.create_task(parent_task=parent_task)
        self.assertEqual(task.gitlab_group, parent_task.new_gitlab_group)

    def test_creating_with_task_group_set_gitlab_group(self):
        task_group = self.create_task_group()
        task = self.create_task(task_group=task_group)
        self.assertEqual(task.gitlab_group, task_group.gitlab_group)

    def test_creating_with_task_group_set_parent_task_if_exist(self):
        parent_task = self.create_parent_task()
        task_group = self.create_task_group(parent_task=parent_task)
        task = self.create_task(task_group=task_group)
        self.assertEqual(task.parent_task.id, parent_task.id)


class AddSubgroupCreateMethods(TaskGroupMethods, core_test_models.TaskMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_group=None, name='name', path='path',
                    **kwargs):
        return models.AddSubgroup.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_group=gitlab_group or (None if (task_group or parent_task) else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            name=name,
            path=path,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return AddSubgroupCreateMethods().create_task(**kwargs)


class AddSubgroupTests(AddSubgroupCreateMethods, core_test_models.AbstractTaskTests):
    def test_init_create_new_gitlab_group_if_does_not_exist(self):
        task = self.create_task()
        self.assertTrue(task.new_gitlab_group)

    def test_init_does_not_create_new_gitlab_group_if_it_exists(self):
        gitlab_group = models.GitlabGroup.objects.create()
        task = self.create_task(new_gitlab_group=gitlab_group)
        self.assertEqual(task.new_gitlab_group.id, gitlab_group.id)

    def test_task_name(self):
        task = self.create_task()
        self.assertEqual(task.task_name, 'Create subgroup: {}'.format(task.name))

    def test_edit_url(self):
        task = self.create_task()
        self.assertEqual(
            task.edit_url,
            reverse('groups:edit_subgroup_task', kwargs={'task_id': task.id}))

    def test_delete_url(self):
        task = self.create_task()
        self.assertEqual(task.delete_url, '#')


class AddMemberCreateMethods(AbstractTaskCreateMethods):
    def create_task(self, owner=None, task_group=None, parent_task=None, gitlab_group=None, username='username',
                    **kwargs):
        return models.AddMember.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group,
            gitlab_group=gitlab_group or (None if (task_group or parent_task) else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            username=username,
            **kwargs
        )


class AddMemberTests(AddMemberCreateMethods, core_test_models.AbstractTaskTests):
    def test_task_name(self):
        task = self.create_task()
        self.assertEqual(task.task_name, 'Add user: {}'.format(task.username))

    def test_edit_url(self):
        task = self.create_task()
        self.assertEqual(
            task.edit_url,
            reverse('groups:edit_member_task', kwargs={'task_id': task.id}))

    def test_delete_url(self):
        task = self.create_task()
        self.assertEqual(task.delete_url, '#')
