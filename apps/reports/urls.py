from django.urls import path

from .views import ReportDetailView, ReportListCreateView, report_download_view, report_generate_view

urlpatterns = [
    path("", ReportListCreateView.as_view(), name="report-list"),
    path("<uuid:pk>/", ReportDetailView.as_view(), name="report-detail"),
    path("<uuid:pk>/generate/", report_generate_view, name="report-generate"),
    path("<uuid:pk>/download/", report_download_view, name="report-download"),
]
