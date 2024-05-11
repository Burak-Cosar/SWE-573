from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('search/', views.search, name='search'),
    path('create/', views.create_community, name='create_community'),
    path('community/<int:community_id>/', views.community_content, name='community_content'),
    path('community/<int:community_id>/join/', views.join_community, name='join_community'),
    path('community/<int:community_id>/leave/', views.leave_community, name='leave_community'),
    path('community/', views.list_communities, name='list_communities'),
    path('community/<int:community_id>/manage/', views.manage_community, name='manage_community'),
    path('community/<int:community_id>/manage/create_template', views.create_template, name='create_template'),
    path('community/<int:community_id>/posts/<int:template_id>/create', views.create_post, name='create_post'),
    path('community/<int:community_id>/posts/<int:post_id>/', views.view_post, name='view_post'),
    path('community/<int:community_id>/manage/invite_users', views.invite_users, name='invite_users'),
    path('users/<int:user_id>', views.view_user, name='view_user'),
    path('code_of_conduct', views.conduct, name='conduct'),
]