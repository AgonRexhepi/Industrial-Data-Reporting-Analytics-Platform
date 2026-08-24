"""Grouping helpers for the analytics engine."""
from __future__ import annotations

import pandas as pd


def apply_groupby(df: pd.DataFrame, dimensions: list[str], measures: list[dict]) -> pd.DataFrame:
    """Group *df* by *dimensions* and aggregate each measure."""
    if not dimensions and not measures:
        return df

    agg_map: dict[str, list] = {}
    for m in measures:
        col = m["column"]
        agg = m["aggregation"].lower()
        pandas_agg = _to_pandas_agg(agg)
        if pandas_agg:
            agg_map.setdefault(col, []).append(pandas_agg)

    if not dimensions:
        # No grouping — aggregate the whole dataset
        rows = {}
        for col, aggs in agg_map.items():
            for pandas_agg in aggs:
                key = f"{col}__{pandas_agg}"
                rows[key] = getattr(df[col], pandas_agg)() if hasattr(df[col], pandas_agg) else df[col].agg(pandas_agg)
        return pd.DataFrame([rows])

    grouped = df.groupby(dimensions)
    result_parts = []
    for col, aggs in agg_map.items():
        part = grouped[col].agg(aggs)
        if isinstance(part, pd.Series):
            part = part.to_frame()
        part.columns = [f"{col}__{a}" for a in aggs]
        result_parts.append(part)

    if result_parts:
        result = pd.concat(result_parts, axis=1).reset_index()
    else:
        result = df[dimensions].drop_duplicates().reset_index(drop=True)

    return result


def _to_pandas_agg(agg: str) -> str | None:
    mapping = {
        "count": "count",
        "sum": "sum",
        "avg": "mean",
        "min": "min",
        "max": "max",
        "median": "median",
        "std": "std",
        "distinct_count": "nunique",
    }
    return mapping.get(agg)
