#!/usr/bin/env python3
import os, setuptools

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    README = f.read()

requires = [
    'asgiref',
    'celery',
    'confusable-homoglyphs',
    'Django',
    'django-celery-results',
    'gunicorn',
    'pytz',
    'python-dateutil',
    'sqlparse',
    'minio',
    'lxml',
    'opac_schema',
    'dsm',
    'scielo_v3_manager',
]

tests_require = [
]

setuptools.setup(
    name="SciELO Publishing Framework",
    version="0.1",
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    description="",
    long_description=README,
    long_description_content_type="text/markdown",
    license="2-clause BSD",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    include_package_data=True,
    extras_require={"testing": tests_require},
    install_requires=requires,
    dependency_links=[
    ],
    python_requires=">=3.6",
    test_suite="tests",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Operating System :: OS Independent",
    ],
)
