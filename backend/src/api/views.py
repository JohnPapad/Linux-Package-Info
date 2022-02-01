# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from .serializers import PackageVersionSerializer, PackageSerializer, RatingSerializer
from rest_framework import viewsets, mixins, filters, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from django_filters.rest_framework import DjangoFilterBackend
from . import models


class PackageViewSet(viewsets.ModelViewSet):
    queryset = models.Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
        
    filterset_fields = ['name', 'distro', 'type', 'section', 'versions__architecture']
    search_fields = ['name', 'description']

    @action(detail=True, methods=['post'], serializer_class=PackageVersionSerializer)
    def versions(self, request, pk=None):
        if type(request.data) is not list or len(request.data) == 0:
            raise ParseError(detail="Request data must be a non empty list.")

        for req_data_pkg_ver in request.data:
            serializer = self.get_serializer(data=req_data_pkg_ver)
            serializer.is_valid(raise_exception=True)

        pkg = self.get_object()

        for req_data_pkg_ver in request.data:
            models.PackageVersion.objects.create(package=pkg, **req_data_pkg_ver)

        return Response({'status': 'versions set'}, status=status.HTTP_201_CREATED)


class PackageVersionViewSet(viewsets.ModelViewSet):
    queryset = models.PackageVersion.objects.all()
    serializer_class = PackageVersionSerializer
    permission_classes = [AllowAny]


class RatingViewSet(viewsets.ModelViewSet):
    queryset = models.Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [AllowAny]
