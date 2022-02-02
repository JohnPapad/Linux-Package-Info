# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class MyUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'email', 'is_staff', 'is_superuser', 'is_active']


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)