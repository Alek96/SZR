from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'authentication'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="authentication/login.html"), name="login"),
    path('login/gitlab/', views.login_gitlab, name="login_gitlab"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
