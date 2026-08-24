from django.contrib import admin
from django.urls import include, path

from apps.core.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("api/health/", HealthCheckView.as_view(), name="api-health-check"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/organizations/", include("apps.tenants.urls")),
    path(
        "api/v1/organizations/<uuid:org_pk>/datasets/",
        include("apps.datasets.urls"),
    ),
    path(
        "api/v1/organizations/<uuid:org_pk>/ingestion/",
        include("apps.ingestion.urls"),
    ),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path(
        "api/v1/organizations/<uuid:org_pk>/dashboards/",
        include("apps.dashboards.urls"),
    ),
]
