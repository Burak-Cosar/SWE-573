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
    path('community/<int:community_id>/templates/', views.manage_templates, name='manage_templates'),
    path('community/<int:community_id>/templates/create', views.create_template, name='create_template'),
    path('community/<int:community_id>/posts/<int:template_id>/create', views.create_post, name='create_post'),
    path('community/<int:community_id>/posts/<int:post_id>/', views.view_post, name='view_post'),

]