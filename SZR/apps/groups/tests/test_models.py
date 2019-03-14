from django.test import TestCase
import unittest
from unittest import mock
from django.conf import settings
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError

from groups.models import *
from tasks.tests.test_models import AbstractTaskGroupTestCase, AbstractTaskTestCase


class GitlabGroupModelUnitTests(TestCase):
    def test_representation(self):
        group = GitlabGroup.objects.create()
        self.assertEqual(repr(group), "<Group: {}>".format(group.id))

    def test_string_representation(self):
        group = GitlabGroup.objects.create()
        self.assertEqual(str(group), "<Group: {}>".format(group.id))


class AddGroupMemberTaskGroupTests(AbstractTaskGroupTestCase.AbstractTaskGroupTests):
    def create_group_task(self, **kwargs):
        return AddGroupMemberTaskGroup.objects.create(**kwargs)


class AddGroupMemberTaskTests(AbstractTaskTestCase.AbstractTaskTests):
    def setUp(self):
        super().setUp()
        self.task_group = AddGroupMemberTaskGroup.objects.create()
        self.gitlab_group = GitlabGroup.objects.create()

    def create_task(self, username="name", **kwargs):
        return AddGroupMemberTask.objects.create(
            owner=self.gitlab_user,
            task_group=self.task_group,
            username=username,
            gitlab_group=self.gitlab_group,
            **kwargs
        )
