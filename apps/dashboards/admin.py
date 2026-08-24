from django.contrib import admin

from .models import Dashboard, DashboardFilter, DashboardWidget


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "is_public", "created_at"]
    list_filter = ["is_public", "organization"]


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ["title", "widget_type", "dashboard"]
    list_filter = ["widget_type"]


@admin.register(DashboardFilter)
class DashboardFilterAdmin(admin.ModelAdmin):
    list_display = ["label", "filter_type", "dashboard"]
