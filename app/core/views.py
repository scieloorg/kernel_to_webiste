from celery.result import AsyncResult

from core.decorators import (
    unauthenticated_user,
    allowed_users,
)
from core.forms import (
    CreateUserForm,
    UpdateUserForm,
)
from core.models import Event
from core.tasks import (
    task_get_package_uri_by_pid,
    task_migrate_acron,
    task_migrate_documents,
    task_migrate_identify_documents,
    task_migrate_isis_db,
    task_ingress_package,
)
from core.utils import package_name_is_valid

from datetime import datetime

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login, logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.http.response import (
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import (
    render,
    redirect,
)
from django.urls import reverse
from django.utils.translation import gettext as _

from dsm.extdeps.isis_migration.migration_models import ISISDocument

from opac_schema.v1.models import Issue as OPACIssue

from spf import settings

import core.controller as controller
import dsm.ingress as dsm_ingress
import dsm.migration as dsm_migration
import math
import os


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


#################
# ingress views #
#################
@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def ingress_package_upload_page(request):
    if request.method == 'POST':
        file_input = request.FILES.get('package_file')

        if file_input:
            fs = FileSystemStorage(location=settings.MEDIA_INGRESS_TEMP)

            if package_name_is_valid(file_input.name):
                # envia arquivo para diretório temporário
                pkg_name = fs.save(file_input.name, file_input)

                file_path = os.path.join(fs.base_location, pkg_name)

                # envia arquivo ao MinIO
                task_ingress_package.delay(file_path, pkg_name, request.user.id)

            else:
                emsg = file_input.name + _(' does not have a valid format. Please provide a zip file.')
                messages.error(request, emsg, extra_tags='alert-danger')

                # registra evento de arquivo inválido
                ev = controller.add_event(
                    user=request.user,
                    event_name=Event.Name.UPLOAD_PACKAGE,
                    annotation={
                        'error': emsg,
                    },
                    status=Event.Status.FAILED,
                )

            return redirect('event_list')

    return render(request, 'ingress/package_upload.html')


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def ingress_package_download_page(request):
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
        return render(request, 'ingress/package_download.html', context)

    # Inicializa task para o PID informado e redireciona para a própria página aguardando resultado
    elif pid:
        job = task_get_package_uri_by_pid.delay(pid, request.user.id)
        return HttpResponseRedirect(reverse('ingress_package_download') + '?job=' + job.id + '&pid=' + pid)

    # Abre template pela primeira vez para digitar PID
    return render(request, 'ingress/package_download.html')


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def ingress_package_list_page(request):
    request_scope = request.GET.get('scope', '')
    deposited_package_list = controller.get_ingress_packages_from_user_and_scope(request.user, request_scope)

    paginator = Paginator(deposited_package_list, 25)
    page_number = request.GET.get('page')
    deposited_package_obj = paginator.get_page(page_number)

    return render(request, 'ingress/package_list.html', context={'deposited_package_obj': deposited_package_obj, 'scope': request_scope})


#################
# journal views #
#################
@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress'])
def journal_list_page(request):
    journal_list = dsm_ingress._journals_manager.get_journals()

    paginator = Paginator(journal_list, 25)
    page_number = request.GET.get('page')
    journal_obj = paginator.get_page(page_number)

    return render(request, 'journal/journal_list.html', context={'journal_obj': journal_obj})


##################
# tracking views #
##################
@login_required(login_url='login')
def event_list_page(request):
    request_scope = request.GET.get('scope', '')
    event_list = controller.get_events_from_user_and_scope(request.user, request_scope).order_by('-datetime')

    paginator = Paginator(event_list, 25)
    page_number = request.GET.get('page')
    event_obj = paginator.get_page(page_number)

    return render(request, 'tracking/event_list.html', context={'event_obj': event_obj, 'scope': request_scope})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_ingress', 'operator_migration', 'quality_analyst'])
def task_update_status(request):
    """Obtém status (STARTING, FAILURY, PROGRESS, SUCCESS ou UNDEFINED) de task executada."""
    try:
        task_id = request.GET['task_id']
        task = AsyncResult(task_id)
        result = task.result
        status = task.status
    except:
        result = 'UNDEFINED'
        status = 'UNDEFINED'

    json_data = {
        'status': status,
        'state': 'PROGRESS',
        'data': result,
    }

    return JsonResponse(json_data)


###################
# migration views #
###################
@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_migration'])
def migrate_identify_documents(request):
    # registra evento de identificação
    ev = controller.add_event(request.user, Event.Name.IDENTIFY_DOCUMENTS_TO_MIGRATE)

    # identifica documentos para migrar
    task_migrate_identify_documents.delay()

    controller.update_event(ev, {'status': Event.Status.COMPLETED})

    # informa mensagem de sucesso
    messages.success(request, _('Task submitted successfully'), extra_tags='alert alert-success')

    return redirect('event_list')


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_migration'])
def migrate_isis_db_page(request):
    if request.method == 'POST':
        id_file = request.FILES.get('id_file')
        isis_path = request.POST.get('isis_path')
        data_type = request.POST.get('data_type')

        input_path = ''

        fs = FileSystemStorage(location=settings.MEDIA_INGRESS_TEMP)

        # migração por arquivo id
        if id_file:
            # envia arquivo para diretório temporário
            fs_file_name = fs.save(id_file.name, id_file)

            # caminho completo do arquivo
            fs_full_path_id_file = os.path.join(fs.base_location, fs_file_name)

            # registra evento de migração
            ev = controller.add_event(request.user, Event.Name.START_MIGRATION_BY_ID_FILE, {'path': fs_full_path_id_file})

            # inica task para efetuar migração
            task_migrate_isis_db.delay(data_type, fs_full_path_id_file)

            input_path = fs_full_path_id_file

        # migração por base isis
        elif isis_path:
            # gera caminho canônico da base ISIS
            full_isis_path = os.path.join(isis_path, data_type, data_type)

            # registra evento de migração
            ev = controller.add_event(request.user, Event.Name.START_MIGRATION_BY_ISIS_DB, {'path': full_isis_path})

            # inica task para efetuar migração
            task_migrate_isis_db.delay(data_type, full_isis_path)

            input_path = full_isis_path

        if input_path:
            # cria registro de pacote migrado
            controller.add_migration_package(request.user, datetime.utcnow(), input_path)

            # informa mensagem de sucesso
            messages.success(request, _('Task submitted successfully'), extra_tags='alert alert-success')

            # atualiza estado do evento de migração
            controller.update_event(ev, {'status': Event.Status.COMPLETED})

        return redirect('event_list')

    return render(request, 'migration/isis_db.html', context={'isis_path': dsm_migration.configuration.BASES_PATH})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_migration'])
def migrate_search_pending_documents_page(request):
    page_number = int(request.GET.get('page', 1))
    pub_year = request.GET.get('pub_year', None)
    acron = request.GET.get('acron', None)
    volume = request.GET.get('volume', None)

    year = request.GET.get('year', None)
    issn = request.GET.get('issn', None)
    pid = request.GET.get('pid', None)

    pending_documents = []
    paginator = None

    class Object():
        pass

    search = Object()
    setattr(search, 'exists', True)
    url = '?'

    if issn or year or pid:
        filter = ''

        if pid:
            filter = pid
        else:
            if issn:
                filter = issn
                url += 'issn='+issn+'&'
            if year:
                filter += year
                url += 'year='+year+'&'

        filter_documents = ISISDocument.objects.filter(_id__contains = filter)
        paginator = Paginator(filter_documents, 25)
        pending_documents = paginator.get_page(page_number)

        setattr(paginator, 'exists', False)
        setattr(search, 'url', url)

    elif acron or volume or pub_year:
        pending_documents = dsm_migration.list_documents_to_migrate(acron, volume, pub_year, "", "", items_per_page=25, page_number=page_number, status="")
        total_documents = dsm_migration.list_documents_to_migrate(acron, volume, pub_year, "", "", items_per_page=1000, page_number=int(1), status="")

        paginator = Object()
        has_next = False
        has_previous = False
        next_page_number = ''
        previous_page_number = ''
        num_pages = math.ceil(len(total_documents)/25)

        if num_pages > page_number:
            next_page_number = page_number + 1
            has_next = True

        if page_number > 1:
            previous_page_number = page_number - 1
            has_previous = True

        setattr(paginator, 'exists', True)
        setattr(paginator, 'page_number', page_number)
        setattr(paginator, 'num_pages', num_pages)
        setattr(paginator, 'has_next', has_next)
        setattr(paginator, 'has_previous', has_previous)
        setattr(paginator, 'next_page_number', next_page_number)
        setattr(paginator, 'previous_page_number', previous_page_number)

        if pub_year:
            setattr(paginator, 'pub_year', pub_year)
            url += 'pub_year='+pub_year+'&'

        if acron:
            setattr(paginator, 'acron', acron)
            url += 'acron='+acron+'&'

        if volume:
            setattr(paginator, 'volume', volume)
            url += 'volume='+volume+'&'

        if url != '?':
            setattr(search, 'exists', False)

        setattr(paginator, 'url', url)

    if request.method == 'POST':
        # obtiene documentos seleccionadas
        migrate = []

        if request.POST.get('migrate') == "select":
            migrate = request.POST.getlist('document')

        if request.POST.get('migrate') == "this":
            for p in pending_documents:
                migrate.append(p.id)

        if request.POST.get('migrate') == "all":
            for f in filter_documents:
                migrate.append(f.id)

        task_migrate_documents.delay(pid=",".join(migrate))

        ev = controller.add_event(request.user, Event.Name.START_MIGRATION_BY_AVY)

        messages.success(request, _('Task submitted successfully'), extra_tags='alert alert-success')

        controller.update_event(ev, {'status': Event.Status.COMPLETED})

        return redirect('event_list')

    return render(request, 'migration/search_pending_documents.html', context={'documents_obj': pending_documents, 'paginator': paginator, 'search': search})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_migration'])
def migrate_pending_documents_by_journal_list_page(request):
    journals = dsm_ingress._journals_manager.get_journals()

    paginator = Paginator(journals, 25)
    page_number = request.GET.get('page')
    journals_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        acronym = request.POST.getlist('acronym')
        task_migrate_acron.delay(",".join(acronym))

        # registra evento de migração por acrônimo
        ev = controller.add_event(request.user, Event.Name.START_MIGRATION_BY_ACRONYM)

        messages.success(request, _('Task submitted successfully'), extra_tags='alert alert-success')

        controller.update_event(ev, {'status': Event.Status.COMPLETED})

        return redirect('event_list')

    return render(request, 'migration/pending_documents_by_journal_list.html', context={'journals_obj': journals_obj})


@login_required(login_url='login')
@allowed_users(allowed_groups=['manager', 'operator_migration'])
def migrate_pending_documents_by_issue_list_page(request):
    if request.method == 'POST':
        # obtiene años o carpetas seleccionadas
        years=None
        volumes=None
        selected = request.POST.getlist(request.POST.get('migrate'))

        if request.POST.get('migrate') == "years":
            years = ",".join(selected)

        if request.POST.get('migrate') == "volumes":
            volumes = ",".join(selected)

        acron = request.GET.get('acron')
        task_migrate_documents.delay(acronym=acron, volume=volumes, pub_year=years)

        # registra evento de migração por acrônimo, volume e ano
        ev = controller.add_event(request.user, Event.Name.START_MIGRATION_BY_AVY)

        messages.success(request, _('Task submitted successfully'), extra_tags='alert alert-success')

        controller.update_event(ev, {'status': Event.Status.COMPLETED})

        return redirect('event_list')

    issue = request.GET.get('issue')
    acron = request.GET.get('acron')
    issues = OPACIssue.objects.filter(journal=issue)
    i_prev = ''
    issue_obj = None
    issues_obj = []

    class Issue:
        def __init__(self, volumes = None, year = None):
            if volumes:
                self.volumes = volumes
            else:
                self.volumes = []
            self.year = year

    for num, i in enumerate(issues):
        if i.year != i_prev:
            if issue_obj:
                if issue_obj.year:
                    issues_obj.append(issue_obj)
            issue_obj = Issue()
            i_prev = i.year
            issue_obj.year = i.year

        volume = ''

        if i.volume:
            volume = 'v' + str(i.volume)

        if i.number:
            volume += 'n' + str(i.number)

        issue_obj.volumes.append(volume)
        if num == len(issues)-1:
            issues_obj.append(issue_obj)

    paginator = Paginator(issues_obj, 25)
    page_number = request.GET.get('page')
    issues_obj = paginator.get_page(page_number)

    return render(request, 'migration/pending_documents_by_issue_list.html', context={'issues_obj': issues_obj, 'issue': issue, 'acron': acron})
