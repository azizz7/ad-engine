"""
Shared helpers for turning pandas/numpy values into JSON-safe primitives.

Used by both the persistence layer (before storing raw rows as JSON) and
the API layer (before returning DataFrame-derived data as a response), so
the NaN/Timestamp/numpy-scalar handling only lives in one place.
"""
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def to_json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) or np.isinf(value) else float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        # NaN/inf (NaN != NaN is the classic float check)
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def dataframe_records_to_json_safe(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{key: to_json_safe(value) for key, value in record.items()} for record in records]
