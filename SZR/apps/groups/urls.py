from django.urls import path, re_path

from . import views

app_name = 'groups'
urlpatterns = [
    path('<int:group_id>/init_sidebar/', views.init_sidebar, name='init_sidebar'),

    path('', views.groups_roots, name='index'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('<int:group_id>/members/', views.group_members, name='group_members'),

    path('new/', views.new_group, name='new_group'),
    path('<int:group_id>/new/', views.new_subgroup, name='new_subgroup'),

    path('ajax/load-subgroups/<int:group_id>/', views.ajax_load_subgroups, name='ajax_load_subgroups'),
    path('ajax/load-subgroups-and-projects/<int:group_id>/', views.ajax_load_subgroups_and_projects,
         name='ajax_load_subgroups_and_projects'),

    # path('delete/<int:group_id>/', views.delete_group, name='delete_group'),
]
