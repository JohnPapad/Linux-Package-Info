from rest_framework import serializers
from .models import Package, PackageVersion


class PackageVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageVersion
        fields= "__all__"


class PackageSerializer(serializers.ModelSerializer):
    versions = PackageVersionSerializer(many=True)
    class Meta:
        model = Package
        fields= "__all__"