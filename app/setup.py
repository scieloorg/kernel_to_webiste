#!/usr/bin/env python3
import setuptools

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
    version="0.1.6.0",
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    description="This is the SciELO Upload Framework",
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
)
