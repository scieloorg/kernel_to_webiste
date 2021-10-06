from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.urls import reverse
from django.http.response import HttpResponseRedirect, JsonResponse
from django.utils.translation import gettext as _
from django.shortcuts import render, redirect
from core.forms import CreateUserForm, UpdateUserForm
from core.decorators import unauthenticated_user, allowed_users
from core.models import Event
from core.tasks import task_get_package_uri_by_pid
from spf import settings
from os import path

import core.controller as controller
import dsm.ingress as dsm_ingress


###################
### general views #
###################
def index_page(request):
    return render(request, 'index.html')


def faq_page(request):
    return render(request, 'faq.html')


################
### user views #
################
@unauthenticated_user
def user_register_page(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,
                             _('User %s was created') % username,
                             extra_tags='alert-success')
            return redirect('login')
        else:
            for val in form.errors.values():
                messages.error(request, _(val[0]), extra_tags='alert-danger')
    context = {
        'username': request.POST.get('username', ''),
        'email': request.POST.get('email', ''),
        'first_name': request.POST.get('first_name', ''),
        'last_name': request.POST.get('last_name', '')
    }
    return render(request, 'user/register.html', context=context)


@unauthenticated_user
def user_login_page(request):
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
                          extra_tags='alert-danger')
            context['username'] = username

    return render(request, 'user/login.html', context=context)


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')


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
            user = controller.get_user_from_username(username)
            user_groups = controller.get_groups_from_groups_names(groups_names)
            controller.update_user_groups(user, user_groups)

            messages.success(request,
                             _('User %s was created') % username,
                             extra_tags='alert-success')

        else:
            for val in form.errors.values():
                messages.error(request, _(val[0]), extra_tags='alert-danger')

            context.update({
                'username': request.POST.get('username', ''),
                'email': request.POST.get('email', ''),
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', '')
            })

    context.update({'available_groups': controller.get_groups()})

    return render(request, 'user/add.html', context=context)


@login_required(login_url='login')
def user_change_password_page(request):
    context = {}
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                _('Your password was updated'),
                extra_tags='alert-success'
            )
        else:
            for val in form.errors.values():
                messages.error(request, _(val[0]), extra_tags='alert-danger')
            context.update({
                'old_password': request.POST.get('old_password', ''),
                'new_password1': request.POST.get('new_password1', ''),
                'new_password2': request.POST.get('new_password2', ''),
                'form': form
                })
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'user/change_password.html', context=context)


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def user_groups_edit_page(request):
    user_list = controller.get_users()
    available_groups = controller.get_groups()

    paginator = Paginator(user_list, 25)
    page_number = request.GET.get('page')
    user_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        ev = controller.add_event(request.user, Event.Name.CHANGE_USER_GROUPS)

        for u in user_obj:
            groups_names = request.POST.getlist('%s|user_groups' % u.username)
            user_groups = controller.get_groups_from_groups_names(groups_names)
            controller.update_user_groups(u, user_groups)

        messages.success(request, _("Users' groups were updated"), extra_tags='alert-success')
        controller.update_event(ev, {'status': Event.Status.COMPLETED})

    return render(request, 'user/groups_edit.html', context={'user_obj': user_obj, 'available_groups': available_groups})


@login_required(login_url='login')
def user_profile_page(request):
    groups_names = controller.get_groups_names_from_user(request.user)
    return render(request, 'user/profile.html', context={'groups': groups_names})


@login_required(login_url='login')
def user_profile_edit_page(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,
                             _('User %s was updated') % username,
                             extra_tags='alert-success')
            return redirect('user_profile_edit')
    return render(request, 'user/profile_edit.html', context={})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def user_package_upload_page(request):
    if request.method == 'POST':
        file_input = request.FILES.get('package_file')
        # registra evento de envio de pacote novo
        ev = controller.add_event(request.user, Event.Name.UPLOAD_PACKAGE, {'file_name': file_input.name})

        if file_input:
            fs = FileSystemStorage(location=settings.MEDIA_INGRESS_TEMP)

            # envia arquivo para diretório temporário
            pkg_name = fs.save(file_input.name, file_input)

            # envia arquivo ao MinIO
            try:
                file_path = path.join(fs.base_location, pkg_name)
                ingress_results = dsm_ingress.upload_package(file_path)

                if len(ingress_results['errors']) > 0:
                    messages.error(request,
                                   _('Errors ocurred: %s') % ingress_results['errors'],
                                   extra_tags='alert-danger')
                    # registra o evento como completado com falha
                    ev = controller.update_event(ev, {'status': Event.Status.FAILED})
                else:
                    for d in ingress_results['docs']:
                        messages.success(request,
                                         _('Package (%(name)s, %(id)s) was added')
                                         % {'name': d['name'], 'id': d['id']},
                                         extra_tags='alert-success')
                    # registra o evento como completado com sucesso
                    ev = controller.update_event(ev, {'status': Event.Status.COMPLETED})

                    # registra o pacote enviado
                    controller.add_ingress_package(request.user, ev.datetime, pkg_name)
            except ValueError:
                messages.error(request,
                               pkg_name + _(' does not have a valid format. Please provide a zip file.'),
                               extra_tags='alert-danger')
                # registra o evento como completado com falha
                ev = controller.update_event(ev, {'status': Event.Status.FAILED})

            # remove arquivo de diretório temporário
            fs.delete(pkg_name)

    return render(request, 'core/user_package_upload.html')


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def user_package_download_page(request):
    pid = request.GET.get('pid', '')
    job_id = request.GET.get('job', '')

    # Há task sendo executada: renderiza template para mostrar resultados (ou aguardar por eles)
    if job_id:
        job = AsyncResult(job_id)

        context = {
            'pid': pid,
            'check_status': 1,
            'data': '',
            'state': 'STARTING',
            'task_id': job_id
        }
        return render(request, 'core/user_package_download.html', context)

    # Inicializa task para o PID informado e redireciona para a própria página aguardando resultado
    elif pid:
        job = task_get_package_uri_by_pid.delay(pid)
        return HttpResponseRedirect(reverse('user_package_download') + '?job=' + job.id + '&pid=' + pid)

    # Abre template pela primeira vez para digitar PID
    return render(request, 'core/user_package_download.html')


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager'])
def user_groups_edit_page(request):
    user_list = controller.get_users()
    available_groups = controller.get_groups()

    paginator = Paginator(user_list, 25)
    page_number = request.GET.get('page')
    user_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        ev = controller.add_event(request.user, Event.Name.CHANGE_USER_GROUPS)

        for u in user_obj:
            groups_names = request.POST.getlist('%s|user_groups' % u.username)
            user_groups = controller.get_groups_from_groups_names(groups_names)
            controller.update_user_groups(u, user_groups)

        messages.success(request, _("Users' groups were updated"), extra_tags='alert-success')
        controller.update_event(ev, {'status': Event.Status.COMPLETED})

    return render(request, 'core/user_groups_edit.html', context={'user_obj': user_obj, 'available_groups': available_groups})
