from django.contrib import admin
from .models import Event, IngressPackage, ValidationSchema, Validation

admin.site.register(Event)
admin.site.register(IngressPackage)
admin.site.register(ValidationSchema)
admin.site.register(Validation)
