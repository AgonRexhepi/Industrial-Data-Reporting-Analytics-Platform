"""Analytics API views — Phase 3."""
from __future__ import annotations

import logging

from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.datasets.models import Dataset, DatasetVersion
from apps.tenants.models import OrganizationMember

from .engine.filtering import apply_filters
from .engine.query_builder import run_query
from .engine.statistics import compute_statistics
from .serializers import AnalyticsQuerySerializer, StatisticsQuerySerializer

logger = logging.getLogger(__name__)


def _load_dataset_df(dataset_id: str, user):
    """Load the latest ready version of *dataset_id* as a DataFrame.

    Raises NotFound if the dataset doesn't exist or the user lacks access.
    """
    from apps.ingestion.parsers import parse_file

    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        raise NotFound("Dataset not found.")

    if not OrganizationMember.objects.filter(
        organization=dataset.organization, user=user
    ).exists():
        raise NotFound("Dataset not found.")

    version: DatasetVersion | None = dataset.versions.order_by("-version_number").first()
    if version is None or version.file is None:
        raise ValidationError("Dataset has no processed version.")

    df = parse_file(version.file.file_path, version.file.file_format)
    return df


class AnalyticsQueryView(APIView):
    """POST /api/v1/analytics/query/ — run an ad-hoc analytics query."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AnalyticsQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        df = _load_dataset_df(str(data["dataset_id"]), request.user)

        try:
            result = run_query(df, data)
        except ValidationError:
            raise
        except Exception as exc:
            logger.exception("Analytics query error: %s", exc)
            raise ValidationError("An error occurred while executing the query.") from exc

        return Response(result, status=status.HTTP_200_OK)


class AnalyticsStatisticsView(APIView):
    """POST /api/v1/analytics/statistics/ — compute descriptive statistics."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = StatisticsQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        df = _load_dataset_df(str(data["dataset_id"]), request.user)

        filters = data.get("filters") or []
        if filters:
            df = apply_filters(df, filters)

        columns = data.get("columns") or []
        try:
            stats = compute_statistics(df, columns or None)
        except Exception as exc:
            logger.exception("Statistics error: %s", exc)
            raise ValidationError("An error occurred while computing statistics.") from exc

        return Response({"statistics": stats}, status=status.HTTP_200_OK)
