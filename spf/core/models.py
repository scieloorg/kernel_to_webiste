from enum import Enum
from django.db import models
from django.contrib.auth.models import User

from opac_schema.v1.models import *


class EventName(Enum):
    # nomes de eventos associados à busca e ao envio de pacotes
    RETRIEVE_PACKAGE_DATA = "RETRIVE_PACKAGE_DATA"
    UPLOAD_NEW_PACKAGE = "UPLOAD_NEW_PACKAGE"
    UPLOAD_EXISTING_PACKAGE = "UPLOAD_EXISTING_PACKAGE"

    # nomes de eventos associados a validação
    START_VALIDATION = "START_VALIDATION"
    FINALIZE_VALIDATION = "FINALIZE_VALIDATION"


class EventStatus(Enum):
    # estado de um evento
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Event(models.Model):
    # quem realiza o evento
    actor = models.ForeignKey(User, on_delete=models.PROTECT)

    # momento em que o evento foi iniciado
    datetime = models.DateTimeField(auto_now=True)

    # nome do evento
    name = models.CharField(max_length=200)

    # estado do evento (iniciado, realizando, concluído)
    status = models.CharField(max_length=100, default=EventStatus.INITIATED)

    # informação relacionada ao evento
    annotation = models.CharField(max_length=200, null=True)


class ValidationSchema(models.Model):
    schema_name = models.CharField(max_length=200, null=True)


class Validation(models.Model):
    name = models.CharField(max_length=200, null=True)
    validation_schema = models.ForeignKey(ValidationSchema, on_delete=models.PROTECT)
