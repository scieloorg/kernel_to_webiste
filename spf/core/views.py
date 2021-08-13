from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import query
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic.list import ListView

from .models import Document, Journal, Package
from .forms import CreateUserForm, UpdateUserForm
from .decorators import unauthenticated_user, allowed_users


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
            messages.success(request, _('User %s was updated') % username)
            return redirect('user_dashboard')
    return render(request, 'core/user_profile_edit.html', context={})


@login_required(login_url='login')
def user_dashboard_page(request):
    return render(request, 'core/user_dashboard.html', context={})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def journal_list_page(request):
    num_journals = Journal.objects.all().count()
    context = {'num_journals': num_journals}

    return render(request, 'core/journal_list.html', context=context)


@unauthenticated_user
def account_register_page(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, _('User %s was created') % username)
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
            messages.info(request, _('Incorrect username or password'))

    return render(request, 'accounts/login.html', context={})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def user_add_page(request):
    return redirect('user_add')


def logout_user(request):
    logout(request)
    return redirect('login')


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
class SearchResultsView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'core.view_document'
    model = Document
    template_name = 'core/search_results.html'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('pid')
        object_list = Document.objects.filter(pid__icontains=query)
        return object_list
