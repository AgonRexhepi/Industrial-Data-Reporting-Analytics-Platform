"""Time series / date grouping helpers for the analytics engine."""
from __future__ import annotations

import pandas as pd

from .validators import ALLOWED_DATE_GROUPINGS, ValidationError


FREQ_MAP = {
    "year": "YE",
    "quarter": "QE",
    "month": "ME",
    "week": "W",
    "day": "D",
    "hour": "h",
}


def apply_date_grouping(df: pd.DataFrame, column: str, grouping: str) -> pd.DataFrame:
    """Add a derived column ``<column>__<grouping>`` for time-based bucketing."""
    if grouping not in ALLOWED_DATE_GROUPINGS:
        raise ValidationError(f"Invalid date grouping '{grouping}'. Allowed: {sorted(ALLOWED_DATE_GROUPINGS)}")

    if column not in df.columns:
        raise ValidationError(f"Column '{column}' not found.")

    dt = pd.to_datetime(df[column], errors="coerce")

    if grouping == "year":
        df[f"{column}__year"] = dt.dt.year
    elif grouping == "quarter":
        df[f"{column}__quarter"] = dt.dt.to_period("Q").astype(str)
    elif grouping == "month":
        df[f"{column}__month"] = dt.dt.to_period("M").astype(str)
    elif grouping == "week":
        df[f"{column}__week"] = dt.dt.isocalendar().week.astype(int)
    elif grouping == "day":
        df[f"{column}__day"] = dt.dt.date.astype(str)
    elif grouping == "hour":
        df[f"{column}__hour"] = dt.dt.floor("h").astype(str)

    return df
