from core import sidebar
from django.urls import reverse


class ProjectSidebar(sidebar.Sidebar):
    def __init__(self, project, **kwargs):
        super().__init__(
            title=project.name,
            name='Project Menu',
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
                        url=sidebar.Url(url=reverse('projects:detail', kwargs={'project_id': project.id}))),
                    sidebar.Point(
                        name='GitLab',
                        url=sidebar.NewPageUrl(url=project.web_url)),
                ]),
            sidebar.Point(
                name='Members',
                icon=sidebar.UsersIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('projects:members', kwargs={'project_id': project.id}))),
                    sidebar.Point(
                        name='Add Member',
                        url=sidebar.Url(url=reverse('projects:new_member', kwargs={'project_id': project.id}))),
                    sidebar.Point(
                        name='GitLab'),
                ]),
            sidebar.Point(
                name='Tasks',
                icon=sidebar.TasksIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('projects:tasks', kwargs={'project_id': project.id}))),
                    sidebar.Point(
                        name='New Task Group',
                        url=sidebar.Url(url=reverse('projects:new_task_group', kwargs={'project_id': project.id}))),
                    sidebar.Point(
                        name='Add Member',
                        url=sidebar.Url(url=reverse('projects:new_member_task', kwargs={'project_id': project.id}))),
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


class FutureProjectSidebar(sidebar.Sidebar):
    def __init__(self, task, **kwargs):
        super().__init__(
            title=task.get_name,
            name='Project Menu',
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
                        url=sidebar.Url(url=reverse('projects:future_project_detail', kwargs={'task_id': task.id}))),
                ]),
            sidebar.Point(
                name='Members',
                icon=sidebar.UsersIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('projects:future_project_members', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Add Members',
                        url=sidebar.Url(url=reverse('projects:new_member_task', kwargs={'task_id': task.id}))),
                ]),
            sidebar.Point(
                name='Tasks',
                icon=sidebar.TasksIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details',
                        url=sidebar.Url(url=reverse('projects:future_project_tasks', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='New Task Group',
                        url=sidebar.Url(url=reverse('projects:new_task_group', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Add Member',
                        url=sidebar.Url(url=reverse('projects:new_member_task', kwargs={'task_id': task.id}))),
                ]),
            sidebar.Point(
                name='Setting',
                icon=sidebar.SettingIcon(),
                sub_points=[
                    sidebar.Point(
                        name='Details'),
                    sidebar.Point(
                        name='Edit',
                        url=sidebar.Url(url=reverse('groups:edit_project_task', kwargs={'task_id': task.id}))),
                    sidebar.Point(
                        name='Delete'),
                ]),
        ]
