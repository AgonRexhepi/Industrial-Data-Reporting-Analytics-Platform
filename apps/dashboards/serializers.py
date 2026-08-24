"""Serializers for the dashboards app."""
from __future__ import annotations

from rest_framework import serializers

from .models import Dashboard, DashboardFilter, DashboardWidget


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = [
            "id",
            "title",
            "widget_type",
            "configuration",
            "position_x",
            "position_y",
            "width",
            "height",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardFilter
        fields = [
            "id",
            "label",
            "filter_type",
            "target_column",
            "default_value",
            "position",
        ]
        read_only_fields = ["id"]


class DashboardSerializer(serializers.ModelSerializer):
    widgets = DashboardWidgetSerializer(many=True, read_only=True)
    filters = DashboardFilterSerializer(many=True, read_only=True)

    class Meta:
        model = Dashboard
        fields = [
            "id",
            "name",
            "description",
            "is_public",
            "layout",
            "widgets",
            "filters",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = ["name", "description", "is_public", "layout"]
