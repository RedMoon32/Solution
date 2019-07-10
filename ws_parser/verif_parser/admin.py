from django.contrib import admin

# Register your models here.
from verif_parser.models import Company, Director

admin.site.register(Company)
admin.site.register(Director)
