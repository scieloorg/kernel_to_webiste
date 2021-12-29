import os

from django.core.files.storage import FileSystemStorage
from django.utils.translation import gettext as _
from datetime import datetime
from spf import settings


class PathDoesNotExistError(Exception):
    ...


def package_name_is_valid(package_name):
    filename, extension = os.path.splitext(package_name)

    if extension.endswith('zip'):
        return True


def create_file_path(filename):
    return os.path.join(settings.MEDIA_INGRESS_TEMP, filename)


def write_file_to_disk(file):
    try:
        path = create_file_path(file.name)

        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

            return {
                'success': True, 
                'path': path, 
                'created': datetime.fromtimestamp(os.stat(path).st_ctime),
            }
    except Exception as e:
        return {
            'success': False, 
            'error': e,
        }


def handle_upload_file(file):
    result = write_file_to_disk(file)
    
    return {
        'package_file': file.name, 
        'package_path': result.get('path'), 
        'datetime': result.get('created'),
        'error': result.get('errro'),
        'success': result.get('success'),
        }
