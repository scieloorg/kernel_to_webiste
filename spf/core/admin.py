from django.contrib import admin
from .models import Event, ValidationSchema, Validation

admin.site.register(Event)
admin.site.register(ValidationSchema)
admin.site.register(Validation)
