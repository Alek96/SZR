from unittest import mock
import unittest
from django.test import TestCase
from django.utils import timezone
from pydoc import locate
import json

from groups.models import *
from groups.tests.models import *
from core.tests.test_models import TaskGroupAndTaskMethods, AbstractTaskTests, AbstractTaskGroupTests


class GitlabGroupModelUnitTests(TestCase):
    def test_representation(self):
        group = GitlabGroup.objects.create()
        self.assertEqual(repr(group), "<Group: {}>".format(group.id))

    def test_string_representation(self):
        group = GitlabGroup.objects.create()
        self.assertEqual(str(group), "<Group: {}>".format(group.id))

    def _prepare_task_groups(self, create_class, gitlab_group):
        task_group_list = [
            create_class().create_task_group(
                gitlab_group=gitlab_group,
                status=AddSubgroupGroup.WAITING),
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

    def test_get_unfinished_task_list(self):
        gitlab_group = GitlabGroup.objects.create()
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

    def test_get_finished_task_list(self):
        gitlab_group = GitlabGroup.objects.create()
        subgroup_list = self._prepare_task_groups(AddSubgroupCreateMethods, gitlab_group)
        member_list = self._prepare_task_groups(AddMemberCreateMethods, gitlab_group)

        finished_task_list = gitlab_group.get_finished_task_list()
        self.assertEqual(len(finished_task_list), 4)
        # sorted by finished_date
        self.assertEqual(finished_task_list[0].id, subgroup_list[3].id)
        self.assertEqual(finished_task_list[1].id, subgroup_list[4].id)
        self.assertEqual(finished_task_list[2].id, member_list[3].id)
        self.assertEqual(finished_task_list[3].id, member_list[4].id)


class ParentTaskSubgroupCreateMethods(TaskGroupAndTaskMethods):
    def create_task_group(self, name='name', parent_task=None, gitlab_group=None, **kwargs):
        return FakeParentTaskSubgroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or None if parent_task else GitlabGroup.objects.create(),
            parent_task=parent_task,
            **kwargs
        )

    def create_task(self, owner=None, task_group=None, new_gitlab_group=None, **kwargs):
        return FakeAddSubgroup.objects.create(
            owner=owner or GitlabUser.objects.create(),
            task_group=task_group or getattr(self, 'task_group', self.create_task_group()),
            new_gitlab_group=new_gitlab_group,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return self.create_task(
            task_group=self.create_task_group()
        )


class AbstractParentTaskSubgroupTests(AbstractTaskGroupTests, ParentTaskSubgroupCreateMethods):
    def test_creating_with_parent_task_and_gitlab_groups_raise_error(self):
        with self.assertRaises(ValidationError):
            self.create_task_group(
                parent_task=self.create_parent_task(),
                gitlab_group=GitlabGroup.objects.create()
            )

    def test_creating_with_parent_task_set_gitlab_group(self):
        task = self.create_parent_task()
        task_group = self.create_task_group(parent_task=task)
        self.assertEqual(task_group.gitlab_group, task.new_gitlab_group)


class AbstractAddSubgroupTests(AbstractTaskTests, ParentTaskSubgroupCreateMethods):
    def test_creating_with_new_gitlab_group_does_not_create_new_gitlab_group(self):
        gitlab_group = GitlabGroup.objects.create()
        task = self.create_task(
            new_gitlab_group=gitlab_group
        )
        self.assertEqual(task.new_gitlab_group, gitlab_group)


class AddSubgroupCreateMethods(TaskGroupAndTaskMethods):
    def create_task_group(self, name='name', parent_task=None, gitlab_group=None, **kwargs):
        return AddSubgroupGroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or (None if parent_task else GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )

    def create_task(self, owner=None, task_group=None, new_gitlab_group=None, name='name', path='path', **kwargs):
        return AddSubgroup.objects.create(
            owner=owner or GitlabUser.objects.create(),
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


class AddSubgroupGroupTests(AbstractParentTaskSubgroupTests, AddSubgroupCreateMethods):
    pass


class AddSubgroupTests(AbstractTaskTests, AddSubgroupCreateMethods):
    def test_task_name(self):
        task = self.create_task()
        self.assertEqual(task.task_name, 'Create subgroup: {}'.format(task.name))


class AddMemberCreateMethods(TaskGroupAndTaskMethods):
    def create_task_group(self, name='name', parent_task=None, gitlab_group=None, **kwargs):
        return AddMemberGroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or (None if parent_task else GitlabGroup.objects.create()),
            parent_task=parent_task,
            **kwargs
        )

    def create_task(self, owner=None, task_group=None, username='username', **kwargs):
        return AddMember.objects.create(
            owner=owner or GitlabUser.objects.create(),
            task_group=task_group or getattr(self, 'task_group', self.create_task_group()),
            username=username,
            **kwargs
        )

    def create_parent_task(self, **kwargs):
        return AddSubgroupCreateMethods().create_task()


class AddMemberGroupsTests(AbstractParentTaskSubgroupTests, AddMemberCreateMethods):
    pass


class AddMemberTests(AbstractTaskTests, AddMemberCreateMethods):
    def test_task_name(self):
        task = self.create_task()
        self.assertEqual(task.task_name, 'Add user: {}'.format(task.username))
