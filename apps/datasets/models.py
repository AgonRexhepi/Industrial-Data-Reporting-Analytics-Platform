from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class Dataset(models.Model):
    class Status(models.TextChoices):
        UPLOADING = "uploading", "Uploading"
        PROCESSING = "processing", "Processing"
        VALIDATING = "validating", "Validating"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="datasets",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_datasets",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADING)
    row_count = models.PositiveIntegerField(null=True, blank=True)
    column_count = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "datasets_dataset"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.organization})"


class DatasetFile(models.Model):
    class Format(models.TextChoices):
        CSV = "csv", "CSV"
        EXCEL = "excel", "Excel"
        JSON = "json", "JSON"
        XML = "xml", "XML"
        PARQUET = "parquet", "Parquet"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="files",
    )
    original_filename = models.CharField(max_length=500)
    file_format = models.CharField(max_length=20, choices=Format.choices)
    file_path = models.CharField(max_length=1000)
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "datasets_dataset_file"

    def __str__(self) -> str:
        return self.original_filename


class DatasetVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField()
    file = models.ForeignKey(
        DatasetFile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="versions",
    )
    row_count = models.PositiveIntegerField(null=True, blank=True)
    column_count = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dataset_versions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "datasets_dataset_version"
        unique_together = ("dataset", "version_number")
        ordering = ["-version_number"]

    def __str__(self) -> str:
        return f"{self.dataset.name} v{self.version_number}"


class DatasetColumn(models.Model):
    class LogicalType(models.TextChoices):
        STRING = "string", "String"
        INTEGER = "integer", "Integer"
        DECIMAL = "decimal", "Decimal"
        BOOLEAN = "boolean", "Boolean"
        DATE = "date", "Date"
        DATETIME = "datetime", "Datetime"
        CURRENCY = "currency", "Currency"
        PERCENTAGE = "percentage", "Percentage"
        CATEGORY = "category", "Category"
        EMAIL = "email", "Email"
        URL = "url", "URL"
        UNKNOWN = "unknown", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset_version = models.ForeignKey(
        DatasetVersion,
        on_delete=models.CASCADE,
        related_name="columns",
    )
    name = models.CharField(max_length=500)
    original_name = models.CharField(max_length=500)
    logical_type = models.CharField(max_length=20, choices=LogicalType.choices, default=LogicalType.UNKNOWN)
    position = models.PositiveIntegerField()
    null_count = models.PositiveIntegerField(default=0)
    unique_count = models.PositiveIntegerField(default=0)
    min_value = models.TextField(blank=True, null=True)
    max_value = models.TextField(blank=True, null=True)
    mean_value = models.FloatField(null=True, blank=True)
    sample_values = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "datasets_dataset_column"
        ordering = ["position"]

    def __str__(self) -> str:
        return f"{self.name} ({self.logical_type})"


class DatasetQuality(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset_version = models.OneToOneField(
        DatasetVersion,
        on_delete=models.CASCADE,
        related_name="quality",
    )
    total_rows = models.PositiveIntegerField(default=0)
    total_columns = models.PositiveIntegerField(default=0)
    missing_cells = models.PositiveIntegerField(default=0)
    missing_percentage = models.FloatField(default=0.0)
    duplicate_rows = models.PositiveIntegerField(default=0)
    quality_score = models.FloatField(default=0.0)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "datasets_dataset_quality"

    def __str__(self) -> str:
        return f"Quality for {self.dataset_version} — {self.quality_score:.1f}%"
