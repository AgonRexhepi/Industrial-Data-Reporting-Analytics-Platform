from __future__ import annotations

from rest_framework import serializers

from .models import Dataset, DatasetColumn, DatasetFile, DatasetQuality, DatasetVersion


class DatasetFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetFile
        fields = ("id", "original_filename", "file_format", "file_size", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class DatasetColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetColumn
        fields = (
            "id",
            "name",
            "original_name",
            "logical_type",
            "position",
            "null_count",
            "unique_count",
            "min_value",
            "max_value",
            "mean_value",
            "sample_values",
        )
        read_only_fields = ("id",)


class DatasetQualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DatasetQuality
        fields = (
            "id",
            "total_rows",
            "total_columns",
            "missing_cells",
            "missing_percentage",
            "duplicate_rows",
            "quality_score",
            "calculated_at",
        )
        read_only_fields = ("id", "calculated_at")


class DatasetVersionSerializer(serializers.ModelSerializer):
    columns = DatasetColumnSerializer(many=True, read_only=True)
    quality = DatasetQualitySerializer(read_only=True)

    class Meta:
        model = DatasetVersion
        fields = ("id", "version_number", "row_count", "column_count", "notes", "created_at", "columns", "quality")
        read_only_fields = ("id", "version_number", "row_count", "column_count", "created_at")


class DatasetSerializer(serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = (
            "id",
            "name",
            "description",
            "status",
            "row_count",
            "column_count",
            "created_at",
            "updated_at",
            "latest_version",
        )
        read_only_fields = ("id", "status", "row_count", "column_count", "created_at", "updated_at")

    def get_latest_version(self, obj) -> int | None:
        version = obj.versions.order_by("-version_number").first()
        return version.version_number if version else None
