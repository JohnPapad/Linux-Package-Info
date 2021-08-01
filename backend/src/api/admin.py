# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin
from .models import Package, PackageVersion

# Register your models here.
admin.site.register(Package)
admin.site.register(PackageVersion)
