from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_page, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('user/', views.user_page, name='user'),
    path('journals/', views.journals_page, name='journals'),
]
