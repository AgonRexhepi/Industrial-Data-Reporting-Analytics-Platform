"""
Data profiling utilities.

Analyses a pandas DataFrame to detect column types, compute statistics,
and calculate a data-quality score.
"""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

from apps.datasets.models import DatasetColumn, DatasetQuality, DatasetVersion

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def _detect_logical_type(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return DatasetColumn.LogicalType.BOOLEAN
    if pd.api.types.is_integer_dtype(series):
        return DatasetColumn.LogicalType.INTEGER
    if pd.api.types.is_float_dtype(series):
        return DatasetColumn.LogicalType.DECIMAL
    if pd.api.types.is_datetime64_any_dtype(series):
        return DatasetColumn.LogicalType.DATETIME

    # Try casting object columns
    sample = series.dropna().astype(str)
    if sample.empty:
        return DatasetColumn.LogicalType.UNKNOWN

    # Try email
    if sample.str.match(EMAIL_RE).mean() > 0.8:
        return DatasetColumn.LogicalType.EMAIL

    # Try URL
    if sample.str.match(URL_RE).mean() > 0.8:
        return DatasetColumn.LogicalType.URL

    # Try datetime parse
    try:
        pd.to_datetime(sample.head(50), format="mixed", errors="raise")
        return DatasetColumn.LogicalType.DATETIME
    except Exception:
        pass

    # Try numeric
    numeric = pd.to_numeric(sample.head(100), errors="coerce")
    if numeric.notna().mean() > 0.9:
        if (numeric % 1 == 0).all():
            return DatasetColumn.LogicalType.INTEGER
        return DatasetColumn.LogicalType.DECIMAL

    # Low-cardinality → category
    if series.nunique() / max(len(series), 1) < 0.05 and series.nunique() <= 50:
        return DatasetColumn.LogicalType.CATEGORY

    return DatasetColumn.LogicalType.STRING


def profile_dataframe(df: pd.DataFrame, version: DatasetVersion) -> None:
    """
    Detect column types, compute per-column statistics, and calculate
    data-quality metrics for the given DatasetVersion.
    """
    columns_to_create: list[DatasetColumn] = []
    for position, col_name in enumerate(df.columns):
        series = df[col_name]
        logical_type = _detect_logical_type(series)

        null_count = int(series.isna().sum())
        unique_count = int(series.nunique(dropna=True))

        min_val: Any = None
        max_val: Any = None
        mean_val: float | None = None

        try:
            min_val = str(series.min()) if not series.dropna().empty else None
            max_val = str(series.max()) if not series.dropna().empty else None
        except Exception:
            pass

        if logical_type in (DatasetColumn.LogicalType.INTEGER, DatasetColumn.LogicalType.DECIMAL):
            numeric = pd.to_numeric(series, errors="coerce")
            if numeric.notna().any():
                mean_val = float(numeric.mean())

        sample_values = series.dropna().astype(str).head(5).tolist()

        columns_to_create.append(
            DatasetColumn(
                dataset_version=version,
                name=col_name,
                original_name=col_name,
                logical_type=logical_type,
                position=position,
                null_count=null_count,
                unique_count=unique_count,
                min_value=min_val,
                max_value=max_val,
                mean_value=mean_val,
                sample_values=sample_values,
            )
        )

    DatasetColumn.objects.bulk_create(columns_to_create)

    total_rows = len(df)
    total_columns = len(df.columns)
    total_cells = total_rows * total_columns
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0.0
    dup_pct = (duplicate_rows / total_rows * 100) if total_rows > 0 else 0.0
    quality_score = max(0.0, 100.0 - missing_pct - dup_pct)

    DatasetQuality.objects.create(
        dataset_version=version,
        total_rows=total_rows,
        total_columns=total_columns,
        missing_cells=missing_cells,
        missing_percentage=round(missing_pct, 2),
        duplicate_rows=duplicate_rows,
        quality_score=round(quality_score, 2),
    )
