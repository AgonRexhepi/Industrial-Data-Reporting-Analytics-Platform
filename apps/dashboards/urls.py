"""URL configuration for the dashboards app."""
from __future__ import annotations

from django.urls import path

from .views import (
    DashboardDetailView,
    DashboardExecuteView,
    DashboardFilterListCreateView,
    DashboardListCreateView,
    DashboardWidgetDetailView,
    DashboardWidgetListCreateView,
)

urlpatterns = [
    path("", DashboardListCreateView.as_view(), name="dashboard-list"),
    path("<uuid:pk>/", DashboardDetailView.as_view(), name="dashboard-detail"),
    path("<uuid:dashboard_pk>/widgets/", DashboardWidgetListCreateView.as_view(), name="dashboard-widget-list"),
    path(
        "<uuid:dashboard_pk>/widgets/<uuid:pk>/",
        DashboardWidgetDetailView.as_view(),
        name="dashboard-widget-detail",
    ),
    path("<uuid:dashboard_pk>/filters/", DashboardFilterListCreateView.as_view(), name="dashboard-filter-list"),
    path("<uuid:pk>/execute/", DashboardExecuteView.as_view(), name="dashboard-execute"),
]
