from django.contrib import admin
from .models import Package, PackageVersion

# Register your models here.
admin.site.register(Package)
admin.site.register(PackageVersion)