"""Aggregation helpers for the analytics engine."""
from __future__ import annotations

import pandas as pd

from .validators import validate_aggregation


def apply_aggregation(series: pd.Series, aggregation: str) -> float | int:
    """Apply a single aggregation function to a Series."""
    agg = validate_aggregation(aggregation)

    if agg == "count":
        return int(series.count())
    elif agg == "sum":
        return float(series.sum())
    elif agg == "avg":
        return float(series.mean())
    elif agg == "min":
        return series.min()
    elif agg == "max":
        return series.max()
    elif agg == "median":
        return float(series.median())
    elif agg == "std":
        return float(series.std())
    elif agg == "distinct_count":
        return int(series.nunique())
    elif agg == "percentage":
        total = len(series)
        return round(float(series.count()) / total * 100, 2) if total else 0.0

    return None  # pragma: no cover
