import numpy as np
import pandas as pd
import pytest

from app.services.forecasting import forecast_all, forecast_metric


def _trending_df(days=20, start=100, daily_increase=10):
    dates = pd.date_range("2024-01-01", periods=days)
    return pd.DataFrame(
        {
            "date": dates,
            "revenue": [start + i * daily_increase for i in range(days)],
            "conversions": [5 + i for i in range(days)],
        }
    )


def test_forecast_continues_an_upward_trend_instead_of_flattening():
    """The old RandomForest-based forecaster plateaued at the max training
    value for a steadily-climbing metric - a real correctness bug for a
    'predict the future' feature. Holt's trend method must not do that."""
    df = _trending_df()
    forecast = forecast_metric(df, "revenue", days_ahead=5)

    assert len(forecast) == 5
    values = [p["predicted_value"] for p in forecast]
    last_actual = df["revenue"].iloc[-1]

    # Forecast should keep climbing, not flatten at/near the last actual value.
    assert values[0] > last_actual
    assert values[-1] > values[0]


def test_forecast_confidence_bounds_widen_with_horizon():
    df = _trending_df()
    forecast = forecast_metric(df, "revenue", days_ahead=5)

    widths = [p["upper_bound"] - p["lower_bound"] for p in forecast]
    assert widths[-1] >= widths[0]


def test_forecast_never_predicts_negative_values():
    dates = pd.date_range("2024-01-01", periods=10)
    df = pd.DataFrame({"date": dates, "revenue": [10, 8, 6, 4, 2, 1, 0, 0, 0, 0]})
    forecast = forecast_metric(df, "revenue", days_ahead=10)

    for point in forecast:
        assert point["predicted_value"] >= 0
        assert point["lower_bound"] >= 0


def test_forecast_handles_very_short_series_via_linear_fallback():
    dates = pd.date_range("2024-01-01", periods=3)
    df = pd.DataFrame({"date": dates, "revenue": [100, 110, 120]})
    forecast = forecast_metric(df, "revenue", days_ahead=3)

    assert len(forecast) == 3
    assert forecast[0]["predicted_value"] > 120


def test_forecast_all_skips_missing_columns():
    dates = pd.date_range("2024-01-01", periods=10)
    df = pd.DataFrame({"date": dates, "clicks": range(10)})
    result = forecast_all(df, days_ahead=5)
    assert result == {}


def test_forecast_all_includes_revenue_and_conversions_when_present():
    df = _trending_df()
    result = forecast_all(df, days_ahead=5)
    assert set(result.keys()) == {"revenue", "conversions"}
    assert len(result["revenue"]) == 5
