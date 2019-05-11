from django.urls import path

from . import views

app_name = 'groups'
urlpatterns = [
    path('<int:group_id>/init_sidebar/', views.init_sidebar, name='init_sidebar'),

    path('', views.roots, name='index'),

    path('new/', views.new_group, name='new_group'),
    path('<int:group_id>/', views.detail, name='detail'),
    path('<int:group_id>/new/', views.new_subgroup, name='new_subgroup'),
    path('<int:group_id>/project/new/', views.new_project, name='new_project'),

    path('<int:group_id>/members/', views.members, name='members'),
    path('<int:group_id>/members/new/', views.new_member, name='new_member'),

    path('<int:group_id>/tasks/', views.tasks, name='tasks'),
    path('<int:group_id>/tasks/task_group/new/', views.new_task_group, name='new_task_group'),
    path('<int:group_id>/tasks/add_subgroup/new/', views.new_subgroup_task, name='new_subgroup_task'),
    path('<int:group_id>/tasks/add_project/new/', views.new_project_task, name='new_project_task'),
    path('<int:group_id>/tasks/add_member/new/', views.new_member_task, name='new_member_task'),
    path('<int:group_id>/tasks/add_member/new_members_from_file/', views.new_members_from_file,
         name='new_members_from_file'),
    path('<int:group_id>/tasks/add_member/new_subgroup_and_members_from_file/',
         views.new_subgroup_and_members_from_file, name='new_subgroup_and_members_from_file'),

    path('tasks/task_group/<int:task_group_id>/edit/', views.edit_task_group, name='edit_task_group'),
    path('tasks/task_group/<int:task_group_id>/add_subgroup/new/', views.new_subgroup_task, name='new_subgroup_task'),
    path('tasks/task_group/<int:task_group_id>/add_project/new/', views.new_project_task, name='new_project_task'),
    path('tasks/task_group/<int:task_group_id>/add_member/new/', views.new_member_task, name='new_member_task'),

    path('tasks/add_project/<int:task_id>/edit/', views.edit_project_task, name='edit_project_task'),
    path('tasks/add_member/<int:task_id>/edit/', views.edit_member_task, name='edit_member_task'),

    path('tasks/add_subgroup/<int:task_id>/edit/', views.edit_subgroup_task, name='edit_subgroup_task'),
    path('tasks/add_subgroup/<int:task_id>/', views.future_group_detail, name='future_group_detail'),
    path('tasks/add_subgroup/<int:task_id>/members/', views.future_group_members, name='future_group_members'),
    path('tasks/add_subgroup/<int:task_id>/tasks/', views.future_group_tasks, name='future_group_tasks'),
    path('tasks/add_subgroup/<int:task_id>/task_group/new', views.new_task_group, name='new_task_group'),
    path('tasks/add_subgroup/<int:task_id>/add_subgroup/new', views.new_subgroup_task, name='new_subgroup_task'),
    path('tasks/add_subgroup/<int:task_id>/add_project/new', views.new_project_task, name='new_project_task'),
    path('tasks/add_subgroup/<int:task_id>/add_member/new', views.new_member_task, name='new_member_task'),
    path('tasks/add_subgroup/<int:task_id>/add_member/new_members_from_file', views.new_members_from_file,
         name='new_members_from_file'),
    path('tasks/add_subgroup/<int:task_id>/add_member/new_subgroup_and_members_from_file',
         views.new_subgroup_and_members_from_file, name='new_subgroup_and_members_from_file'),

    path('ajax/load-subgroups/<int:group_id>/', views.ajax_load_subgroups, name='ajax_load_subgroups'),
    path('ajax/load-subgroups-and-projects/<int:group_id>/', views.ajax_load_subgroups_and_projects,
         name='ajax_load_subgroups_and_projects'),

    # path('delete/<int:group_id>/', views.delete_group, name='delete_group'),
]
