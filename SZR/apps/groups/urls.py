from django.urls import path, re_path

from . import views

app_name = 'groups'
urlpatterns = [
    # path('init_sidebar', views.init_sidebar, name='init_sidebar'),

    path('', views.groups_index, name='index'),
    path('<int:group_id>', views.group_detail_index, name='group_detail_index'),

    path('new/', views.new_group, name='new_group'),
    path('<int:group_id>/new/', views.new_subgroup, name='new_subgroup'),
    path('<int:group_id>/members/', views.group_members, name='group_members'),

    path('ajax/load-subgroups/<int:group_id>/', views.ajax_load_subgroups, name='ajax_load_subgroups'),
    path('ajax/load-subgroups-and-projects/<int:group_id>/', views.ajax_load_subgroups_and_projects,
         name='ajax_load_subgroups_and_projects'),

    # path('new/<int:group_id>/', views.create_subgroup, name='create_subgroup'),
    # path('delete/<int:group_id>/', views.delete_group, name='delete_group'),
]
