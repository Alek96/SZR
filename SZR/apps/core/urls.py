from django.urls import path, re_path

from . import views

app_name = 'core'
urlpatterns = [
    path('init_navbar/', views.init_navbar, name='init_navbar'),
    path('init_navbar/<int:arg>/', views.init_navbar_arguments, name='init_navbar_arguments'),
    path('init_sidebar/', views.init_sidebar, name='init_sidebar'),
    path('init_sidebar/<int:arg>/', views.init_sidebar_arguments, name='init_sidebar_arguments'),
]
