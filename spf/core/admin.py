from django.contrib import admin
from .models import Journal, Package, Document, DocumentFile, DocumentAsset, ValidationSchema, Validation


admin.site.register(Journal)
admin.site.register(Package)
admin.site.register(Document)
admin.site.register(DocumentFile)
admin.site.register(DocumentAsset)
admin.site.register(ValidationSchema)
admin.site.register(Validation)
