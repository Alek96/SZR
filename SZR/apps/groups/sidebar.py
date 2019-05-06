from core import sidebar
from django.urls import reverse


class GroupSidebar(sidebar.Sidebar):
    def __init__(self, group, **kwargs):
        super().__init__(
            title=group.name,
            name='Group Menu',
            search=True,
            **kwargs)
        self.points = [
            sidebar.Point(
                name='Overview',
                icon=sidebar.HomeIcon(),
                active=True,
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('groups:detail', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='Add Subgroup',
                        url=sidebar.Url(url=reverse('groups:new_subgroup', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='Add Project',
                        url=sidebar.Url(url=reverse('groups:new_project', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='GitLab',
                        url=sidebar.NewPageUrl(url=group.web_url)),
                ]),
            sidebar.Point(
                name='Members',
                icon=sidebar.UsersIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('groups:members', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='Add Member',
                        url=sidebar.Url(url=reverse('groups:new_member', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='GitLab'),
                ]),
            sidebar.Point(
                name='Tasks',
                icon=sidebar.TasksIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('groups:tasks', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='New Task Group',
                        url=sidebar.Url(url=reverse('groups:new_task_group', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='Add Subgroups',
                        url=sidebar.Url(url=reverse('groups:new_subgroup_task', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='Add Project',
                        url=sidebar.Url(url=reverse('groups:new_project_task', kwargs={'group_id': group.id}))),
                    sidebar.Point(
                        name='Add Members',
                        url=sidebar.Url(url=reverse('groups:new_member_task', kwargs={'group_id': group.id}))),
                ]),
            sidebar.Point(
                name='Setting',
                icon=sidebar.SettingIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details'),
                    sidebar.Point(
                        name='Edit'),
                    sidebar.Point(
                        name='Delete'),
                ]),
        ]


class FutureGroupSidebar(sidebar.Sidebar):
    def __init__(self, task, **kwargs):
        super().__init__(
            title=task.get_name,
            name='Group Menu',
            search=True,
            **kwargs)
        self.points = [
            sidebar.Point(
                name='Overview',
                icon=sidebar.HomeIcon(),
                active=True,
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('groups:future_group_detail', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Add Subgroups',
                        url=sidebar.Url(url=reverse('groups:new_subgroup_task', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Add Project',
                        url=sidebar.Url(url=reverse('groups:new_project_task', kwargs={'task_id': task.id}))),
                ]),
            sidebar.Point(
                name='Members',
                icon=sidebar.UsersIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('groups:future_group_members', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Add Members',
                        url=sidebar.Url(url=reverse('groups:new_member_task', kwargs={'task_id': task.id}))),
                ]),
            sidebar.Point(
                name='Tasks',
                icon=sidebar.TasksIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('groups:future_group_tasks', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='New Task Group',
                        url=sidebar.Url(url=reverse('groups:new_task_group', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Add Subgroups',
                        url=sidebar.Url(url=reverse('groups:new_subgroup_task', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Add Project',
                        url=sidebar.Url(url=reverse('groups:new_project_task', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Add Members',
                        url=sidebar.Url(url=reverse('groups:new_member_task', kwargs={'task_id': task.id}))),
                ]),
            sidebar.Point(
                name='Setting',
                icon=sidebar.SettingIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details'),
                    sidebar.Point(
                        name='Edit',
                        url=sidebar.Url(url=reverse('groups:edit_subgroup_task', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Delete'),
                ]),
        ]
