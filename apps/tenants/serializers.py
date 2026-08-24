from __future__ import annotations

from django.utils.text import slugify
from rest_framework import serializers

from .models import Organization, OrganizationMember


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "is_active", "created_at")
        read_only_fields = ("id", "slug", "is_active", "created_at")

    def create(self, validated_data):
        base_slug = slugify(validated_data["name"])
        if not base_slug:
            raise serializers.ValidationError({"name": "Organization name must contain at least one alphanumeric character."})
        if Organization.objects.filter(slug=base_slug).exists():
            raise serializers.ValidationError({"name": f"An organization with the slug '{base_slug}' already exists."})
        validated_data["slug"] = base_slug
        return super().create(validated_data)


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = OrganizationMember
        fields = ("id", "organization", "user", "user_email", "user_full_name", "role", "joined_at")
        read_only_fields = ("id", "joined_at")
