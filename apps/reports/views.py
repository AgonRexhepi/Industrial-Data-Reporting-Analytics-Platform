from __future__ import annotations

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from apps.tenants.models import OrganizationMember

from .models import Report
from .serializers import ReportSerializer


class OrganizationReportMixin:
    permission_classes = [permissions.IsAuthenticated]

    def _get_org_id(self) -> str:
        return self.kwargs["org_pk"]

    def _assert_member(self):
        if not OrganizationMember.objects.filter(organization_id=self._get_org_id(), user=self.request.user).exists():
            raise NotFound("Organization not found.")

    def get_queryset(self):
        self._assert_member()
        return Report.objects.filter(organization_id=self._get_org_id())


class ReportListCreateView(OrganizationReportMixin, generics.ListCreateAPIView):
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        self._assert_member()
        serializer.save(organization_id=self._get_org_id(), created_by=self.request.user)


class ReportDetailView(OrganizationReportMixin, generics.RetrieveAPIView):
    serializer_class = ReportSerializer


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def report_generate_view(request, org_pk, pk):
    if not OrganizationMember.objects.filter(organization_id=org_pk, user=request.user).exists():
        raise NotFound("Organization not found.")
    report = Report.objects.filter(pk=pk, organization_id=org_pk).first()
    if not report:
        raise NotFound("Report not found.")

    report.status = Report.Status.GENERATED
    report.generated_at = timezone.now()
    report.generated_file_path = f"reports/{report.id}.{report.report_format}"
    report.save(update_fields=["status", "generated_at", "generated_file_path", "updated_at"])

    return Response(ReportSerializer(report).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def report_download_view(request, org_pk, pk):
    if not OrganizationMember.objects.filter(organization_id=org_pk, user=request.user).exists():
        raise NotFound("Organization not found.")
    report = Report.objects.filter(pk=pk, organization_id=org_pk).first()
    if not report:
        raise NotFound("Report not found.")
    if report.status != Report.Status.GENERATED or not report.generated_file_path:
        raise ValidationError("Report has not been generated yet.")

    filename = f"{report.title.strip().replace(' ', '_') or 'report'}.{report.report_format}"
    return Response(
        {
            "id": str(report.id),
            "filename": filename,
            "file_path": report.generated_file_path,
            "generated_at": report.generated_at,
        },
        status=status.HTTP_200_OK,
    )
