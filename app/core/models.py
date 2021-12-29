from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


GROUP_MANAGER = 'manager'
GROUP_OPERATOR_INGRESS = 'operator_ingress'
GROUP_OPERATOR_MIGRATION = 'operator_migration'
GROUP_QUALITY_ANALYST = 'quality_analyst'

SCOPE_ALL_USERS = 'all_users'


class IngressPackage(models.Model): 
    class Status(models.TextChoices):
        RECEIVED = 'RC', _('Received')
        QUEUDED_FOR_VALIDATION = 'QV', _('Queued for validation')
        VALIDATING = 'VI', _('Validating')
        VALIDATION_FAILURE = 'VF', _('Validation failure')
        VALIDATED = 'VC', _('Validated')
        QUEUED_FOR_UPLOADING = 'QU', _('Queued for uploading')
        UPLOADING = 'UI', _('Uploading')
        UPLOADING_FAILURE = 'UF', _('Uploading failure')
        UPLOADED = 'UC', _('Uploaded')

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    package_name = models.CharField(max_length=200)
    datetime = models.DateTimeField()
    status = models.CharField(max_length=2, choices=Status.choices, blank=False, null=False)


class MigrationPackage(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'RC', _('Received')

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    path = models.CharField(max_length=200)
    datetime = models.DateTimeField(null=True)
    status = models.CharField(max_length=2, choices=Status.choices, blank=False, null=False)


class Event(models.Model):
    class Status(models.TextChoices):
        INITIATED = 'I', _('Initiated')
        COMPLETED = 'C', _('Completed')
        FAILED = 'F', _('Failed')

    class Name(models.TextChoices):
        RETRIEVE_PACKAGE = 'RP', _('Retrieve package')
        UPLOAD_PACKAGE = 'UP', _('Upload package')
        START_VALIDATION = 'SV', _('Start validation')
        FINALIZE_VALIDATION = 'FV', _('Finalize validation')
        CHANGE_USER_GROUPS = 'CUG', _('Change user groups')
        IDENTIFY_DOCUMENTS_TO_MIGRATE =  'MID', _('Identify documents to migrate')
        START_MIGRATION_BY_ID_FILE = 'MSF', _('Start migration by id file')
        START_MIGRATION_BY_ISIS_DB = 'MSD', _('Start migration by ISIS database')
        START_MIGRATION_BY_ACRONYM = 'MAC', _('Start migration by acronym')
        START_MIGRATION_BY_AVY = 'MVY', _('Start migration by volume or year')

    # quem realiza o evento
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    # momento em que o evento foi iniciado
    datetime = models.DateTimeField(auto_now=True)

    # nome do evento
    name = models.CharField(max_length=3, choices=Name.choices, blank=False, null=False)

    # estado do evento (iniciado, realizando, concluído)
    status = models.CharField(max_length=1, choices=Status.choices, blank=False, null=False)

    # informação relacionada ao evento
    annotation = models.CharField(max_length=200, null=True)


class ValidationSchema(models.Model):
    schema_name = models.CharField(max_length=200, null=True)


class Validation(models.Model):
    name = models.CharField(max_length=200, null=True)
    validation_schema = models.ForeignKey(ValidationSchema, on_delete=models.PROTECT)
