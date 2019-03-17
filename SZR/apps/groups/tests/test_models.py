from django.test import TestCase

from groups.models import *
from core.tests.test_models import AbstractTaskGroupAndTaskMethods, AbstractTaskGroupTestCase, AbstractTaskTestCase


class GitlabGroupModelUnitTests(TestCase):
    def test_representation(self):
        group = GitlabGroup.objects.create()
        self.assertEqual(repr(group), "<Group: {}>".format(group.id))

    def test_string_representation(self):
        group = GitlabGroup.objects.create()
        self.assertEqual(str(group), "<Group: {}>".format(group.id))


class AddGroupMemberTaskGroupAndTaskMethods(AbstractTaskGroupAndTaskMethods):
    def __init__(self):
        super().__init__()
        self.gitlab_group = GitlabGroup.objects.create()

    def create_task_group(self, **kwargs):
        return AddGroupMemberTaskGroup.objects.create(**kwargs)

    def create_task(self, username="name", **kwargs):
        return AddGroupMemberTask.objects.create(
            owner=self.gitlab_user,
            task_group=self.task_group,
            username=username,
            gitlab_group=self.gitlab_group,
            **kwargs
        )


class AddGroupMemberTaskGroupTests(AbstractTaskGroupTestCase.AbstractTaskGroupTests):
    _task_group_and_task_methods_class = AddGroupMemberTaskGroupAndTaskMethods


class AddGroupMemberTaskTests(AbstractTaskTestCase.AbstractTaskTests):
    _task_group_and_task_methods_class = AddGroupMemberTaskGroupAndTaskMethods
