# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin
from .models import Package, PackageVersion, Rating

# Register your models here.

class PackageModelAdmin(admin.ModelAdmin):
    list_filter = [
        "distro"
    ]
    search_fields = (
        "name",
    )

admin.site.register(Package, PackageModelAdmin)
admin.site.register(PackageVersion)
admin.site.register(Rating)
