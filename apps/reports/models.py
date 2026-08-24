from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class Report(models.Model):
    class Format(models.TextChoices):
        PDF = "pdf", "PDF"
        XLSX = "xlsx", "XLSX"
        CSV = "csv", "CSV"
        HTML = "html", "HTML"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("tenants.Organization", on_delete=models.CASCADE, related_name="reports")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_reports",
    )
    title = models.CharField(max_length=255)
    executive_summary = models.TextField(blank=True)
    report_format = models.CharField(max_length=10, choices=Format.choices, default=Format.PDF)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    generated_file_path = models.CharField(max_length=1000, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reports_report"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.organization})"
