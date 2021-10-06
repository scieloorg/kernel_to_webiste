from django.conf.urls import url
from django.urls import path
from . import views


general = [
    path('', views.index_page, name='index'),
    path('faq/', views.faq_page, name='faq'),
]

    path('user/groups/edit', views.user_groups_edit_page, name='user_groups_edit'),
    url(r'^[\s\S]*/update_status/$', views.update_status, name='update_status'),
]
