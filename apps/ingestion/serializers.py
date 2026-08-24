from __future__ import annotations

import os

from django.conf import settings
from rest_framework import serializers

from apps.datasets.models import Dataset, DatasetFile

ALLOWED_EXTENSIONS = {
    "csv": DatasetFile.Format.CSV,
    "xlsx": DatasetFile.Format.EXCEL,
    "json": DatasetFile.Format.JSON,
    "xml": DatasetFile.Format.XML,
    "parquet": DatasetFile.Format.PARQUET,
}

MAX_UPLOAD_BYTES = getattr(settings, "MAX_UPLOAD_BYTES", 200 * 1024 * 1024)  # 200 MB


class DatasetUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField()

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1].lstrip(".").lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Unsupported file type '.{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        if value.size > MAX_UPLOAD_BYTES:
            raise serializers.ValidationError(
                f"File too large ({value.size / 1024 / 1024:.1f} MB). Maximum is {MAX_UPLOAD_BYTES / 1024 / 1024:.0f} MB."
            )
        return value
