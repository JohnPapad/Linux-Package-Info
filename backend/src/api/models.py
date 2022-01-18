# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from model_utils import Choices


class Package(models.Model):
    # DISTROS = Choices('Ubuntu', 'Debian', 'Fedora')
    
    name = models.CharField(max_length=50)
    distro = models.CharField(max_length=50)
    section = models.CharField(max_length=50, blank=True, default='')
    license = models.CharField(max_length=50, blank=True, default='')
    maintainer = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='')
    homepage = models.URLField(blank=True, default='')
    repo_URL = models.URLField(blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.distro})"

    class Meta:
        unique_together = [['name', 'distro']]


class PackageVersion(models.Model):
    package = models.ForeignKey(Package, related_name="versions", on_delete=models.CASCADE)
    version = models.CharField(max_length=50)
    architecture = models.CharField(max_length=20)
    swhid = models.CharField(max_length=100, blank=True, default='')
    swhid_exists = models.BooleanField(blank=True, null=True)
    size = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.00095)]) # in kBs
    binary_URL = models.URLField(blank=True, default='')

    rating = models.PositiveSmallIntegerField(blank=True, null=True, validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])

    def __str__(self):
        return f"{self.version}-{self.architecture}-{self.package}"

    class Meta:
        unique_together = [['package', 'version']]
