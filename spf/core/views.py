from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from django.views import generic

from dsm.ingress import get_package_uri_by_pid, upload_package
from spf import settings

from .models import *
from .forms import CreateUserForm, UpdateUserForm
from .decorators import unauthenticated_user, allowed_users

import os


def index_page(request):
    return render(request, 'index.html', context={})


def faq_page(request):
    return render(request, 'faq.html', context={})


@login_required(login_url='login')
def user_profile_page(request):
    return render(request, 'core/user_profile.html', context={})


@login_required(login_url='login')
def user_profile_edit_page(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,
                             _('User %s was updated') % username,
                             extra_tags='alert alert-success')
            return redirect('user_dashboard')
    return render(request, 'core/user_profile_edit.html', context={})


@login_required(login_url='login')
def user_dashboard_page(request):
    groups = request.user.groups.values_list('name', flat=True)
    return render(request, 'core/user_dashboard.html', context={'groups': groups})


@unauthenticated_user
def account_register_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,
                             _('User %s was created') % username,
                             extra_tags='alert alert-success')
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context=context)


@unauthenticated_user
def account_login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request,
                          _('Incorrect username or password'),
                          extra_tags='alert alert-danger')

    return render(request, 'accounts/login.html', context={})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def user_add_page(request):
    return redirect('user_add')


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def journal_list_page(request):
    journal_list = Journal.objects.all()
    return render(request, 'core/journal_list.html', context={'journal_list': journal_list})


@login_required(login_url='login')
def article_list_page(request):
    article_list = {}

    return render(request, 'core/article_list.html', context={'article_list': article_list})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def package_upload_page(request):
    context = {}
    if request.method == 'POST':
        file_input = request.FILES.get('package_file')

        if file_input:
            fs = FileSystemStorage(location=settings.MEDIA_INGRESS_TEMP)

            # envia arquivo para diretório temporário
            pkg_name = fs.save(file_input.name, file_input)

            # envia arquivo ao MinIO
            try:
                ingress_results = upload_package(os.path.join(fs.base_location, pkg_name))

                if len(ingress_results['errors']) > 0:
                    messages.error(request,
                                   _('Errors ocurred: %s') % ingress_results['errors'],
                                   extra_tags='alert alert-danger')
                else:
                    for d in ingress_results['docs']:
                        messages.success(request,
                                         _('Package (%s, %s) was added')
                                         % (d['name'], d['id']),
                                         extra_tags='alert alert-success')

            except ValueError:
                messages.error(request,
                               _('%s has not a valid format. Please provide a zip file.') % pkg_name,
                               extra_tags='alert alert-danger')

            # remove arquivo de diretório temporário
            fs.delete(pkg_name)

    return render(request, 'core/user_package_upload.html', context=context)


@login_required(login_url='login')
def package_download_page(request):
    pid = request.GET.get('pid')
    package_uri_results = {'pid': pid, 'doc_pkg': []}
    if pid:
        package_uri_results = get_package_uri_by_pid(pid)
        if len(package_uri_results['doc_pkg']) == 0:
            messages.warning(request,
                             _('No packages were found for document %s') % pid,
                             extra_tags='alert alert-warning')
    return render(request, 'core/user_package_download.html', context={'pid': pid, 'pkgs': package_uri_results['doc_pkg']})


class DepositedPackagesByUserListView(LoginRequiredMixin, generic.ListView):
    login_url = 'login'
    model = Package
    template_name = 'core/user_package_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Package.objects.filter(depositor=self.request.user)


class DepositedPackagesListView(LoginRequiredMixin, generic.ListView):
    login_url = 'login'
    model = Package
    template_name = 'core/package_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Package.objects.all()


class JournalsListView(LoginRequiredMixin, generic.ListView):
    login_url = 'login'
    model = Journal
    template_name = 'core/journal_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Journal.objects.all()


class SearchResultsView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'core.view_document'
    model = Document
    template_name = 'core/search_results.html'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('pid')
        object_list = Document.objects.filter(pid__icontains=query)
        return object_list
