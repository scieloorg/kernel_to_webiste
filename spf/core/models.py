from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class IngressPackage(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'R', _('Received')
        QUEUDED_FOR_VALIDATION = 'Q', _('Queued for validation')
        VALIDATING = 'D', _('Validating')
        VALIDATION_FAILURE = 'F', _('Validation failure')
        VALIDATED = 'V', _('Validated')

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    package_name = models.CharField(max_length=200)
    datetime = models.DateTimeField()
    status = models.CharField(max_length=1, choices=Status.choices, blank=False, null=False)


class MigratePackage(models.Model):
    ...


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
