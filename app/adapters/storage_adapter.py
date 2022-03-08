from datetime import datetime
from packtools import file_utils
from libs import minio
from mimetypes import MimeTypes
from zipfile import ZipFile

import logging
import os
import tempfile
import urllib3


MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_HOST = os.environ.get("MINIO_HOST")
MINIO_SCIELO_COLLECTION = os.environ.get("MINIO_SCIELO_COLLECTION")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_SECURE = True if os.environ.get("MINIO_SECURE", "").lower() == 'true' else False
MINIO_SPF_DIR = os.environ.get("MINIO_SPF_DIR")
MINIO_TIMEOUT = int(os.environ.get("MINIO_TIMEOUT", "10000"))


logger = logging.getLogger(__name__)


class FilesStorageRegisterError(Exception):
    """ To handle registration failures.
    """


def date_now_as_folder_name():
    """
    Generate a folder name based on the value `datetime.utcnow()`
    Returns
    -------
    folder_name: `str`
    """
    return datetime.utcnow().isoformat().replace(":", "")


def get_http_client():
    """
    Get an instance of `urllib3.PoolManager`
    Returns
    -------
    pool_manager: `urllib3.PoolManager`
    """
    if not MINIO_TIMEOUT:
        raise ValueError("Missing value for environment variable MINIO_TIMEOUT")

    return urllib3.PoolManager(
        timeout=MINIO_TIMEOUT,
        maxsize=10,
        cert_reqs="CERT_REQUIRED",
        retries=urllib3.Retry(
            total=5,
            backoff_factor=0.2,
            status_forcelist=[500, 502, 503, 504]
        ))


def get_storage_client():
    """
    Get an instance of `minio.MinioStorage`
    Returns
    -------
    storage_client: `minio.MinioStorage`
    """
    VARNAME = (
        "MINIO_HOST",
        "MINIO_ACCESS_KEY",
        "MINIO_SECRET_KEY",
        "MINIO_SECURE",
        "MINIO_TIMEOUT",
        "MINIO_SCIELO_COLLECTION",
        "MINIO_SPF_DIR",
    )
    for var_name in VARNAME:
        if not os.environ.get(var_name):
            raise ValueError(f"Missing value for environment variable {var_name}")

    return minio.MinioStorage(
        minio_host=MINIO_HOST,
        minio_access_key=MINIO_ACCESS_KEY,
        minio_secret_key=MINIO_SECRET_KEY,
        scielo_collection=MINIO_SCIELO_COLLECTION,
        minio_secure=MINIO_SECURE,
        minio_http_client=get_http_client(),
    )


def get_storage_folder_for_article_files(issn, scielo_pid_v3, ingress="ingress", packages="packages"):
    """
    Get storage folder for article files
    Parameters
    ----------
    issn: str
    scielo_pid_v3: str
    ingress: str
    packages: str
    Returns
    -------
    storage_folder_for_article_files: str
    """
    return os.path.join(
        ingress,
        packages,
        issn,
        scielo_pid_v3,
        date_now_as_folder_name()
    )


def get_storage_folder_for_article_content(issn, scielo_pid_v3, articles="documents"):
    """
    Get storage folder for article content
    Parameters
    ----------
    issn: str
    scielo_pid_v3: str
    articles: str
    Returns
    -------
    storage_folder_for_article_content: str
    """
    return os.path.join(
        articles,
        issn,
        scielo_pid_v3
    )


def register_assets(pkg_data, sps_package):
    """
    Send assets to the storage
    Parameters
    ----------
    pkg_data: packtools.sps.models.packages.Package
    sps_package: packtools.sps.models.sps_package.SPS_Package
    Returns
    -------
    uris_and_names: list
    """
    uris_and_names = []
    article_content_folder = get_storage_folder_for_article_content(sps_package.issn, sps_package.scielo_pid_v3)
    storage_client = get_storage_client()

    for asset_in_xml in sps_package.assets.items:
        asset_file_path = pkg_data.get_asset(asset_in_xml.xlink_href)

        if not asset_file_path:
            continue

        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                with ZipFile(pkg_data.zip_file_path) as zf:
                    extracted_path = zf.extract(asset_file_path, path=tmpdirname)

                    asset_uri = storage_client.register(
                        file_path=extracted_path,
                        prefix=article_content_folder,
                        preserve_name=True,
                    )
                    asset_in_xml.xlink_href = asset_uri

                    uris_and_names.append({'uri': asset_uri, 'name': os.path.basename(asset_uri)})

        except FilesStorageRegisterError:
            ...

    return uris_and_names


