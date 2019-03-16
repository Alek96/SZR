from django.urls import path
from django.contrib.auth import views as auth_views

from core import views

app_name = 'core'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path('login/gitlab/', views.login_gitlab, name="login_gitlab"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
