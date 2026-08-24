"""URL configuration for the analytics app."""
from __future__ import annotations

from django.urls import path

from .views import AnalyticsQueryView, AnalyticsStatisticsView

urlpatterns = [
    path("query/", AnalyticsQueryView.as_view(), name="analytics-query"),
    path("statistics/", AnalyticsStatisticsView.as_view(), name="analytics-statistics"),
]
