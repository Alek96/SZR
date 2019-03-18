import unittest

from GitLabApi.objects import *
from GitLabApi import base
from GitLabApi import mixins


class FakeGitlab(object):
    subgroups = None
    projects = None
    members = None


class FakeObject(base.RESTObject):
    def __init__(self):
        super().__init__(FakeGitlab())


class GroupSubgroupTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(GroupSubgroup(FakeGitlab()), base.RESTObject)


class GroupSubgroupManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = GroupSubgroupManager(FakeObject())
        self.assertIsInstance(mgr, mixins.ListMixin)
        self.assertEqual(mgr._obj_cls, GroupSubgroup)


class GroupProjectTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(GroupProject(FakeGitlab()), base.RESTObject)


class GroupProjectManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = GroupProjectManager(FakeObject())
        self.assertIsInstance(mgr, mixins.ListMixin)
        self.assertEqual(mgr._obj_cls, GroupProject)


class GroupMemberTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(GroupMember(FakeGitlab()), base.RESTObject)


class GroupMemberManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = GroupMemberManager(FakeObject())
        self.assertIsInstance(mgr, mixins.CRUDMixin)
        self.assertEqual(mgr._obj_cls, GroupMember)


class GroupTests(unittest.TestCase):
    def test_inheritance(self):
        obj = Group(FakeGitlab())
        self.assertIsInstance(obj, base.RESTObject)
        self.assertIsInstance(obj.subgroups, GroupSubgroupManager)
        self.assertIsInstance(obj.projects, GroupProjectManager)
        self.assertIsInstance(obj.members, GroupMemberManager)


class GroupManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = GroupManager(FakeObject())
        self.assertIsInstance(mgr, mixins.CRUDMixin)
        self.assertEqual(mgr._obj_cls, Group)


class ProjectMemberTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(ProjectMember(FakeGitlab()), base.RESTObject)


class ProjectMemberManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = ProjectMemberManager(FakeObject())
        self.assertIsInstance(mgr, mixins.CRUDMixin)
        self.assertEqual(mgr._obj_cls, ProjectMember)


class ProjectTests(unittest.TestCase):
    def test_inheritance(self):
        obj = Project(FakeGitlab())
        self.assertIsInstance(obj, base.RESTObject)
        self.assertIsInstance(obj.members, ProjectMemberManager)


class ProjectManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = ProjectManager(FakeObject())
        self.assertIsInstance(mgr, mixins.CRUDMixin)
        self.assertEqual(mgr._obj_cls, Project)
