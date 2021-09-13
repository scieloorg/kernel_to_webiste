from django.db import models
from django.contrib.auth.models import User

from opac_schema.v1.models import *






class Event(models.Model):
    # quem realiza o evento
    actor = models.ForeignKey(User, on_delete=models.PROTECT)

    # momento em que o evento foi iniciado
    datetime = models.DateTimeField(auto_now=True)

    # nome do evento
    name = models.CharField(max_length=200)

    # estado do evento (iniciado, realizando, concluído)

    # informação relacionada ao evento
    annotation = models.CharField(max_length=200, null=True)


class ValidationSchema(models.Model):
    schema_name = models.CharField(max_length=200, null=True)


class Validation(models.Model):
    name = models.CharField(max_length=200, null=True)
    validation_schema = models.ForeignKey(ValidationSchema, on_delete=models.PROTECT)
