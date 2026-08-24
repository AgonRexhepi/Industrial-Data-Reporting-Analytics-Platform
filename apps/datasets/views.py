from __future__ import annotations

from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound

from apps.tenants.models import OrganizationMember

from .models import Dataset, DatasetVersion
from .serializers import DatasetSerializer, DatasetVersionSerializer


class OrganizationDatasetMixin:
    """Restrict queryset to datasets belonging to the caller's organization."""

    permission_classes = [permissions.IsAuthenticated]

    def _get_org_id(self) -> str:
        return self.kwargs["org_pk"]

    def _assert_member(self):
        org_id = self._get_org_id()
        if not OrganizationMember.objects.filter(
            organization_id=org_id,
            user=self.request.user,
        ).exists():
            raise NotFound("Organization not found.")

    def get_queryset(self):
        self._assert_member()
        return Dataset.objects.filter(organization_id=self._get_org_id())


class DatasetListView(OrganizationDatasetMixin, generics.ListAPIView):
    serializer_class = DatasetSerializer


class DatasetDetailView(OrganizationDatasetMixin, generics.RetrieveAPIView):
    serializer_class = DatasetSerializer


class DatasetVersionListView(generics.ListAPIView):
    serializer_class = DatasetVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = self.kwargs["org_pk"]
        dataset_id = self.kwargs["dataset_pk"]
        if not OrganizationMember.objects.filter(organization_id=org_id, user=self.request.user).exists():
            raise NotFound("Organization not found.")
        return DatasetVersion.objects.filter(
            dataset_id=dataset_id,
            dataset__organization_id=org_id,
        )


class DatasetVersionDetailView(generics.RetrieveAPIView):
    serializer_class = DatasetVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = self.kwargs["org_pk"]
        dataset_id = self.kwargs["dataset_pk"]
        if not OrganizationMember.objects.filter(organization_id=org_id, user=self.request.user).exists():
            raise NotFound("Organization not found.")
        return DatasetVersion.objects.filter(
            dataset_id=dataset_id,
            dataset__organization_id=org_id,
        )
