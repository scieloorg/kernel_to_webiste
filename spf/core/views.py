from core.extdeps import event_manager
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect

from dsm.ingress import get_package_uri_by_pid, upload_package
from spf import settings

from opac_schema.v1.models import Journal as OPACJournal
from opac_schema.v2.models import ArticleFiles

from .models import *
from .forms import CreateUserForm, UpdateUserForm
from .decorators import unauthenticated_user, allowed_users

import os


def _get_list_according_to_scope(request, model_class, filtering_field):
    request_scope = request.GET.get('scope', '')

    if request_scope == 'all_users' and 'manager' in [g.name for g in request.user.groups.all()]:
        return request_scope, model_class.objects.all().order_by('-datetime')
    else:
        return request_scope, model_class.objects.filter(**{filtering_field: request.user}).order_by('-datetime')


def index_page(request):
    return render(request, 'index.html')


def faq_page(request):
    return render(request, 'faq.html')


@login_required(login_url='login')
def user_profile_page(request):
    groups = request.user.groups.values_list('name', flat=True)
    return render(request, 'core/user_profile.html', context={'groups': groups})


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
            return redirect('user_profile_edit')
    return render(request, 'core/user_profile_edit.html', context={})


@login_required(login_url='login')
def activity_list_page(request):
    request_scope, event_list = _get_list_according_to_scope(request, Event, 'actor')

    paginator = Paginator(event_list, 25)
    page_number = request.GET.get('page')
    event_obj = paginator.get_page(page_number)

    return render(request, 'core/activity_list.html', context={'event_obj': event_obj, 'scope': request_scope})


@unauthenticated_user
def account_register_page(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,
                             _('User %s was created') % username,
                             extra_tags='alert alert-success')
            return redirect('login')
        else:
            for key_err, key_val in form.errors.items():
                messages.error(
                    request,
                    _('Errors ocurred: (%s ,%s)' % (key_err, key_val[0])),
                    extra_tags='alert alert-danger')

    context = {
        'username': request.POST.get('username', ''),
        'email': request.POST.get('email', ''),
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', '')
    }
    return render(request, 'accounts/register.html', context=context)


@unauthenticated_user
def account_login_page(request):
    context = {'username': ''}

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
            context['username'] = username

    return render(request, 'accounts/login.html', context=context)


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def user_add_page(request):
    context = {'user_groups': []}

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        groups_names = request.POST.getlist('user_groups')
        context.update({'user_groups': groups_names})

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            user = User.objects.get(username=username)

            user_groups = Group.objects.filter(name__in=groups_names)
            for u in user_groups:
                user.groups.add(u)
            user.save()

            messages.success(request,
                             _('User %s was created') % username,
                             extra_tags='alert alert-success')

        else:
            for key_err, key_val in form.errors.items():
                messages.error(
                    request,
                    _('Errors ocurred: (%s, %s)' % (key_err, key_val[0])),
                    extra_tags='alert alert-danger')

            context.update({
                'username': request.POST.get('username', ''),
                'email': request.POST.get('email', ''),
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', '')
            })

    context.update({'available_groups': Group.objects.all()})

    return render(request, 'accounts/add.html', context=context)


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def journal_list_page(request):
    journal_list = OPACJournal.objects.all()

    paginator = Paginator(journal_list, 25)
    page_number = request.GET.get('page')
    journal_obj = paginator.get_page(page_number)

    return render(request, 'core/journal_list.html', context={'journal_obj': journal_obj})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def deposited_package_list_page(request):
    request_scope, deposited_package_list = _get_list_according_to_scope(request, IngressPackage, 'user')

    paginator = Paginator(deposited_package_list, 25)
    page_number = request.GET.get('page')
    deposited_package_obj = paginator.get_page(page_number)

    return render(request, 'core/deposited_package_list.html', context={'deposited_package_obj': deposited_package_obj, 'scope': request_scope})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def article_files_list_page(request):
    article_files_list = ArticleFiles.objects.all().order_by('-updated')

    paginator = Paginator(article_files_list, 25)
    page_number = request.GET.get('page')
    article_files_obj = paginator.get_page(page_number)

    return render(request, 'core/article_files_list.html', context={'article_files_obj': article_files_obj})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def package_upload_page(request):
    context = {}
    if request.method == 'POST':
        file_input = request.FILES.get('package_file')
        # registra evento de envio de pacote novo
        ev = event_manager.register_event(
            request.user,
            event_manager.EventName.UPLOAD_PACKAGE,
            str({'file_name': file_input.name})
        )

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
                    ev = event_manager.update_event(ev, {'status': event_manager.EventStatus.FAILED})
                else:
                    for d in ingress_results['docs']:
                        messages.success(request,
                                         _('Package (%(name)s, %(id)s) was added')
                                         % {'name': d['name'], 'id': d['id']},
                                         extra_tags='alert alert-success')
                    ev = event_manager.update_event(ev, {'status': event_manager.EventStatus.COMPLETED})
            except ValueError:
                messages.error(request,
                               _('%s does not have a valid format. Please provide a zip file.') % pkg_name,
                               extra_tags='alert alert-danger')
                ev = event_manager.update_event(ev, {'status': event_manager.EventStatus.FAILED})

            # remove arquivo de diretório temporário
            fs.delete(pkg_name)

    return render(request, 'core/user_package_upload.html', context=context)


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def package_download_page(request):
    pid = request.GET.get('pid')
    package_uri_results = {'pid': pid, 'doc_pkg': []}
    if pid:
        ev = event_manager.register_event(
            request.user,
            event_manager.EventName.RETRIEVE_PACKAGE_DATA,
            str(str({'pid': pid}))
        )
        package_uri_results = get_package_uri_by_pid(pid)

        if len(package_uri_results['errors']) > 0:
            for e in package_uri_results['errors']:
                messages.error(
                    request,
                    e,
                    extra_tags='alert alert-danger')
            ev = event_manager.update_event(ev, {'status': event_manager.EventStatus.FAILED})
        elif len(package_uri_results['doc_pkg']) == 0:
            messages.warning(
                request,
                _('No packages were found for document %s') % pid,
                extra_tags='alert alert-warning')
        else:
            ev = event_manager.update_event(ev, {'status': event_manager.EventStatus.COMPLETED})

    return render(request, 'core/user_package_download.html', context={'pid': pid, 'pkgs': package_uri_results['doc_pkg']})


class SearchResultsView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'core.view_document'
    model = Document
    template_name = 'core/search_results.html'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('pid')
        object_list = Document.objects.filter(pid__icontains=query)
        return object_list
