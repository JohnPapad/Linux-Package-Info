from django.contrib import admin
from .models import Package, Package_Version

# Register your models here.
admin.site.register(Package)
admin.site.register(Package_Version)