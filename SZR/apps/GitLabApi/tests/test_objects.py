import unittest

from GitLabApi import base
from GitLabApi import mixins
from GitLabApi import objects


class FakeGitlab(object):
    subgroups = None
    projects = None
    members = None


class FakeObject(base.RESTObject):
    def __init__(self):
        super().__init__(FakeGitlab())


class ChoiceAttributeTests(unittest.TestCase):
    def test_get_field_readable(self):
        aa = 10
        bb = 20
        choices = (
            (aa, 'AA'),
            (bb, 'BB'),
        )
        choice_attribute = objects.ChoiceAttribute()

        self.assertEqual(choice_attribute._get_field_readable(aa, choices), 'AA')
        self.assertEqual(choice_attribute._get_field_readable(bb, choices), 'BB')


class AccessLevelTests(unittest.TestCase):
    def test_get_access_level_readable(self):
        access_level = objects.AccessLevel()
        access_level.access_level = objects.AccessLevel.ACCESS_GUEST
        self.assertEqual(access_level.get_access_level_readable(),
                         dict(access_level.ACCESS_LEVEL_CHOICES).get(access_level.ACCESS_GUEST))


class VisibilityLevelTests(unittest.TestCase):
    def test_get_visibility_readable(self):
        visibility = objects.VisibilityLevel()
        visibility.visibility = objects.VisibilityLevel.PUBLIC
        self.assertEqual(visibility.get_visibility_readable(),
                         dict(visibility.VISIBILITY_CHOICES).get(visibility.PUBLIC))


class GroupSubgroupTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(objects.GroupSubgroup(FakeGitlab()), base.RESTObject)

    def test_get_visibility_readable(self):
        group_subgroup = objects.GroupSubgroup(FakeGitlab())
        group_subgroup.visibility = objects.GroupSubgroup.PUBLIC
        self.assertEqual(group_subgroup.get_visibility_readable(),
                         dict(group_subgroup.VISIBILITY_CHOICES).get(group_subgroup.PUBLIC))


class GroupSubgroupManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = objects.GroupSubgroupManager(FakeObject())
        self.assertIsInstance(mgr, mixins.ListMixin)
        self.assertEqual(mgr._obj_cls, objects.GroupSubgroup)


class GroupProjectTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(objects.GroupProject(FakeGitlab()), base.RESTObject)

    def test_get_visibility_readable(self):
        group_project = objects.GroupProject(FakeGitlab())
        group_project.visibility = objects.GroupProject.PUBLIC
        self.assertEqual(group_project.get_visibility_readable(),
                         dict(group_project.VISIBILITY_CHOICES).get(group_project.PUBLIC))


class GroupProjectManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = objects.GroupProjectManager(FakeObject())
        self.assertIsInstance(mgr, mixins.ListMixin)
        self.assertEqual(mgr._obj_cls, objects.GroupProject)


class GroupMemberTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(objects.GroupMember(FakeGitlab()), base.RESTObject)

    def test_get_access_level_readable(self):
        member = objects.GroupMember(FakeGitlab())
        member.access_level = objects.GroupMember.ACCESS_GUEST
        self.assertEqual(member.get_access_level_readable(),
                         dict(member.ACCESS_LEVEL_CHOICES).get(member.ACCESS_GUEST))


class GroupMemberManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = objects.GroupMemberManager(FakeObject())
        self.assertIsInstance(mgr, mixins.CRUDMixin)
        self.assertIsInstance(mgr, mixins.AllMixin)
        self.assertEqual(mgr._obj_cls, objects.GroupMember)


class GroupTests(unittest.TestCase):
    def test_inheritance(self):
        obj = objects.Group(FakeGitlab())
        self.assertIsInstance(obj, base.RESTObject)
        self.assertIsInstance(obj.subgroups, objects.GroupSubgroupManager)
        self.assertIsInstance(obj.projects, objects.GroupProjectManager)
        self.assertIsInstance(obj.members, objects.GroupMemberManager)


class GroupManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = objects.GroupManager(FakeObject())
        self.assertIsInstance(mgr, mixins.CRUDMixin)
        self.assertEqual(mgr._obj_cls, objects.Group)


class ProjectMemberTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(objects.ProjectMember(FakeGitlab()), base.RESTObject)


class ProjectMemberManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = objects.ProjectMemberManager(FakeObject())
        self.assertIsInstance(mgr, mixins.CRUDMixin)
        self.assertIsInstance(mgr, mixins.AllMixin)
        self.assertEqual(mgr._obj_cls, objects.ProjectMember)


class ProjectTests(unittest.TestCase):
    def test_inheritance(self):
        obj = objects.Project(FakeGitlab())
        self.assertIsInstance(obj, base.RESTObject)
        self.assertIsInstance(obj.members, objects.ProjectMemberManager)

    def test_get_visibility_readable(self):
        project = objects.Project(FakeGitlab())
        project.visibility = objects.Project.PUBLIC
        self.assertEqual(project.get_visibility_readable(),
                         dict(project.VISIBILITY_CHOICES).get(project.PUBLIC))


class ProjectManagerTests(unittest.TestCase):
    def test_inheritance(self):
        mgr = objects.ProjectManager(FakeObject())
        self.assertIsInstance(mgr, mixins.CRUDMixin)
        self.assertEqual(mgr._obj_cls, objects.Project)
