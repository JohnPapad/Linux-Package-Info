# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from .serializers import PackageVersionSerializer, PackageSerializer, RatingSerializer, CreateDockerfileSerializer
from rest_framework import viewsets, mixins, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from django_filters.rest_framework import DjangoFilterBackend
from rest_access_policy import AccessPolicy
from .dockerfile_renderer import DockerfileRenderer
from django.db.models import Avg
from . import models


class PackageAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve", "dockerfile"],
            "principal": ["*"],
            "effect": "allow"
        },
        {
            "action": ["create", "versions"],
            "principal": ["group:API_PRIV"],
            "effect": "allow"
        },
        {
            "action": ["*"],
            "principal": ["admin", "staff"],
            "effect": "allow"
        }
    ]


class PackageViewSet(viewsets.ModelViewSet):
    queryset = models.Package.objects.all().annotate(avg_rating=Avg('versions__ratings__rate'))
    serializer_class = PackageSerializer
    permission_classes = [PackageAccessPolicy]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    # filterset_fields = ['name', 'distro', 'type', 'section', 'versions__architecture']
    filterset_fields = {
        'name': ['exact', "icontains"],
        'distro': ['exact', 'in'],
        'type': ['exact', 'in'],
        'section': ['exact', 'in'],
        'versions__architecture': ['exact', 'icontains'],
        # 'rating': ['gte', 'lte'],
    }
    ordering_fields = ['avg_rating', 'name', 'distro', 'type', 'section']

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

    @action(detail=False, methods=['post'], serializer_class=CreateDockerfileSerializer, renderer_classes=[DockerfileRenderer])
    def dockerfile(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(request.data, status=status.HTTP_201_CREATED, headers = {'Content-Disposition': f'attachment; filename={request.data["distro_name"]}.Dockerfile'})


class PackageVersionViewSet(viewsets.ModelViewSet):
    queryset = models.PackageVersion.objects.all()
    serializer_class = PackageVersionSerializer
    permission_classes = [PackageAccessPolicy]


class RatingAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow"
        },
        {
            "action": ["create"],
            "principal": ["group:API_PRIV", "authenticated"],
            "effect": "allow",
            "condition": ["is_request_from_own_user"]
        },
        {
            "action": ["*"],
            "principal": ["admin", "staff"],
            "effect": "allow"
        }
    ]

    def is_request_from_own_user(self, request, view, action) -> bool:
        return request.user.id == request.data.get("user")


class RatingViewSet(viewsets.ModelViewSet):
    queryset = models.Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [RatingAccessPolicy]
