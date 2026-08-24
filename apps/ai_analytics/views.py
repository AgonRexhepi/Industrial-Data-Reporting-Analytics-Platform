from __future__ import annotations

from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import OrganizationMember

from .serializers import AIQuerySerializer


class AIQueryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, org_pk):
        if not OrganizationMember.objects.filter(organization_id=org_pk, user=request.user).exists():
            raise NotFound("Organization not found.")

        serializer = AIQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data["query"]
        lowered_query = query.lower()

        suggested_operations = ["statistics"]
        if any(token in lowered_query for token in ("trend", "over time", "monthly", "daily")):
            suggested_operations.append("date_analysis")
        if any(token in lowered_query for token in ("anomaly", "anomalies", "outlier", "outliers")):
            suggested_operations.append("anomaly_detection")
        if any(token in lowered_query for token in ("forecast", "predict")):
            suggested_operations.append("forecasting")

        return Response(
            {
                "message": "AI analytics is available in preview mode.",
                "query": query,
                "suggested_operations": sorted(set(suggested_operations)),
                "next_step": "Use analytics endpoints to execute validated operations.",
            }
        )
