# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from rest_framework import serializers
from .models import Package, PackageVersion


class PackageVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageVersion
        fields = "__all__"
        # exclude = ["package"]
        extra_kwargs = {
            'package': { 'read_only': True }
        }


class PackageSerializer(serializers.ModelSerializer):
    versions = PackageVersionSerializer(many=True)

    def validate_versions(self, versions):
        if len(versions) == 0:
            raise serializers.ValidationError("This field must not be empty.")
            
        return versions

    class Meta:
        model = Package
        fields = "__all__"

    def create(self, validated_data):
        versions = validated_data.pop('versions')
        pkg = Package.objects.create(**validated_data)
        for version in versions:
            PackageVersion.objects.create(package=pkg, **version)

        return pkg
