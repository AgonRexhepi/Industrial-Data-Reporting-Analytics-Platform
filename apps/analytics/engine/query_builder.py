"""Top-level query builder that orchestrates the analytics engine pipeline."""
from __future__ import annotations

import pandas as pd

from .filtering import apply_filters
from .grouping import apply_groupby
from .time_series import apply_date_grouping
from .validators import validate_sort_direction


def run_query(df: pd.DataFrame, query: dict) -> dict:
    """Execute an analytics query on *df* and return a serialisable result dict.

    *query* schema::

        {
            "dimensions": ["col_a"],          # optional
            "measures": [                     # optional
                {"column": "col_b", "aggregation": "sum"}
            ],
            "filters": [                      # optional
                {"column": "col_a", "operator": "=", "value": "x"}
            ],
            "date_groupings": [               # optional
                {"column": "date_col", "grouping": "month"}
            ],
            "sort": {                         # optional
                "column": "col_b__sum",
                "direction": "desc"
            },
            "limit": 100                      # optional, default 1000
        }
    """
    # 1. Filters
    filters = query.get("filters") or []
    if filters:
        df = apply_filters(df, filters)

    # 2. Date groupings
    for dg in query.get("date_groupings") or []:
        df = apply_date_grouping(df, dg["column"], dg["grouping"])

    # 3. Group + aggregate
    dimensions = query.get("dimensions") or []
    measures = query.get("measures") or []
    if dimensions or measures:
        df = apply_groupby(df, dimensions, measures)

    # 4. Sort
    sort = query.get("sort")
    if sort and sort.get("column") and sort["column"] in df.columns:
        direction = validate_sort_direction(sort.get("direction", "asc"))
        df = df.sort_values(sort["column"], ascending=(direction == "asc"))

    # 5. Limit
    limit = int(query.get("limit") or 1000)
    df = df.head(limit)

    columns = df.columns.tolist()
    rows = df.where(pd.notnull(df), None).values.tolist()

    return {"columns": columns, "rows": rows, "row_count": len(rows)}
