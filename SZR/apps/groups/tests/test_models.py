from unittest import mock
import unittest
from django.test import TestCase
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
            gitlab_group=gitlab_group or None if parent_task else GitlabGroup.objects.create(),
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
    pass


class AddMemberCreateMethods(TaskGroupAndTaskMethods):
    def create_task_group(self, name='name', parent_task=None, gitlab_group=None, **kwargs):
        return AddMemberGroup.objects.create(
            name=name,
            gitlab_group=gitlab_group or None if parent_task else GitlabGroup.objects.create(),
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
    pass
