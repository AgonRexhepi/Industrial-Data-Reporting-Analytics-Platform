from django.contrib import admin

from .models import Dataset, DatasetColumn, DatasetFile, DatasetQuality, DatasetVersion


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "status", "row_count", "column_count", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "organization__name")


@admin.register(DatasetFile)
class DatasetFileAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "file_format", "file_size", "dataset", "uploaded_at")
    list_filter = ("file_format",)


@admin.register(DatasetVersion)
class DatasetVersionAdmin(admin.ModelAdmin):
    list_display = ("dataset", "version_number", "row_count", "column_count", "created_at")


@admin.register(DatasetColumn)
class DatasetColumnAdmin(admin.ModelAdmin):
    list_display = ("name", "logical_type", "position", "null_count", "unique_count")
    list_filter = ("logical_type",)


@admin.register(DatasetQuality)
class DatasetQualityAdmin(admin.ModelAdmin):
    list_display = ("dataset_version", "quality_score", "total_rows", "missing_percentage", "calculated_at")
