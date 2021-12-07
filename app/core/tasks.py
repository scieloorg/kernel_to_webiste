from celery import shared_task, current_task
from django.core.files.storage import FileSystemStorage
from spf import settings

import dsm.ingress as dsm_ingress
import dsm.migration as dsm_migration


@shared_task
def task_get_package_uri_by_pid(pid):
    result = dsm_ingress.get_package_uri_by_pid(pid)

    current_task.update_state(
        state='PROGRESS',
        meta={
            'status': 'LOADING...',
        })

    return result


@shared_task
@shared_task
def task_migrate_isis_db(data_type, file_path, file_id=None):
   results = []

   fs = FileSystemStorage(settings.MEDIA_INGRESS_TEMP)

   if file_id:
       for r in dsm_migration.migrate_isis_db(data_type, file_path):
           current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...', })
           results.append(r)
       fs.delete(file_id)
   else:
       for r in dsm_migration.migrate_isis_db(data_type, file_path):
           current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...',})
           results.append(r)

   return results
def task_migrate_acron(acronym):
    result = []
    if acronym:
        acron = acronym.split(",")
        for a in acron:
            for r in dsm_migration.migrate_acron(a):
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'status': 'LOADING...',
                    })
                result.append('Finish ' + a)

    return result


@shared_task
def task_migrate_documents(acronym=None, volume=None, pub_year=None, pid=None):
    result = None

    if pid:
        result = []
        for p in pid.split(","):
            for r in dsm_migration.migrate_document(p):
                current_task.update_state(
                    state='PROGRESS',
                    meta={
                        'status': 'LOADING...',
                    })
                result.append('Finish ' + str(p))

    if volume:
        result = []
        for v in volume.split(","):
            total_documents = dsm_migration.list_documents_to_migrate(acronym, v, "", "", "", items_per_page=1000000, page_number=1, status="")
            for d in total_documents:
                for r in dsm_migration.migrate_document(d):
                    current_task.update_state(
                        state='PROGRESS',
                        meta={
                            'status': 'LOADING...',
                        })
                    result.append('Finish ' + str(d))

    if pub_year:
        result = []
        for y in pub_year.split(","):
            total_documents = dsm_migration.list_documents_to_migrate(acronym, "", y, "", "", items_per_page=1000000, page_number=1, status="")
            for d in total_documents:
                for r in dsm_migration.migrate_document(d):
                    current_task.update_state(
                        state='PROGRESS',
                        meta={
                            'status': 'LOADING...',
                        })
                    result.append('Finish ' + str(d))

    return result

