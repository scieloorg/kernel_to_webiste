import os


def package_name_is_valid(package_name):
    filename, extension = os.path.splitext(package_name)

    if extension.endswith('zip'):
        return True
