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
    ev = controller.add_event(user_id, models.Event.Name.MAKE_PACKAGE, annotation={'pid': pid}, status=models.Event.Status.INITIATED)

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
def task_upload_package(self, package_path, package_file, user_id):
    """
    Envia um pacote para o sistema, atualiza banco de dados e file storage.

    Parameters
    ----------
    package_path: str
    package_file: str
    user_id: int

    Returns
    -------
    package: dict
    """
    ev = controller.add_event(user_id, models.Event.Name.UPLOAD_PACKAGE, {'package_file': package_file}, models.Event.Status.INITIATED)

    # obtém os arquivos de cada documento
    try:
        names_and_packages = task_get_names_and_packages(package_path)
    except ValueError:
        return ['error']

    packages_metadata = []

    # processa cada documento contido no pacote
    for pkg_name, pkg_data in names_and_packages.items():
        ev = controller.add_event(user, models.Event.Name.UPLOAD_PACKAGE, {'package_file': package_file}, models.Event.Status.INITIATED)



        article_package_uris_and_names['file'] = storage_adapter.register_article_files(
            xml_sps.issn,
            xml_sps.scielo_pid_v3,
            article_package_uris_and_names['zip']
        )

        controller.add_ingress_package(user, article_package_uris_and_names['file']['name'], models.IngressPackage.Status.RECEIVED)

        opac_adapter.update_article(
            pid=xml_sps.scielo_pid_v3,
            xml_sps=xml_sps,
            xml_uri=xml_uri_and_name['uri'],
            renditions_uris_and_names=renditions_uris_and_names,
        )

        package_uris_and_names = {
            'file': article_package_uris_and_names['file'],
            'xml': xml_uri_and_name,
            'renditions': renditions_uris_and_names,
            'assets': assets_uris_and_names,
        }

        article_files = opac_adapter.add_article_files(
            xml_sps.scielo_pid_v3,
            package_uris_and_names,
        )


        packages_metadata.append(package_uris_and_names)

        controller.update_event(ev, {'status': models.Event.Status.COMPLETED})

    utils.fs_delete_file(package_path)

    return packages_metadata


@app.task(bind=True, max_retries=3)
def task_get_names_and_packages(self, path):
    return sps_maker.get_names_and_packages(path)


@app.task(bind=True, max_retries=3)


@app.task(bind=True, max_retries=3)
def task_fill_package_uris_and_names(self, package_uris_and_names, article_files, xml_sps):
    package_uris_and_names['pid'] = article_files.aid
    package_uris_and_names['issn'] = xml_sps.issn
    package_uris_and_names['acron'] = xml_sps.acron
    package_uris_and_names['version'] = article_files.version


@app.task(bind=True, max_retries=3)
def task_make_package_from_uris(self, xml_uri_and_name, renditions_uris_and_names):
    return sps_maker.make_package_from_uris(xml_uri_and_name['uri'], renditions_uris_and_names)


@app.task(bind=True, max_retries=3)
def task_generate_sps(self, xml_content, convert_remote_to_local=True):
    xml_sps = sps_maker.sps_package.SPS_Package(xml_content)

    if convert_remote_to_local:
        xml_sps.remote_to_local(xml_sps.package_name)

    return xml_sps


@app.task(bind=True, max_retries=3)
def task_register_content(self, pkg_data, xml_sps):
    assets_uris_and_names = storage_adapter.register_assets(pkg_data, xml_sps)
    renditions_uris_and_names = storage_adapter.register_renditions(pkg_data, xml_sps)
    xml_uri_and_name = storage_adapter.register_xml(xml_sps)

    return {
        'xml': xml_uri_and_name,
        'renditions': renditions_uris_and_names,
        'assets': assets_uris_and_names,
    }


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
