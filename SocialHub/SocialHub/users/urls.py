from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('login_user', views.login_user, name="login"),
    path('logout_user', views.logout_user, name="logout"),
    path('register_user', views.register_user, name="register_user"),
    path('profile', views.view_profile, name="view_profile"),
]