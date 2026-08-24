"""Descriptive statistics helpers for the analytics engine."""
from __future__ import annotations

import pandas as pd


def compute_statistics(df: pd.DataFrame, columns: list[str] | None = None) -> dict:
    """Return per-column descriptive statistics."""
    cols = columns or df.columns.tolist()
    stats: dict[str, dict] = {}

    for col in cols:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        entry: dict = {
            "count": int(df[col].count()),
            "null_count": int(df[col].isna().sum()),
            "unique_count": int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            entry.update({
                "min": _safe(series.min()),
                "max": _safe(series.max()),
                "mean": _safe(series.mean()),
                "median": _safe(series.median()),
                "std": _safe(series.std()),
                "sum": _safe(series.sum()),
            })
        stats[col] = entry

    return stats


def _safe(value):
    """Convert numpy scalars to Python native types."""
    try:
        return float(value) if value == value else None  # noqa: PLR0124 – NaN check
    except (TypeError, ValueError):
        return str(value)
