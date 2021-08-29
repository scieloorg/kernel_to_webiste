from django.db import models
from django.contrib.auth.models import User

from opac_schema.v1.models import *
from opac_schema.v2.models import *


class Journal(models.Model):
    print_issn = models.CharField(max_length=9)
    online_issn = models.CharField(max_length=9)
    title = models.CharField(max_length=255)
    abbreviated_title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Package(models.Model):
    name = models.CharField(max_length=200)
    deposit_date = models.DateTimeField(auto_now=True)
    state = models.IntegerField(default=0)
    depositor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Document(models.Model):
    name = models.CharField(max_length=200)
    pid = models.CharField(max_length=200)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)


class DocumentFile(models.Model):
    name = models.CharField(max_length=200)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    file = models.FileField()


class DocumentAsset(models.Model):
    name = models.CharField(max_length=200)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    file = models.FileField()


class ValidationSchema(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT)


class Validation(models.Model):
    name = models.CharField(max_length=200)
    validation_schema = models.ForeignKey(ValidationSchema, on_delete=models.PROTECT)
