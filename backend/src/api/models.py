# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Package(models.Model):    
    name = models.CharField(max_length=50)
    distro = models.CharField(max_length=50)
    type = models.CharField(max_length=20, default='')
    section = models.CharField(max_length=50, blank=True, default='')
    license = models.CharField(max_length=200, blank=True, default='')
    maintainer = models.CharField(max_length=200, blank=True, default='')
    description = models.CharField(max_length=300, blank=True, default='')
    homepage = models.URLField(blank=True, default='')
    repo_URL = models.URLField(blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.distro})"

    class Meta:
        unique_together = [['name', 'distro']]
        ordering = ['name', 'distro']


class PackageVersion(models.Model):
    package = models.ForeignKey(Package, related_name="versions", on_delete=models.CASCADE)
    version = models.CharField(max_length=100)
    architecture = models.CharField(max_length=50)
    swhid = models.CharField(max_length=100, blank=True, default='')
    swhid_exists = models.BooleanField(blank=True, null=True)
    size = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0.00095)]) # in kBs
    binary_URL = models.URLField(blank=True, default='')

    @property
    def rating(self):
        return self.ratings.all().aggregate(models.Avg('rate'))['rate__avg']

    def __str__(self):
        return f"{self.version}-{self.architecture}-{self.package}"

    class Meta:
        unique_together = [['package', 'version']]
        ordering = ['-version']


class Rating(models.Model):
    rate = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    pkg_version = models.ForeignKey(PackageVersion, related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['pkg_version', 'user']]