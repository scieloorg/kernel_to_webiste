from spf.celery import app

from dsm import migration as dsm_migration
from packtools.sps import sps_maker

from adapters import opac_adapter, storage_adapter
from core import controller, models, utils


@app.task(bind=True, max_retries=3)
def task_make_package(self, user_id, pid, xml_uri, renditions_uris_and_names):
    """
    Costrói um pacote e atualiza registros no banco de dados e no file storage.

    Parameters
    ----------
    user_id: int
    pid: str
    xml_uri: str
    renditions_uris_and_names: dict

    Returns
    -------
    package: dict
    """
    user = controller.get_user_from_id(user_id)
    ev = controller.add_event(user, models.Event.Name.MAKE_PACKAGE, annotation={'pid': pid}, status=models.Event.Status.INITIATED)

    # cria pacote ZIP
    try:
        article_package_uris_and_names = sps_maker.make_package_from_uris(xml_uri, renditions_uris_and_names)
    except Exception as e:
        controller.update_event(ev, {'status': models.Event.Status.FAILED, 'annotation': {'pid': pid, 'error': e.__class__.__name__}})
        return {'error': e.__class__.__name__}

    # obtém registro de artigo no banco de dados
    article = opac_adapter.get_article_by_pid(pid)

    # envia pacote ZIP para MinIO
    article_package_uris_and_names['file'] = storage_adapter.register_article_files(
        article.journal.scielo_issn,
        article.aid,
        article_package_uris_and_names['zip']
    )

    # cria registro de article_files no banco de dados
    article_files = opac_adapter.add_article_files(article.aid, article_package_uris_and_names)

    # atualiza evento de geração de pacote
    controller.update_event(ev, {'status': models.Event.Status.COMPLETED})

    return {
        'package': {
            'uri': article_files.file.uri,
            'name': article_files.file.name,
            'version': article_files.version,
            'created': article_files.created,
            }
        }


@app.task(bind=True,  max_retries=3)
def task_ingress_package(self, package_path, package_file, user_id):
    user = controller.get_user_from_id(user_id)
    ev = controller.add_event(user, Event.Name.UPLOAD_PACKAGE_TO_MINIO, {'package_file': package_file}, Event.Status.INITIATED)

    results = {}

    try:
        results.update(dsm_ingress.upload_package(package_path))
        controller.update_event(ev, {'status': Event.Status.COMPLETED})
        controller.add_ingress_package(user, ev.datetime, package_file, IngressPackage.Status.RECEIVED)
    except ValueError as e:
        controller.update_event(ev, {'status': Event.Status.FAILED, 'annotation': {'error': str(e)},})
        results.update({'error': str(e)})

    utils.fs_delete_file(package_path)
    
    return results


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

   if file_id:
       for r in dsm_migration.migrate_isis_db(data_type, file_path):
            app.current_task.update_state(state='PROGRESS', meta={'status': 'LOADING...', })
            results.append(r)
       utils.fs_delete_file(file_id)
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