def register_renditions(pkg_data, sps_package):
    """
    Send renditions to the storage
    Parameters
    ----------
    pkg_data: packtools.sps.models.packages.Package
    sps_package: packtools.sps.models.sps_package.SPS_Package
    Returns
    -------
    uris_and_names: list
    """
    uris_and_names = []
    article_content_folder = get_storage_folder_for_article_content(sps_package.issn, sps_package.scielo_pid_v3)
    storage_client = get_storage_client()
    mimetypes = MimeTypes()

    for lang, rendition_path in pkg_data.renditions.items():
        rendition_basename = os.path.basename(rendition_path)
        _mimetype = mimetypes.guess_type(rendition_basename)[0]

        if lang == 'original':
            lang = sps_package.lang

        _rendition = {
            "name": rendition_basename,
            "mimetype": _mimetype,
            "lang": lang,
            "type": "pdf",
        }

        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                with ZipFile(pkg_data.zip_file_path) as zf:
                    extracted_path = zf.extract(rendition_path, path=tmpdirname)

                    rendition_uri = storage_client.register(
                        file_path=extracted_path,
                        prefix=article_content_folder,
                        preserve_name=True,
                    )
                    _rendition['uri'] = rendition_uri
                    _rendition["size_bytes"] = os.path.getsize(extracted_path)

                    uris_and_names.append(_rendition)

        except FilesStorageRegisterError:
            ...

    return uris_and_names


def register_xml(sps_package):
    """
    Send `sps_package.xml_content` to the storage
    Parameters
    ----------
    sps_package: packtools.sps.models.sps_package.SPS_Package
    Returns
    -------
    xml_uri_and_name: dict
    """
    xml_uri_and_name = {}
    temp_dir = tempfile.mkdtemp()
    xml_path = os.path.join(temp_dir, f"{sps_package.package_name}.xml")

    file_utils.write_file(
        xml_path,
        sps_package.xml_content.encode("utf-8"),
        "wb",
    )

    article_content_folder = get_storage_folder_for_article_content(sps_package.issn, sps_package.scielo_pid_v3)
    storage_client = get_storage_client()

    xml_uri_and_name['uri'] = storage_client.register(
        file_path=xml_path,
        prefix=article_content_folder,
        preserve_name=True,
    )
    xml_uri_and_name['name'] = os.path.basename(xml_uri_and_name['uri'])

    return xml_uri_and_name


def register_article_files(issn, scielo_pid_v3, article_files_path):
    """
    Send article_files to the storage
    Parameters
    ----------
    issn: str
    scielo_pid_v3: str
    article_files_path: str
    Returns
    -------
    uri_and_name: dict
    """
    uri_and_name = {}

    article_package_folder = get_storage_folder_for_article_files(issn, scielo_pid_v3)
    storage_client = get_storage_client()

    article_package_uri = storage_client.register(
        file_path=article_files_path,
        prefix=article_package_folder,
        preserve_name=True,
    )

    uri_and_name['uri'] = article_package_uri
    uri_and_name['name'] = os.path.basename(article_package_uri)

    return uri_and_name


def register_article_content(article_files_path, issn, pid_v3, prefix, pdf_langs):
    """
    Send article content to the storage
    Parameters
    ----------
    article_files_path: str
    issn: str
    pid_v3: str
    prefix: str
    pdf_langs: list
    Returns
    -------
    uris_and_names: dict
    """
    storage_client = get_storage_client()
    article_content_folder = get_storage_folder_for_article_content(issn=issn,scielo_pid_v3=pid_v3)

    files_paths = {'xml': '', 'assets': [], 'renditions': []}

    for fi in file_utils.files_list_from_zipfile(article_files_path):
        fi_read = file_utils.read_from_zipfile(article_files_path, fi)
        fi_path = file_utils.create_temp_file(fi, fi_read, 'wb')

        file_role = file_utils.get_file_role(fi, prefix, pdf_langs)

        fi_result = storage_client.register(
            file_path=fi_path,
            prefix=article_content_folder,
            preserve_name=True,
        )

        if file_role == 'xml':
            files_paths[file_role] = fi_result
        else:
            files_paths[file_role].append(fi_result)

    return files_paths
