from django.conf.urls import url
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_page, name='index'),
    path('register/', views.account_register_page, name='register'),
    path('login/', views.account_login_page, name='login'),
    path('change-password/', views.account_change_password_page, name='change_password'),
    path('logout/', views.logout_user, name='logout'),
    path('faq/', views.faq_page, name='faq'),
    path('article/files/list', views.article_files_list_page, name='article_files_list'),
    path('package/list', views.deposited_package_list_page, name='package_list'),
    path('event/list', views.event_list_page, name='event_list'),
    path('journal/list', views.journal_list_page, name='journal_list'),
    path('user/add', views.user_add_page, name='user_add'),
    path('user/package/upload', views.user_package_upload_page, name='user_package_upload'),
    path('user/package/download', views.user_package_download_page, name='user_package_download'),
    path('user/profile', views.user_profile_page, name='user_profile'),
    path('user/profile/edit', views.user_profile_edit_page, name='user_profile_edit'),
    path('user/groups/edit', views.user_groups_edit_page, name='user_groups_edit'),
    url(r'^[\s\S]*/update_status/$', views.update_status, name='update_status'),
]
