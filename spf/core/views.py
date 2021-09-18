from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group, User
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from core.extdeps import event_manager
from core.models import (
    IngressPackage,
    Event
)
from core.forms import (
    CreateUserForm,
    UpdateUserForm
)
from core.decorators import (
    unauthenticated_user,
    allowed_users
)
from spf import settings
from opac_schema.v1.models import Journal as OPACJournal
from opac_schema.v2.models import ArticleFiles
from os import path

import dsm.ingress as dsm_ingress


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
                    _('Errors ocurred: (%(msg_key)s, %(msg_value)s)' % {'msg_key': key_err, 'msg_value': key_val[0]}),
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
def account_change_password_page(request):
    context = {}
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                _('Your password was updated'),
                extra_tags='alert alert-success'
            )
        else:
            for val in form.errors.values():
                messages.error(request, _(val[0]), extra_tags='alert alert-danger')
            context.update({
                'old_password': request.POST.get('old_password', ''),
                'new_password1': request.POST.get('new_password1', ''),
                'new_password2': request.POST.get('new_password2', ''),
                'form': form
                })
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', context=context)


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
                    _('Errors ocurred: (%(msg_key)s, %(msg_value)s)' % {'msg_key': key_err, 'msg_value': key_val[0]}),
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
def user_package_upload_page(request):
    if request.method == 'POST':
        file_input = request.FILES.get('package_file')
        # registra evento de envio de pacote novo
        ev = event_manager.register_event(
            request.user,
            Event.Name.UPLOAD_PACKAGE,
            str({'file_name': file_input.name})
        )

        if file_input:
            fs = FileSystemStorage(location=settings.MEDIA_INGRESS_TEMP)

            # envia arquivo para diretório temporário
            pkg_name = fs.save(file_input.name, file_input)

            # envia arquivo ao MinIO
            try:
                ingress_results = dsm_ingress.upload_package(path.join(fs.base_location, pkg_name))

                if len(ingress_results['errors']) > 0:
                    messages.error(request,
                                   _('Errors ocurred: %s') % ingress_results['errors'],
                                   extra_tags='alert alert-danger')
                    # registra o evento como completado com falha
                    ev = event_manager.update_event(ev, {'status': Event.Status.FAILED})
                else:
                    for d in ingress_results['docs']:
                        messages.success(request,
                                         _('Package (%(name)s, %(id)s) was added')
                                         % {'name': d['name'], 'id': d['id']},
                                         extra_tags='alert alert-success')
                    # registra o evento como completado com sucesso
                    ev = event_manager.update_event(ev, {'status': Event.Status.COMPLETED})

                    # registra o pacote enviado
                    ip = IngressPackage()
                    ip.user = request.user
                    ip.datetime = ev.datetime
                    ip.package_name = pkg_name
                    ip.status = IngressPackage.Status.RECEIVED
                    ip.save()
            except ValueError:
                messages.error(request,
                               pkg_name + _(' does not have a valid format. Please provide a zip file.'),
                               extra_tags='alert alert-danger')
                # registra o evento como completado com falha
                ev = event_manager.update_event(ev, {'status': Event.Status.FAILED})

            # remove arquivo de diretório temporário
            fs.delete(pkg_name)

    return render(request, 'core/user_package_upload.html')


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def user_package_download_page(request):
    pid = request.GET.get('pid', '')
    package_uri_results = {'pid': pid, 'doc_pkg': []}
    if pid:
        ev = event_manager.register_event(
            request.user,
            Event.Name.RETRIEVE_PACKAGE,
            str(str({'pid': pid}))
        )
        package_uri_results = dsm_ingress.get_package_uri_by_pid(pid)

        if len(package_uri_results['errors']) > 0:
            for e in package_uri_results['errors']:
                messages.error(
                    request,
                    e,
                    extra_tags='alert alert-danger')
            ev = event_manager.update_event(ev, {'status': Event.Status.FAILED})
        elif len(package_uri_results['doc_pkg']) == 0:
            messages.warning(
                request,
                _('No packages were found for document %s') % pid,
                extra_tags='alert alert-warning')
        else:
            ev = event_manager.update_event(ev, {'status': Event.Status.COMPLETED})

    return render(request, 'core/user_package_download.html', context={'pid': pid, 'pkgs': package_uri_results['doc_pkg']})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def user_groups_edit_page(request):
    user_list = User.objects.filter(is_superuser=False)
    available_groups = Group.objects.all()

    paginator = Paginator(user_list, 25)
    page_number = request.GET.get('page')
    user_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        ev = event_manager.register_event(request.user, Event.Name.CHANGE_USER_GROUPS)

        for u in user_obj:
            groups_names = request.POST.getlist('%s|user_groups' % u.username)
            user_groups = Group.objects.filter(name__in=groups_names)
            for ag in available_groups:
                if ag not in user_groups:
                    u.groups.remove(ag)

            for ug in user_groups:
                u.groups.add(ug)
            u.save()

        messages.success(request, _("Users' groups were updated"), extra_tags='alert alert-success')
        event_manager.update_event(ev, {'status': Event.Status.COMPLETED})

    return render(request, 'core/user_groups_edit.html', context={'user_obj': user_obj, 'available_groups': available_groups})
