"""Analytics Engine - Computes key performance metrics from ad performance data."""
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from app.services.serialization import dataframe_records_to_json_safe


class AnalyticsEngine:
    """Computes business metrics from ad performance data."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.has_revenue = "revenue" in self.df.columns
        self.has_conversions = "conversions" in self.df.columns
        self._prepare_data()

    def _prepare_data(self):
        """Prepare and clean data for analysis.

        `revenue`/`conversions` are optional input columns. Rather than
        special-casing every aggregation below on whether they exist, we
        default them to 0 here and use `self.has_revenue`/`has_conversions`
        (captured before this runs) wherever "was this data actually
        provided" matters for the response shape.
        """
        numeric_cols = ["impressions", "clicks", "spend", "conversions", "revenue"]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(0)
            else:
                self.df[col] = 0.0

    def compute_ctr(self) -> float:
        """Compute overall Click-Through Rate"""
        total_clicks = self.df["clicks"].sum()
        total_impressions = self.df["impressions"].sum()
        if total_impressions == 0:
            return 0.0
        return (total_clicks / total_impressions) * 100

    def compute_cpc(self) -> float:
        """Compute overall Cost Per Click"""
        total_clicks = self.df["clicks"].sum()
        total_spend = self.df["spend"].sum()
        if total_clicks == 0:
            return 0.0
        return total_spend / total_clicks

    def compute_cpa(self):
        """Compute overall Cost Per Acquisition"""
        if not self.has_conversions:
            return None
        total_conversions = self.df["conversions"].sum()
        total_spend = self.df["spend"].sum()
        if total_conversions == 0:
            return None
        return total_spend / total_conversions

    def compute_roas(self):
        """Compute overall Return on Ad Spend"""
        if not self.has_revenue:
            return None
        total_revenue = self.df["revenue"].sum()
        total_spend = self.df["spend"].sum()
        if total_spend == 0:
            return None
        return total_revenue / total_spend

    def _group_col(self) -> str | None:
        if "ad_name" in self.df.columns:
            return "ad_name"
        if "campaign_name" in self.df.columns:
            return "campaign_name"
        return None

    def get_best_performing_ads(self, metric: str = "roas", limit: int = 5) -> List[Dict]:
        """Get top performing ads by specified metric"""
        group_col = self._group_col()
        if group_col is None:
            return []

        grouped = self.df.groupby(group_col).agg(
            {
                "spend": "sum",
                "revenue": "sum",
                "conversions": "sum",
                "clicks": "sum",
                "impressions": "sum",
            }
        ).reset_index()

        if metric == "roas" and self.has_revenue:
            grouped["metric_value"] = grouped.apply(
                lambda x: x["revenue"] / x["spend"] if x["spend"] > 0 else 0, axis=1
            )
        elif metric == "cpa" and self.has_conversions:
            grouped["metric_value"] = grouped.apply(
                lambda x: x["spend"] / x["conversions"] if x["conversions"] > 0 else float("inf"),
                axis=1,
            )
            grouped = grouped.sort_values("metric_value").head(limit)
            return dataframe_records_to_json_safe(grouped.to_dict("records"))
        elif metric == "ctr":
            grouped["metric_value"] = grouped.apply(
                lambda x: (x["clicks"] / x["impressions"] * 100) if x["impressions"] > 0 else 0,
                axis=1,
            )
        else:
            return []

        grouped = grouped.sort_values("metric_value", ascending=False).head(limit)
        return dataframe_records_to_json_safe(grouped.to_dict("records"))

    def get_worst_performing_ads(self, metric: str = "roas", limit: int = 5) -> List[Dict]:
        """Get worst performing ads by specified metric"""
        group_col = self._group_col()
        if group_col is None:
            return []

        grouped = self.df.groupby(group_col).agg(
            {
                "spend": "sum",
                "revenue": "sum",
                "conversions": "sum",
                "clicks": "sum",
                "impressions": "sum",
            }
        ).reset_index()

        if metric == "roas" and self.has_revenue:
            grouped["metric_value"] = grouped.apply(
                lambda x: x["revenue"] / x["spend"] if x["spend"] > 0 else 0, axis=1
            )
            grouped = grouped.sort_values("metric_value", ascending=True).head(limit)
        elif metric == "cpa" and self.has_conversions:
            grouped["metric_value"] = grouped.apply(
                lambda x: x["spend"] / x["conversions"] if x["conversions"] > 0 else float("inf"),
                axis=1,
            )
            grouped = grouped.sort_values("metric_value", ascending=False).head(limit)
        elif metric == "ctr":
            grouped["metric_value"] = grouped.apply(
                lambda x: (x["clicks"] / x["impressions"] * 100) if x["impressions"] > 0 else 0,
                axis=1,
            )
            grouped = grouped.sort_values("metric_value", ascending=True).head(limit)
        else:
            return []

        return dataframe_records_to_json_safe(grouped.to_dict("records"))

    def identify_spend_inefficiencies(self, threshold_roas: float = 1.0) -> List[Dict]:
        """Identify ads with high spend but low ROAS"""
        if not self.has_revenue:
            return []

        group_col = self._group_col()
        if group_col is None:
            return []

        grouped = self.df.groupby(group_col).agg({"spend": "sum", "revenue": "sum"}).reset_index()
        grouped["roas"] = grouped.apply(
            lambda x: x["revenue"] / x["spend"] if x["spend"] > 0 else 0, axis=1
        )

        inefficiencies = grouped[
            (grouped["spend"] > grouped["spend"].quantile(0.5)) & (grouped["roas"] < threshold_roas)
        ].sort_values("spend", ascending=False)

        return dataframe_records_to_json_safe(inefficiencies.to_dict("records"))

    def compute_trends(self) -> Dict[str, Any]:
        """Compute performance trends over time"""
        daily = self.df.groupby("date").agg(
            {
                "spend": "sum",
                "revenue": "sum",
                "conversions": "sum",
                "clicks": "sum",
                "impressions": "sum",
            }
        ).reset_index()

        daily["ctr"] = daily.apply(
            lambda x: (x["clicks"] / x["impressions"] * 100) if x["impressions"] > 0 else 0,
            axis=1,
        )

        if self.has_revenue:
            daily["roas"] = daily.apply(
                lambda x: x["revenue"] / x["spend"] if x["spend"] > 0 else 0, axis=1
            )

        optional_metrics = {"revenue": self.has_revenue, "conversions": self.has_conversions}
        trends = {}
        for metric in ["spend", "revenue", "conversions", "ctr", "roas"]:
            if not optional_metrics.get(metric, True):
                continue
            if metric in daily.columns:
                values = daily[metric].values
                if len(values) > 1:
                    x = np.arange(len(values))
                    slope = np.polyfit(x, values, 1)[0]
                    trends[metric] = {
                        "slope": float(slope),
                        "direction": "increasing" if slope > 0 else "decreasing",
                        "strength": "strong" if abs(slope) > np.std(values) else "weak",
                    }

        daily["date"] = daily["date"].dt.strftime("%Y-%m-%d")
        daily_data = dataframe_records_to_json_safe(daily.to_dict("records"))

        return {"daily_data": daily_data, "trends": trends}

    def compute_all_metrics(self) -> Dict[str, Any]:
        """Compute all analytics metrics"""
        cpa = self.compute_cpa()
        roas = self.compute_roas()

        overall = {
            "ctr": round(self.compute_ctr(), 2),
            "cpc": round(self.compute_cpc(), 2),
            "cpa": round(cpa, 2) if cpa is not None else None,
            "roas": round(roas, 2) if roas is not None else None,
            "total_spend": float(self.df["spend"].sum()),
            "total_impressions": float(self.df["impressions"].sum()),
            "total_clicks": float(self.df["clicks"].sum()),
            "total_revenue": float(self.df["revenue"].sum()) if self.has_revenue else None,
            "total_conversions": float(self.df["conversions"].sum())
            if self.has_conversions
            else None,
        }

        platform_metrics: List[Dict[str, Any]] = []
        if "platform" in self.df.columns:
            platform_grouped = self.df.groupby("platform").agg(
                {
                    "impressions": "sum",
                    "clicks": "sum",
                    "spend": "sum",
                    "conversions": "sum",
                    "revenue": "sum",
                }
            ).reset_index()

            for _, row in platform_grouped.iterrows():
                ctr = (row["clicks"] / row["impressions"] * 100) if row["impressions"] > 0 else 0.0
                cpc = (row["spend"] / row["clicks"]) if row["clicks"] > 0 else 0.0
                row_cpa = (
                    (row["spend"] / row["conversions"])
                    if self.has_conversions and row["conversions"] > 0
                    else None
                )
                row_roas = (
                    (row["revenue"] / row["spend"]) if self.has_revenue and row["spend"] > 0 else None
                )

                platform_metrics.append(
                    {
                        "platform": row["platform"],
                        "total_spend": float(row["spend"]),
                        "total_revenue": float(row["revenue"]) if self.has_revenue else None,
                        "total_conversions": float(row["conversions"]) if self.has_conversions else None,
                        "ctr": round(float(ctr), 2),
                        "cpc": round(float(cpc), 2),
                        "cpa": round(float(row_cpa), 2) if row_cpa is not None else None,
                        "roas": round(float(row_roas), 2) if row_roas is not None else None,
                    }
                )

        return {
            "overall_metrics": overall,
            "platform_metrics": platform_metrics,
            "best_performing": self.get_best_performing_ads(),
            "worst_performing": self.get_worst_performing_ads(),
            "spend_inefficiencies": self.identify_spend_inefficiencies(),
            "trends": self.compute_trends(),
        }
