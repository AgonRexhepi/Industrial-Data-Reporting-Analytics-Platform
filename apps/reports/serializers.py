from __future__ import annotations

from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            "id",
            "title",
            "executive_summary",
            "report_format",
            "status",
            "generated_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "generated_at", "created_at", "updated_at")
