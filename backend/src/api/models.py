from django.db import models
from model_utils import Choices

# t(["Version", "Section", "Installed-Size", "Homepage", "Description", "Original-Maintainer"])


class Package(models.Model):
    DISTROS = Choices('Ubuntu', 'Debian', 'Fedora')
    
    name = models.CharField(max_length=50)
    distro = models.CharField(max_length=50, choices=DISTROS)
    section = models.CharField(max_length=50, blank=True, default='')
    license = models.CharField(max_length=50, blank=True, default='')
    maintainer = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='')
    homepage = models.URLField(blank=True, default='')
    size = models.PositiveIntegerField(blank=True, null=True) # in MBs

    def __str__(self):
        return f"{self.name} ({self.distro})"

    class Meta:
        unique_together = [['name', 'distro']]


class PackageVersion(models.Model):
    VERSION_ARCHs = Choices("amd64", "i386", "amd64 i386")

    package = models.ForeignKey(Package, related_name="versions", on_delete=models.CASCADE)
    version = models.CharField(max_length=50)
    architecture = models.CharField(max_length=20, choices=VERSION_ARCHs)
    swhid = models.CharField(max_length=100, blank=True, default='')
    swhid_exists = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f"{self.version}-{self.architecture}"