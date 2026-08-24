"""Whitelist validators for analytics query parameters."""
from __future__ import annotations

from rest_framework.exceptions import ValidationError

ALLOWED_AGGREGATIONS = {"count", "sum", "avg", "min", "max", "median", "std", "distinct_count"}

ALLOWED_FILTER_OPERATORS = {"=", "!=", ">", ">=", "<", "<=", "in", "not_in", "contains", "starts_with", "ends_with", "is_null", "is_not_null"}

ALLOWED_SORT_DIRECTIONS = {"asc", "desc"}

ALLOWED_DATE_GROUPINGS = {"year", "quarter", "month", "week", "day", "hour"}


def validate_aggregation(value: str) -> str:
    v = value.lower()
    if v not in ALLOWED_AGGREGATIONS:
        raise ValidationError(f"Invalid aggregation '{value}'. Allowed: {sorted(ALLOWED_AGGREGATIONS)}")
    return v


def validate_filter_operator(value: str) -> str:
    v = value.lower()
    if v not in ALLOWED_FILTER_OPERATORS:
        raise ValidationError(f"Invalid operator '{value}'. Allowed: {sorted(ALLOWED_FILTER_OPERATORS)}")
    return v


def validate_sort_direction(value: str) -> str:
    v = value.lower()
    if v not in ALLOWED_SORT_DIRECTIONS:
        raise ValidationError(f"Invalid sort direction '{value}'. Allowed: asc, desc")
    return v


def validate_column_name(name: str, available: list[str]) -> str:
    if name not in available:
        raise ValidationError(f"Column '{name}' not found. Available: {available}")
    return name
