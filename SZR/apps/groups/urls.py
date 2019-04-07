from django.urls import path

from . import views

app_name = 'groups'
urlpatterns = [
    path('<int:group_id>/init_sidebar/', views.init_sidebar, name='init_sidebar'),

    path('', views.roots, name='index'),

    path('new/', views.new_group, name='new_group'),
    path('<int:group_id>/', views.detail, name='detail'),
    path('<int:group_id>/new/', views.new_subgroup, name='new_subgroup'),

    path('<int:group_id>/members/', views.members, name='members'),
    path('<int:group_id>/members/new/', views.new_member, name='new_member'),

    path('<int:group_id>/tasks/', views.tasks, name='tasks'),

    path('<int:group_id>/tasks/add_subgroup_group/new/', views.new_subgroup_group, name='new_subgroup_group'),
    path('tasks/add_subgroup_group/<int:task_group_id>/new/', views.new_subgroup_task, name='new_subgroup_task'),
    path('tasks/add_subgroup_group/<int:task_group_id>/edit/', views.edit_subgroup_group, name='edit_subgroup_group'),
    path('tasks/add_subgroup/<int:task_id>/edit/', views.edit_subgroup_task, name='edit_subgroup_task'),

    path('<int:group_id>/tasks/add_member_group/new/', views.new_member_group, name='new_member_group'),
    path('tasks/add_member_group/<int:task_group_id>/new/', views.new_member_task, name='new_member_task'),
    path('tasks/add_member_group/<int:task_group_id>/edit/', views.edit_member_group, name='edit_member_group'),
    path('tasks/add_member/<int:task_id>/edit/', views.edit_member_task, name='edit_member_task'),

    path('tasks/add_subgroup/<int:task_id>/', views.future_group_detail, name='future_group_detail'),
    path('tasks/add_subgroup/<int:task_id>/members/', views.future_group_members, name='future_group_members'),
    path('tasks/add_subgroup/<int:task_id>/tasks/', views.future_group_tasks, name='future_group_tasks'),
    path('tasks/add_subgroup/<int:task_id>/add_subgroup_group', views.new_subgroup_group, name='new_subgroup_group'),
    path('tasks/add_subgroup/<int:task_id>/add_member_group', views.new_member_group, name='new_member_group'),

    path('ajax/load-subgroups/<int:group_id>/', views.ajax_load_subgroups, name='ajax_load_subgroups'),
    path('ajax/load-subgroups-and-projects/<int:group_id>/', views.ajax_load_subgroups_and_projects,
         name='ajax_load_subgroups_and_projects'),

    # path('delete/<int:group_id>/', views.delete_group, name='delete_group'),
]
