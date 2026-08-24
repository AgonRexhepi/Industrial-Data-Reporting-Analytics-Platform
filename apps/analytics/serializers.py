"""Serializers for analytics query requests."""
from __future__ import annotations

from rest_framework import serializers


class MeasureSerializer(serializers.Serializer):
    column = serializers.CharField()
    aggregation = serializers.CharField()


class FilterSerializer(serializers.Serializer):
    column = serializers.CharField()
    operator = serializers.CharField()
    value = serializers.JSONField(required=False, allow_null=True)


class DateGroupingSerializer(serializers.Serializer):
    column = serializers.CharField()
    grouping = serializers.CharField()


class SortSerializer(serializers.Serializer):
    column = serializers.CharField()
    direction = serializers.CharField(default="asc")


class AnalyticsQuerySerializer(serializers.Serializer):
    dataset_id = serializers.UUIDField()
    dimensions = serializers.ListField(child=serializers.CharField(), default=list)
    measures = MeasureSerializer(many=True, default=list)
    filters = FilterSerializer(many=True, default=list)
    date_groupings = DateGroupingSerializer(many=True, default=list)
    sort = SortSerializer(required=False, allow_null=True)
    limit = serializers.IntegerField(default=1000, min_value=1, max_value=100_000)


class StatisticsQuerySerializer(serializers.Serializer):
    dataset_id = serializers.UUIDField()
    columns = serializers.ListField(child=serializers.CharField(), default=list)
    filters = FilterSerializer(many=True, default=list)
