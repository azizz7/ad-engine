import pandas as pd
import pytest

from app.services.analytics_engine import AnalyticsEngine


def test_compute_all_metrics_happy_path(sample_df):
    engine = AnalyticsEngine(sample_df)
    metrics = engine.compute_all_metrics()

    overall = metrics["overall_metrics"]
    assert overall["total_spend"] == pytest.approx(sample_df["spend"].sum())
    assert overall["total_impressions"] == pytest.approx(sample_df["impressions"].sum())
    assert overall["ctr"] > 0
    assert overall["roas"] is not None
    assert overall["cpa"] is not None

    assert len(metrics["platform_metrics"]) == 2
    assert metrics["best_performing"]
    assert metrics["worst_performing"]


def test_missing_optional_columns_does_not_crash():
    """revenue/conversions are optional per the documented CSV format;
    metrics that depend on them should be None, not raise."""
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=5),
            "impressions": [1000, 1200, 900, 1100, 1300],
            "clicks": [10, 12, 9, 11, 13],
            "spend": [50.0, 60.0, 45.0, 55.0, 65.0],
        }
    )

    engine = AnalyticsEngine(df)
    metrics = engine.compute_all_metrics()
    overall = metrics["overall_metrics"]

    assert overall["roas"] is None
    assert overall["cpa"] is None
    assert overall["total_revenue"] is None
    assert overall["total_conversions"] is None
    assert overall["ctr"] > 0
    # Must not raise even though there's no ad_name/campaign_name column.
    assert metrics["best_performing"] == []


def test_zero_impressions_does_not_divide_by_zero():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3),
            "impressions": [0, 0, 0],
            "clicks": [0, 0, 0],
            "spend": [0.0, 0.0, 0.0],
        }
    )

    engine = AnalyticsEngine(df)
    metrics = engine.compute_all_metrics()

    assert metrics["overall_metrics"]["ctr"] == 0.0
    assert metrics["overall_metrics"]["cpc"] == 0.0


def test_get_best_performing_ads_ranks_by_roas(sample_df):
    engine = AnalyticsEngine(sample_df)
    best = engine.get_best_performing_ads(limit=3)

    assert len(best) == 3
    values = [ad["metric_value"] for ad in best]
    assert values == sorted(values, reverse=True)
