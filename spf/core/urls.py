from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_page, name='index'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    path('register/', views.account_register_page, name='register'),
    path('login/', views.account_login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('faq/', views.faq_page, name='faq'),
    path('package/list', views.DepositedPackagesListView.as_view(), name='package_list'),
    path('package/search', views.package_search_results_page, name='package_search'),
    path('journal/list', views.journal_list_page, name='journal_list'),
    path('article/list', views.article_list_page, name='article_list'),
    path('user/add', views.user_add_page, name='user_add'),
    path('user/dashboard', views.user_dashboard_page, name='user_dashboard'),
    path('user/package/list', views.DepositedPackagesByUserListView.as_view(), name='user_package_list'),
    path('user/package/upload', views.package_upload_page, name='user_package_upload'),
    path('user/package/search', views.package_search_results_page, name='user_package_search_results'),
    path('user/profile', views.user_profile_page, name='user_profile'),
    path('user/profile/edit', views.user_profile_edit_page, name='user_profile_edit'),
]
