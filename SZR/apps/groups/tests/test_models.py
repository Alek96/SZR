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
            create_class().create_task_group(
                gitlab_group=gitlab_group,
                status=models.AddSubgroupGroup.WAITING),
            create_class().create_task_group(
                gitlab_group=gitlab_group,
                tasks_number=1),
            create_class().create_task_group(
                gitlab_group=gitlab_group,
                tasks_number=2,
                finished_tasks_number=1),
            create_class().create_task_group(
                gitlab_group=gitlab_group,
                tasks_number=1,
                finished_tasks_number=1,
                finished_date=timezone.now()),
            create_class().create_task_group(
                gitlab_group=gitlab_group,
                tasks_number=1,
                finished_tasks_number=1,
                failed_task_number=1,
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


class AbstractTaskGroupCreateMethods(core_test_models.TaskGroupAndTaskMethods):
    def create_task_group(self, name='name', parent_task=None, gitlab_group=None, **kwargs):
        return test_models.FakeTaskGroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or (None if parent_task else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )

    def create_task(self, owner=None, task_group=None, new_gitlab_group=None, **kwargs):
        return test_models.FakeAddSubgroup.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group or getattr(self, 'task_group', self.create_task_group()),
            new_gitlab_group=new_gitlab_group,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return self.create_task(
            task_group=self.create_task_group()
        )


class AbstractTaskGroupTests(AbstractTaskGroupCreateMethods, core_test_models.AbstractTaskGroupTests):
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

    def test_creating_with_parent_task_and_gitlab_groups_raise_error(self):
        with self.assertRaises(ValidationError):
            self.create_task_group(
                parent_task=self.create_parent_task(),
                gitlab_group=models.GitlabGroup.objects.create()
            )

    def test_creating_with_parent_task_set_gitlab_group(self):
        parent_task = self.create_parent_task()
        task_group = self.create_task_group(parent_task=parent_task)
        self.assertEqual(task_group.gitlab_group, parent_task.new_gitlab_group)


class AbstractAddSubgroupTests(AbstractTaskGroupCreateMethods, core_test_models.AbstractTaskTests):
    def test_creating_with_new_gitlab_group_does_not_create_new_gitlab_group(self):
        gitlab_group = models.GitlabGroup.objects.create()
        task = self.create_task(
            new_gitlab_group=gitlab_group
        )
        self.assertEqual(task.new_gitlab_group, gitlab_group)


class AddSubgroupCreateMethods(core_test_models.TaskGroupAndTaskMethods):
    def create_task_group(self, name='name', parent_task=None, gitlab_group=None, **kwargs):
        return models.AddSubgroupGroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or (None if parent_task else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )

    def create_task(self, owner=None, task_group=None, new_gitlab_group=None, name='name', path='path', **kwargs):
        return models.AddSubgroup.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group or getattr(self, 'task_group', self.create_task_group()),
            new_gitlab_group=new_gitlab_group,
            name=name,
            path=path,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return self.create_task(
            task_group=self.create_task_group()
        )


class AddSubgroupGroupTests(AddSubgroupCreateMethods, AbstractTaskGroupTests):
    def test_edit_url(self):
        task_group = self.create_task_group()
        self.assertEqual(
            task_group.edit_url,
            reverse('groups:edit_subgroup_group', kwargs={'task_group_id': task_group.id}))

    def test_delete_url(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.delete_url, '#')

    def test_new_task_url(self):
        task_group = self.create_task_group(
            gitlab_group=models.GitlabGroup.objects.create(gitlab_id=42)
        )
        self.assertEqual(
            task_group.new_task_url,
            reverse('groups:new_subgroup_task', kwargs={'task_group_id': task_group.id}))


class AddSubgroupTests(AddSubgroupCreateMethods, core_test_models.AbstractTaskTests):
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

    def test_tasks_page_url_points_tasks(self):
        task = self.create_task(
            task_group=self.create_task_group(
                gitlab_group=models.GitlabGroup.objects.create(gitlab_id=42)))

        self.assertEqual(
            task.tasks_page_url,
            reverse('groups:tasks', kwargs={'group_id': task.task_group.gitlab_group.gitlab_id}))

    def test_tasks_page_url_points_future_tasks(self):
        parent_task = self.create_parent_task()
        task = self.create_task(
            task_group=self.create_task_group(
                parent_task=parent_task))

        self.assertEqual(
            task.tasks_page_url,
            reverse('groups:future_group_tasks', kwargs={'task_id': parent_task.id}))


class AddMemberCreateMethods(core_test_models.TaskGroupAndTaskMethods):
    def create_task_group(self, name='name', parent_task=None, gitlab_group=None, **kwargs):
        return models.AddMemberGroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or (None if parent_task else models.GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )

    def create_task(self, owner=None, task_group=None, username='username', **kwargs):
        return models.AddMember.objects.create(
            owner=owner or core_models.GitlabUser.objects.create(),
            task_group=task_group or getattr(self, 'task_group', self.create_task_group()),
            username=username,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return AddSubgroupCreateMethods().create_task()


class AddMemberGroupsTests(AddMemberCreateMethods, AbstractTaskGroupTests):
    def test_link_to_edit(self):
        task_group = self.create_task_group()
        self.assertEqual(
            task_group.edit_url,
            reverse('groups:edit_member_group', kwargs={'task_group_id': task_group.id}))

    def test_delete_url(self):
        task_group = self.create_task_group()
        self.assertEqual(task_group.delete_url, '#')

    def test_new_task_url(self):
        task_group = self.create_task_group(
            gitlab_group=models.GitlabGroup.objects.create(gitlab_id=42)
        )
        self.assertEqual(
            task_group.new_task_url,
            reverse('groups:new_member_task', kwargs={'task_group_id': task_group.id}))


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

    def test_tasks_page_url_points_tasks(self):
        task = self.create_task(
            task_group=self.create_task_group(
                gitlab_group=models.GitlabGroup.objects.create(gitlab_id=42)))

        self.assertEqual(
            task.tasks_page_url,
            reverse('groups:tasks', kwargs={'group_id': task.task_group.gitlab_group.gitlab_id}))

    def test_tasks_page_url_points_future_tasks(self):
        parent_task = self.create_parent_task()
        task = self.create_task(
            task_group=self.create_task_group(
                parent_task=parent_task))

        self.assertEqual(
            task.tasks_page_url,
            reverse('groups:future_group_tasks', kwargs={'task_id': parent_task.id}))
