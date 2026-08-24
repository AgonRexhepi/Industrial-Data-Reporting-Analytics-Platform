"""Dashboard models — Phase 4 & 5."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class Dashboard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="dashboards",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_dashboards",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    layout = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboards_dashboard"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.organization})"


class DashboardWidget(models.Model):
    class WidgetType(models.TextChoices):
        KPI = "kpi", "KPI"
        TABLE = "table", "Table"
        BAR = "bar", "Bar Chart"
        LINE = "line", "Line Chart"
        PIE = "pie", "Pie Chart"
        AREA = "area", "Area Chart"
        SCATTER = "scatter", "Scatter Plot"
        HEATMAP = "heatmap", "Heatmap"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name="widgets",
    )
    title = models.CharField(max_length=255)
    widget_type = models.CharField(max_length=20, choices=WidgetType.choices)
    configuration = models.JSONField(default=dict)
    position_x = models.PositiveSmallIntegerField(default=0)
    position_y = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=6)
    height = models.PositiveSmallIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboards_widget"
        ordering = ["position_y", "position_x"]

    def __str__(self) -> str:
        return f"{self.title} ({self.widget_type}) on {self.dashboard}"


class DashboardFilter(models.Model):
    class FilterType(models.TextChoices):
        DATE = "date", "Date"
        TEXT = "text", "Text"
        SELECT = "select", "Select"
        MULTI_SELECT = "multi_select", "Multi Select"
        NUMBER_RANGE = "number_range", "Number Range"
        DATE_RANGE = "date_range", "Date Range"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name="filters",
    )
    label = models.CharField(max_length=255)
    filter_type = models.CharField(max_length=20, choices=FilterType.choices)
    target_column = models.CharField(max_length=500)
    default_value = models.JSONField(null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "dashboards_filter"
        ordering = ["position"]

    def __str__(self) -> str:
        return f"{self.label} ({self.filter_type}) on {self.dashboard}"
