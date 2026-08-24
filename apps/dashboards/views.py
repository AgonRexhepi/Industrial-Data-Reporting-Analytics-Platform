"""Dashboard views — Phase 5."""
from __future__ import annotations

import logging

from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import OrganizationMember

from .models import Dashboard, DashboardFilter, DashboardWidget
from .serializers import (
    DashboardFilterSerializer,
    DashboardSerializer,
    DashboardWidgetSerializer,
    DashboardWriteSerializer,
)

logger = logging.getLogger(__name__)


class OrganizationDashboardMixin:
    permission_classes = [permissions.IsAuthenticated]

    def _get_org_id(self) -> str:
        return str(self.kwargs["org_pk"])

    def _assert_member(self):
        if not OrganizationMember.objects.filter(
            organization_id=self._get_org_id(), user=self.request.user
        ).exists():
            raise NotFound("Organization not found.")

    def get_queryset(self):
        self._assert_member()
        return Dashboard.objects.filter(organization_id=self._get_org_id())


class DashboardListCreateView(OrganizationDashboardMixin, generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return DashboardWriteSerializer
        return DashboardSerializer

    def perform_create(self, serializer):
        self._assert_member()
        from apps.tenants.models import Organization

        try:
            org = Organization.objects.get(pk=self._get_org_id())
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")
        serializer.save(organization=org, created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        write_serializer = DashboardWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        read_serializer = DashboardSerializer(write_serializer.instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class DashboardDetailView(OrganizationDashboardMixin, generics.RetrieveUpdateDestroyAPIView):
    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return DashboardWriteSerializer
        return DashboardSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        write_serializer = DashboardWriteSerializer(instance, data=request.data, partial=partial)
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save()
        read_serializer = DashboardSerializer(write_serializer.instance)
        return Response(read_serializer.data)


# ──────────────────────────────────────────────────────────────────────────────
# Widget views
# ──────────────────────────────────────────────────────────────────────────────

class DashboardWidgetListCreateView(generics.ListCreateAPIView):
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_dashboard(self) -> Dashboard:
        org_id = str(self.kwargs["org_pk"])
        if not OrganizationMember.objects.filter(organization_id=org_id, user=self.request.user).exists():
            raise NotFound("Organization not found.")
        try:
            return Dashboard.objects.get(pk=self.kwargs["dashboard_pk"], organization_id=org_id)
        except Dashboard.DoesNotExist:
            raise NotFound("Dashboard not found.")

    def get_queryset(self):
        return DashboardWidget.objects.filter(dashboard=self._get_dashboard())

    def perform_create(self, serializer):
        serializer.save(dashboard=self._get_dashboard())


class DashboardWidgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = str(self.kwargs["org_pk"])
        if not OrganizationMember.objects.filter(organization_id=org_id, user=self.request.user).exists():
            raise NotFound("Organization not found.")
        return DashboardWidget.objects.filter(dashboard__organization_id=org_id, dashboard_id=self.kwargs["dashboard_pk"])


# ──────────────────────────────────────────────────────────────────────────────
# Filter views
# ──────────────────────────────────────────────────────────────────────────────

class DashboardFilterListCreateView(generics.ListCreateAPIView):
    serializer_class = DashboardFilterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _get_dashboard(self) -> Dashboard:
        org_id = str(self.kwargs["org_pk"])
        if not OrganizationMember.objects.filter(organization_id=org_id, user=self.request.user).exists():
            raise NotFound("Organization not found.")
        try:
            return Dashboard.objects.get(pk=self.kwargs["dashboard_pk"], organization_id=org_id)
        except Dashboard.DoesNotExist:
            raise NotFound("Dashboard not found.")

    def get_queryset(self):
        return DashboardFilter.objects.filter(dashboard=self._get_dashboard())

    def perform_create(self, serializer):
        serializer.save(dashboard=self._get_dashboard())


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard execute view
# ──────────────────────────────────────────────────────────────────────────────

class DashboardExecuteView(APIView):
    """POST /api/v1/organizations/<org>/dashboards/<id>/execute/

    Execute all widgets in a dashboard, returning data for each widget.
    Accepts optional global filter overrides in the request body.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, org_pk, pk):
        org_id = str(org_pk)
        if not OrganizationMember.objects.filter(organization_id=org_id, user=request.user).exists():
            raise NotFound("Organization not found.")

        try:
            dashboard = Dashboard.objects.prefetch_related("widgets").get(pk=pk, organization_id=org_id)
        except Dashboard.DoesNotExist:
            raise NotFound("Dashboard not found.")

        from apps.analytics.engine.query_builder import run_query
        from apps.analytics.views import _load_dataset_df

        global_filters = request.data.get("filters") or []

        results = []
        for widget in dashboard.widgets.all():
            config = dict(widget.configuration or {})
            dataset_id = config.get("dataset_id")
            if not dataset_id:
                results.append({"widget_id": str(widget.id), "error": "No dataset_id in configuration"})
                continue

            try:
                df = _load_dataset_df(str(dataset_id), request.user)
                query = {
                    "dimensions": config.get("dimensions") or [],
                    "measures": config.get("measures") or [],
                    "filters": (config.get("filters") or []) + global_filters,
                    "sort": config.get("sort"),
                    "limit": config.get("limit") or 1000,
                }
                data = run_query(df, query)
                results.append({"widget_id": str(widget.id), "widget_type": widget.widget_type, "data": data})
            except Exception as exc:
                logger.exception("Widget %s execution error: %s", widget.id, exc)
                results.append({"widget_id": str(widget.id), "error": str(exc)})

        return Response({"dashboard_id": str(dashboard.id), "results": results})
