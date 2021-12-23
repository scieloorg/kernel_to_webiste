from spf.celery import app
from django.core.files.storage import FileSystemStorage
from spf import settings
from core import controller
from core.models import Event, IngressPackage

import dsm.ingress as dsm_ingress
import dsm.migration as dsm_migration


@app.task(bind=True,  max_retries=3)
def task_get_package_uri_by_pid(self, pid, user_id):
    # obtém objeto User
    user = controller.get_user_from_id(user_id)

    # cria evento de pesquisa por pacote
    ev = controller.add_event(
        user,
        Event.Name.RETRIEVE_PACKAGE,
        annotation={
            'pid': pid,
        }
    )

    # obtém o {uri, name} de todos os pacotes existentes para o PID informado
    result = dsm_ingress.get_package_uri_by_pid(pid)

    app.current_task.update_state(
        state='PROGRESS',
        meta={
            'status': 'LOADING...',
        })

    if result['errors']:
        # houve alguma falha. atualiza status com valor FAILED e conteúdo da falha ocorrida
        controller.update_event(
            ev,
            {
                'status': Event.Status.FAILED,
                'annotation': result,
            }
        )
    else:

        # evento ocorreu com sucesso. atualiza status com valor COMPLETED
        controller.update_event(ev, {'status': Event.Status.COMPLETED})

    return result


@app.task(bind=True,  max_retries=3)
def task_ingress_package(self, file_path, pkg_name, user_id, event_id):
    # obtém objeto User
    user = controller.get_user_from_id(user_id)

    # obtém objeto Event
    ev = controller.get_event_from_id(event_id)

    try:
        # envia pacote ao MinIO e guarda saída em results
        results = dsm_ingress.upload_package(file_path)

        # evento ocorreu com sucesso. atualiza status com valor COMPLETED
        controller.update_event(ev, {'status': Event.Status.COMPLETED})

        # registra o pacote enviado
        controller.add_ingress_package(
            user=user,
            event_datetime=ev.datetime,
            package_name=pkg_name,
            status=IngressPackage.Status.RECEIVED
        )

    except ValueError as e:
        # evento falhou. atualiza status com valor FAILED
        controller.update_event(
            ev,
            {
                'status': Event.Status.FAILED,
                'annotation': str(e),
            }
        )

    # remove da pasta temporária o arquivo enviado
    fs = FileSystemStorage(location=settings.MEDIA_INGRESS_TEMP)
    fs.delete(file_path)

    # devolve caminho
    return file_path


@app.task(bind=True,  max_retries=3)
def task_migrate_identify_documents(self):
    app.current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...'})

    results = []
    for i in dsm_migration.identify_documents_to_migrate():
        results.append(i)

    return results


@app.task(bind=True,  max_retries=3)
def task_migrate_isis_db(self, data_type, file_path, file_id=None):
   results = []

   fs = FileSystemStorage(settings.MEDIA_INGRESS_TEMP)

   if file_id:
       for r in dsm_migration.migrate_isis_db(data_type, file_path):
           app.current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...', })
           results.append(r)
       fs.delete(file_id)
   else:
       for r in dsm_migration.migrate_isis_db(data_type, file_path):
           app.current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...',})
           results.append(r)

   return results


@app.task(bind=True,  max_retries=3)
def task_migrate_acron(self, acronym):
    results = []

    if acronym:
        acron = acronym.split(",")
        for a in acron:
            for r in dsm_migration.migrate_acron(a):
                app.current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...',})
                results.append('Finish ' + a)

    return results


@app.task(bind=True,  max_retries=3)
def task_migrate_documents(self, acronym=None, volume=None, pub_year=None, pid=None):
    results = None

    if pid:
        results = []
        for p in pid.split(","):
            for r in dsm_migration.migrate_document(p):
                app.current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...',})
                results.append('Finish ' + str(p))

    if volume:
        results = []
        for v in volume.split(","):
            total_documents = dsm_migration.list_documents_to_migrate(acronym, v, "", "", "", items_per_page=1000000, page_number=1, status="")
            for d in total_documents:
                for r in dsm_migration.migrate_document(d):
                    app.current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...',})
                    results.append('Finish ' + str(d))

    if pub_year:
        results = []
        for y in pub_year.split(","):
            total_documents = dsm_migration.list_documents_to_migrate(acronym, "", y, "", "", items_per_page=1000000, page_number=1, status="")
            for d in total_documents:
                for r in dsm_migration.migrate_document(d):
                    app.current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...',})
                    results.append('Finish ' + str(d))

    return results
