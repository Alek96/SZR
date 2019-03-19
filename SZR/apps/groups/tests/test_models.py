from django.test import TestCase

from groups.models import *


class GitlabGroupModelUnitTests(TestCase):
    def test_representation(self):
        group = GitlabGroup.objects.create()
        self.assertEqual(repr(group), "<Group: {}>".format(group.id))

    def test_string_representation(self):
        group = GitlabGroup.objects.create()
        self.assertEqual(str(group), "<Group: {}>".format(group.id))

# class AddGroupMemberTaskGroupTests(AbstractTaskGroupTestCase.AbstractTaskGroupTests):
#     _task_group_and_task_methods_class = AddGroupMemberTaskGroupAndTaskMethods
#
#
# class AddGroupMemberTaskTests(AbstractTaskTestCase.AbstractTaskTests):
#     _task_group_and_task_methods_class = AddGroupMemberTaskGroupAndTaskMethods
