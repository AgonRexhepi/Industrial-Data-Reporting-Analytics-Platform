"""Filtering helpers for the analytics engine."""
from __future__ import annotations

import pandas as pd

from .validators import validate_filter_operator


def apply_filters(df: pd.DataFrame, filters: list[dict]) -> pd.DataFrame:
    """Apply a list of filter dicts to *df* and return the filtered DataFrame."""
    for f in filters:
        column = f["column"]
        operator = validate_filter_operator(f["operator"])
        value = f.get("value")

        if column not in df.columns:
            continue

        col = df[column]

        if operator == "=":
            df = df[col == value]
        elif operator == "!=":
            df = df[col != value]
        elif operator == ">":
            df = df[col > value]
        elif operator == ">=":
            df = df[col >= value]
        elif operator == "<":
            df = df[col < value]
        elif operator == "<=":
            df = df[col <= value]
        elif operator == "in":
            df = df[col.isin(value)]
        elif operator == "not_in":
            df = df[~col.isin(value)]
        elif operator == "contains":
            df = df[col.astype(str).str.contains(str(value), na=False, regex=False)]
        elif operator == "starts_with":
            df = df[col.astype(str).str.startswith(str(value), na=False)]
        elif operator == "ends_with":
            df = df[col.astype(str).str.endswith(str(value), na=False)]
        elif operator == "is_null":
            df = df[col.isna()]
        elif operator == "is_not_null":
            df = df[col.notna()]

    return df
