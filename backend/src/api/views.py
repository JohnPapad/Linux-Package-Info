from .serializers import PackageVersionSerializer, PackageSerializer
from rest_framework import viewsets
from . import models
from rest_framework.permissions import AllowAny


class PackageViewSet(viewsets.ModelViewSet):
    queryset = models.Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]