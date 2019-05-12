import unittest

from GitLabApi import GitLabApi, mock_all_gitlab_url
from core.tests.test_view import LoginMethods
from projects.sidebar import ProjectSidebar, FutureProjectSidebar
from projects.tests.models import AddProjectCreateMethods


class GroupSidebarTests(LoginMethods):

    @mock_all_gitlab_url
    @LoginMethods.create_user_wrapper
    def test_init(self):
        group = GitLabApi(self.user.id).groups.get(1)
        sidebar = ProjectSidebar(group)
        self.assertEqual(sidebar.title, group.name)
        self.assertEqual(sidebar.name, 'Project Menu')
        self.assertEqual(sidebar.search, True)


class FutureGroupSidebarTests(unittest.TestCase):

    def test_init(self):
        task = AddProjectCreateMethods().create_task()
        sidebar = FutureProjectSidebar(task)
        self.assertEqual(sidebar.title, task.get_name)
        self.assertEqual(sidebar.name, 'Project Menu')
        self.assertEqual(sidebar.search, True)
