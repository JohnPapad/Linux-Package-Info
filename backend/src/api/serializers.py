# Copyright 2021 Ioannis Papadopoulos
# SPDX-License-Identifier: AGPL-3.0-or-later

from rest_framework import serializers
from .models import Package, PackageVersion, Rating
from model_utils import Choices


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"


class PackageVersionSerializer(serializers.ModelSerializer):
    # ratings = RatingSerializer(many=True) # read_only=True
    rating = serializers.FloatField(read_only=True) # serializers.ReadOnlyField()
    class Meta:
        model = PackageVersion
        fields = "__all__"
        # exclude = ["package"]
        extra_kwargs = {
            'package': { 'read_only': True }
        }


class PackageSerializer(serializers.ModelSerializer):
    versions = PackageVersionSerializer(many=True)

    rating = serializers.SerializerMethodField()
    def get_rating(self, package):
        sum_rating = 0
        num_of_ratings = 0
        pkg_versions = package.versions.all()
        for version in pkg_versions:
            version_ratings = version.ratings.all()
            for rating in version_ratings:
                sum_rating += rating.rate

            num_of_ratings += version_ratings.count()

        if num_of_ratings == 0:
            return None
            
        return sum_rating / num_of_ratings

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


class CreateDockerfileSerializer(serializers.Serializer):
    distro_name = serializers.ChoiceField(required=True, choices=Choices("Ubuntu", "Debian", "Kali", "Fedora", "CentOS"))
    distro_type = serializers.ChoiceField(required=True, choices=Choices("deb", "rpm"))
    distro_version = serializers.CharField(required=True)
    packages = serializers.ListField(required=True,
        child = serializers.DictField(required=True)
    )

    class Meta:
        fields = "__all__"