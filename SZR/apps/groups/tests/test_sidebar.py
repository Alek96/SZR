import unittest

from GitLabApi import GitLabApi, mock_all_gitlab_url
from core.tests.test_view import LoginMethods
from groups.sidebar import GroupSidebar, FutureGroupSidebar
from groups.tests.models import AddSubgroupCreateMethods


class GroupSidebarTests(LoginMethods):

    @mock_all_gitlab_url
    @LoginMethods.create_user_wrapper
    def test_init(self):
        group = GitLabApi(self.user.id).groups.get(1)
        sidebar = GroupSidebar(group)
        self.assertEqual(sidebar.title, group.name)
        self.assertEqual(sidebar.name, 'Group Menu')
        self.assertEqual(sidebar.search, True)


class FutureGroupSidebarTests(unittest.TestCase):

    def test_init(self):
        task = AddSubgroupCreateMethods().create_task()
        sidebar = FutureGroupSidebar(task)
        self.assertEqual(sidebar.title, task.task_name)
        self.assertEqual(sidebar.name, 'Group Menu')
        self.assertEqual(sidebar.search, True)
