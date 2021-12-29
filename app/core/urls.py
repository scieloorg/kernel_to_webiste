from django.conf.urls import url
from django.views.i18n import JavaScriptCatalog
from django.urls import path
from django.views.generic import TemplateView
from . import views


general = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
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

ingress = [
    path('ingress/package_upload/', views.ingress_package_upload_page, name='ingress_package_upload'),
    path('ingress/package_download/', views.ingress_package_download_page, name='ingress_package_download'),
    path('ingress/package_list/', views.ingress_package_list_page, name='ingress_package_list'),
]

journal = [
    path('journal/list/', views.journal_list_page, name='journal_list'),
]

tracking = [
    url(r'^event/(?P<eid>[\d-]+)/$', views.event_status, name='event'),
    path('event/list/', views.event_list_page, name='event_list'),
    path('task/update_status/', views.task_update_status, name='task_update_status'),
]

migration = [
    path('migration/documents/identify', views.migrate_identify_documents, name='migrate_identify_documents_list'),
    path('migration/documents/list', views.migrate_search_pending_documents_page, name='migrate_search_pending_documents'),
    path('migration/journals/list', views.migrate_pending_documents_by_journal_list_page, name='migrate_pending_documents_by_journal_list'),
    path('migration/issue/list', views.migrate_pending_documents_by_issue_list_page, name='migrate_pending_documents_by_issue_list'),
    path('migration/isis_db', views.migrate_isis_db_page, name='migrate_isis_db'),
]

javascript_catalog = [path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog')]

urlpatterns = general + user + ingress + journal +  tracking + migration + javascript_catalog
