"""Statistical trend detection and ad clustering.

Forecasting (predicting future revenue/conversions) lives in
`forecasting.py` instead of here - it's a time-series problem, not a
tabular regression problem, and doesn't need a persisted/trained model
object the way this class's name might suggest.
"""
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.services.forecasting import forecast_all


class MLModels:
    """Trend detection, clustering, and forecasting for one dataset."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df["date"] = pd.to_datetime(self.df["date"])

        numeric_cols = ["impressions", "clicks", "spend", "conversions", "revenue"]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(0)

    def predict_future(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Forecast revenue/conversions forward. See `forecasting.forecast_all`."""
        return forecast_all(self.df, days_ahead=days_ahead)

    def detect_trends(self) -> Dict[str, Any]:
        """Detect performance trends using simple linear-regression slope/R²."""
        agg = {"spend": "sum", "clicks": "sum"}
        if "revenue" in self.df.columns:
            agg["revenue"] = "sum"
        if "conversions" in self.df.columns:
            agg["conversions"] = "sum"

        daily = self.df.groupby("date").agg(agg).reset_index()

        trends = {}
        for metric in ["spend", "revenue", "conversions", "clicks"]:
            if metric in daily.columns:
                values = daily[metric].values
                if len(values) >= 7:
                    x = np.arange(len(values))
                    slope, intercept = np.polyfit(x, values, 1)

                    y_pred = slope * x + intercept
                    ss_res = np.sum((values - y_pred) ** 2)
                    ss_tot = np.sum((values - np.mean(values)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

                    pct_change = ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0

                    trends[metric] = {
                        "slope": float(slope),
                        "direction": "increasing" if slope > 0 else "decreasing",
                        "r_squared": float(r_squared),
                        "pct_change": float(pct_change),
                        "strength": "strong" if abs(r_squared) > 0.5 else "weak",
                    }

        return trends

    def cluster_ads(self, n_clusters: int = 3) -> Dict[str, Any]:
        """Cluster ads by performance behavior."""
        if "ad_name" in self.df.columns:
            group_col = "ad_name"
        elif "campaign_name" in self.df.columns:
            group_col = "campaign_name"
        else:
            return {"error": "No ad_name or campaign_name column found"}

        agg = {"spend": "sum", "clicks": "sum", "impressions": "sum"}
        if "revenue" in self.df.columns:
            agg["revenue"] = "sum"
        if "conversions" in self.df.columns:
            agg["conversions"] = "sum"

        ad_data = self.df.groupby(group_col).agg(agg).reset_index()

        ad_data["ctr"] = ad_data.apply(
            lambda x: (x["clicks"] / x["impressions"] * 100) if x["impressions"] > 0 else 0, axis=1
        )

        if "revenue" in ad_data.columns:
            ad_data["roas"] = ad_data.apply(
                lambda x: x["revenue"] / x["spend"] if x["spend"] > 0 else 0, axis=1
            )

        feature_cols = ["spend", "ctr"]
        if "roas" in ad_data.columns:
            feature_cols.append("roas")
        if "conversions" in ad_data.columns:
            feature_cols.append("conversions")

        if len(ad_data) < n_clusters:
            return {"error": f"Not enough ads to cluster into {n_clusters} groups"}

        X = ad_data[feature_cols].values
        X_scaled = StandardScaler().fit_transform(X)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        ad_data["cluster"] = kmeans.fit_predict(X_scaled)

        cluster_summary = []
        for cluster_id in range(n_clusters):
            cluster_ads = ad_data[ad_data["cluster"] == cluster_id]
            cluster_summary.append(
                {
                    "cluster_id": int(cluster_id),
                    "ad_count": len(cluster_ads),
                    "avg_spend": float(cluster_ads["spend"].mean()),
                    "avg_ctr": float(cluster_ads["ctr"].mean()),
                    "avg_roas": float(cluster_ads["roas"].mean()) if "roas" in cluster_ads.columns else None,
                    "ads": cluster_ads[group_col].tolist(),
                }
            )

        return {
            "n_clusters": n_clusters,
            "clusters": cluster_summary,
            "ad_clusters": ad_data[[group_col, "cluster"]].to_dict("records"),
        }
