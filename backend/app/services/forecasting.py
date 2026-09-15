"""
Time-series forecasting for daily ad performance metrics.

Why not the old RandomForest approach: tree-based models cannot extrapolate
beyond the range of values they were trained on. A metric climbing every
day would still get its forecast flattened at the highest value ever seen
in training - a real correctness bug for a "predict future performance"
feature, not just a modeling nuance.

Holt's linear trend method (double exponential smoothing) is fit directly
on daily-aggregated history, has an explicit trend component so it keeps
extrapolating instead of plateauing, is damped so it doesn't run away to
infinity over long horizons, and fits in milliseconds even on a few
hundred points - so there is no need to train-and-cache a model on disk
the way the old joblib-pickled RandomForest was. Everything here is
computed fresh, on demand, per request.
"""
import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import Holt

logger = logging.getLogger(__name__)

MIN_POINTS_FOR_HOLT = 5
CONFIDENCE_Z = 1.96  # ~95% interval under a normal-residual assumption


def _daily_series(df: pd.DataFrame, target: str) -> pd.Series:
    daily = df.groupby("date")[target].sum().sort_index()
    return daily


def _linear_trend_forecast(values: np.ndarray, days_ahead: int) -> np.ndarray:
    """Fallback for series too short to fit Holt: extend the least-squares line."""
    x = np.arange(len(values))
    slope, intercept = np.polyfit(x, values, 1)
    future_x = np.arange(len(values), len(values) + days_ahead)
    return slope * future_x + intercept


def forecast_metric(df: pd.DataFrame, target: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
    """Forecast a single daily metric (e.g. 'revenue', 'conversions') forward."""
    if target not in df.columns:
        return []

    series = _daily_series(df, target)
    values = series.values.astype(float)
    last_date = series.index.max()

    if len(values) < 2:
        return []

    if len(values) < MIN_POINTS_FOR_HOLT:
        point_forecast = _linear_trend_forecast(values, days_ahead)
        residual_std = float(np.std(values)) if len(values) > 1 else 0.0
    else:
        try:
            model = Holt(values, damped_trend=True, initialization_method="estimated").fit()
            point_forecast = model.forecast(days_ahead)
            residual_std = float(np.std(model.resid))
        except Exception:
            logger.exception("Holt forecasting failed for target=%s; falling back to linear trend", target)
            point_forecast = _linear_trend_forecast(values, days_ahead)
            residual_std = float(np.std(values))

    predictions = []
    for i, value in enumerate(point_forecast, start=1):
        # Uncertainty naturally widens with the forecast horizon.
        margin = CONFIDENCE_Z * residual_std * np.sqrt(i)
        point = max(0.0, float(value))
        predictions.append(
            {
                "date": (last_date + pd.Timedelta(days=i)).isoformat(),
                "predicted_value": round(point, 2),
                "lower_bound": round(max(0.0, point - margin), 2),
                "upper_bound": round(point + margin, 2),
            }
        )

    return predictions


def forecast_all(df: pd.DataFrame, days_ahead: int = 7) -> Dict[str, List[Dict[str, Any]]]:
    """Forecast every metric we have a documented use case for."""
    predictions: Dict[str, List[Dict[str, Any]]] = {}

    for target in ("revenue", "conversions"):
        if target in df.columns:
            forecast = forecast_metric(df, target, days_ahead)
            if forecast:
                predictions[target] = forecast

    return predictions
