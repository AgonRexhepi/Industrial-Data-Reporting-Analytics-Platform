from __future__ import annotations

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Organization, OrganizationMember
from .serializers import OrganizationMemberSerializer, OrganizationSerializer


class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(
            members__user=self.request.user,
            is_active=True,
        )

    def perform_create(self, serializer):
        org = serializer.save()
        OrganizationMember.objects.create(
            organization=org,
            user=self.request.user,
            role=OrganizationMember.Role.OWNER,
        )


class OrganizationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(
            members__user=self.request.user,
            is_active=True,
        )


class OrganizationMemberListView(generics.ListCreateAPIView):
    serializer_class = OrganizationMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrganizationMember.objects.filter(
            organization_id=self.kwargs["org_pk"],
            organization__members__user=self.request.user,
        )

    def _get_org_or_403(self):
        """Return the organization if the current user is an owner or admin, else raise 403."""
        try:
            membership = OrganizationMember.objects.get(
                organization_id=self.kwargs["org_pk"],
                user=self.request.user,
            )
        except OrganizationMember.DoesNotExist:
            raise PermissionDenied("You are not a member of this organization.")
        if membership.role not in (OrganizationMember.Role.OWNER, OrganizationMember.Role.ADMIN):
            raise PermissionDenied("Only owners and admins can manage members.")
        return membership.organization

    def perform_create(self, serializer):
        org = self._get_org_or_403()
        serializer.save(organization=org)
