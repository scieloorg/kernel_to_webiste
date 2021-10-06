from django.conf.urls import url
from django.urls import path
from . import views


general = [
    path('', views.index_page, name='index'),
    path('faq/', views.faq_page, name='faq'),
]

user = [
    path('register/', views.user_register_page, name='register'),
    path('login/', views.user_login_page, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('user/add/', views.user_add_page, name='user_add'),
    path('user/change_password/', views.user_change_password_page, name='user_change_password'),
    path('user/groups/edit', views.user_groups_edit_page, name='user_groups_edit'),
    path('user/profile/', views.user_profile_page, name='user_profile'),
    path('user/profile/edit/', views.user_profile_edit_page, name='user_profile_edit'),
]
