from django.urls import path

from . import views

app_name = 'projects'
urlpatterns = [
    path('<int:project_id>/init_sidebar/', views.init_sidebar, name='init_sidebar'),

    path('', views.roots, name='index'),

    # path('new/', views.new_project, name='new_project'),
    path('<int:project_id>/', views.detail, name='detail'),

    path('<int:project_id>/members/', views.members, name='members'),
    path('<int:project_id>/members/new/', views.new_member, name='new_member'),

    path('<int:project_id>/tasks/', views.tasks, name='tasks'),
    path('<int:project_id>/tasks/task_group/new/', views.new_task_group, name='new_task_group'),
    path('<int:project_id>/tasks/add_member/new/', views.new_member_task, name='new_member_task'),

    path('tasks/task_group/<int:task_group_id>/edit/', views.edit_task_group, name='edit_task_group'),
    path('tasks/task_group/<int:task_group_id>/add_member/new/', views.new_member_task, name='new_member_task'),

    path('tasks/add_member/<int:task_id>/edit/', views.edit_member_task, name='edit_member_task'),

    path('tasks/add_project/<int:task_id>/edit/', views.edit_project_task, name='edit_project_task'),
    path('tasks/add_project/<int:task_id>/', views.future_project_detail, name='future_project_detail'),
    path('tasks/add_project/<int:task_id>/members/', views.future_project_members, name='future_project_members'),
    path('tasks/add_project/<int:task_id>/tasks/', views.future_project_tasks, name='future_project_tasks'),
    path('tasks/add_project/<int:task_id>/task_group/new', views.new_task_group, name='new_task_group'),
    path('tasks/add_project/<int:task_id>/add_member/new', views.new_member_task, name='new_member_task'),

    # path('delete/<int:project_id>/', views.delete_group, name='delete_group'),
]
