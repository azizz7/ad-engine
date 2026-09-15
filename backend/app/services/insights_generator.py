"""Insights Generator - Creates business-focused, plain-English insights."""
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """Generates interpretable, business-focused insights from analytics and ML results."""

    def __init__(self, df: pd.DataFrame, analytics: Dict, ml_models):
        self.df = df.copy()
        self.analytics = analytics
        self.ml_models = ml_models

    def generate_performance_insights(self) -> List[str]:
        insights = []
        overall = self.analytics.get("overall_metrics", {})

        if overall.get("roas"):
            roas = overall["roas"]
            if roas < 1.0:
                insights.append(
                    f"⚠️ Overall ROAS is {roas:.2f}x, indicating you're spending more than you're earning. "
                    "Consider pausing underperforming ads and reallocating budget to top performers."
                )
            elif roas < 2.0:
                insights.append(
                    f"📊 Overall ROAS is {roas:.2f}x. While positive, there's room for optimization. "
                    "Focus on scaling high-ROAS campaigns."
                )
            else:
                insights.append(
                    f"✅ Strong overall ROAS of {roas:.2f}x. Your campaigns are performing well. "
                    "Consider increasing budget allocation to maintain this performance."
                )

        if overall.get("cpa"):
            cpa = overall["cpa"]
            total_spend = overall.get("total_spend", 0)
            insights.append(
                f"💰 Your average Cost Per Acquisition is ${cpa:.2f}. "
                f"With a total spend of ${total_spend:,.0f}, you've acquired approximately "
                f"{int(total_spend / cpa) if cpa > 0 else 0} conversions."
            )

        ctr = overall.get("ctr", 0)
        if ctr < 1.0:
            insights.append(
                f"📉 Your overall CTR is {ctr:.2f}%, which is below industry average. "
                "Consider testing new ad creatives or targeting more relevant audiences."
            )
        elif ctr > 2.0:
            insights.append(
                f"📈 Excellent CTR of {ctr:.2f}%. Your ad messaging is resonating well with your audience."
            )

        return insights

    def generate_top_performer_insights(self) -> List[str]:
        insights = []
        best = self.analytics.get("best_performing", [])
        if not best:
            return insights

        top_ad = best[0]
        ad_name = top_ad.get("ad_name") or top_ad.get("campaign_name", "Unknown")

        if "metric_value" in top_ad:
            metric_value = top_ad["metric_value"]
            spend = top_ad.get("spend", 0)
            revenue = top_ad.get("revenue", 0)

            insights.append(
                f"🏆 Top performer: '{ad_name}' with ROAS of {metric_value:.2f}x. "
                f"Generated ${revenue:,.0f} in revenue from ${spend:,.0f} in spend. "
                "Consider increasing budget allocation to this ad."
            )

        if len(best) >= 3:
            top_3_avg_roas = sum(ad.get("metric_value", 0) for ad in best[:3]) / 3
            insights.append(
                f"📊 Your top 3 ads average {top_3_avg_roas:.2f}x ROAS. "
                "These represent your best opportunities for scaling."
            )

        return insights

    def generate_underperformer_insights(self) -> List[str]:
        insights = []
        worst = self.analytics.get("worst_performing", [])
        inefficiencies = self.analytics.get("spend_inefficiencies", [])

        if worst:
            worst_ad = worst[0]
            ad_name = worst_ad.get("ad_name") or worst_ad.get("campaign_name", "Unknown")
            spend = worst_ad.get("spend", 0)

            insights.append(
                f"⚠️ Underperformer alert: '{ad_name}' is spending ${spend:,.0f} with poor performance. "
                "Consider pausing this ad or significantly reducing its budget to test improvements."
            )

        if inefficiencies:
            total_waste = sum(ad.get("spend", 0) for ad in inefficiencies[:5])
            insights.append(
                f"💸 Found {len(inefficiencies)} ads with high spend but low ROAS. "
                f"These represent approximately ${total_waste:,.0f} in potentially inefficient spend. "
                "Review these campaigns for optimization opportunities."
            )

        return insights

    def generate_trend_insights(self) -> List[str]:
        insights = []
        trends_data = self.analytics.get("trends", {})
        trends = trends_data.get("trends", {})

        if "revenue" in trends:
            rev_trend = trends["revenue"]
            direction = rev_trend["direction"]
            strength = rev_trend["strength"]

            if direction == "increasing" and strength == "strong":
                insights.append(
                    "📈 Strong upward trend detected in revenue. Your campaigns are gaining momentum. "
                    "Consider maintaining or increasing investment."
                )
            elif direction == "decreasing" and strength == "strong":
                insights.append(
                    "📉 Declining revenue trend detected. Investigate recent changes in ad performance "
                    "or market conditions. Consider pausing underperformers."
                )

        if "spend" in trends:
            spend_trend = trends["spend"]
            if spend_trend["direction"] == "increasing":
                insights.append(
                    "💰 Spend is trending upward. Monitor ROAS closely to ensure efficiency is maintained."
                )

        try:
            ml_trends = self.ml_models.detect_trends()
        except Exception:
            logger.exception("ML trend detection failed while generating insights")
            ml_trends = {}

        if "revenue" in ml_trends:
            pct_change = ml_trends["revenue"].get("pct_change", 0)
            if abs(pct_change) > 10:
                if pct_change > 0:
                    insights.append(
                        f"📊 Revenue has increased by {pct_change:.1f}% over the analyzed period. "
                        "This indicates strong campaign performance."
                    )
                else:
                    insights.append(
                        f"📊 Revenue has decreased by {abs(pct_change):.1f}% over the analyzed period. "
                        "Review recent campaign changes and market factors."
                    )

        return insights

    def generate_predictive_insights(self) -> List[str]:
        insights = []

        try:
            predictions = self.ml_models.predict_future(days_ahead=7)

            if "revenue" in predictions:
                pred_data = predictions["revenue"]
                if pred_data:
                    avg_predicted = sum(p["predicted_value"] for p in pred_data) / len(pred_data)
                    current_avg = self.df["revenue"].mean() if "revenue" in self.df.columns else 0

                    if current_avg > 0:
                        change_pct = ((avg_predicted - current_avg) / current_avg) * 100

                        if change_pct > 5:
                            insights.append(
                                f"🔮 Predictive model forecasts a {change_pct:.1f}% increase in revenue "
                                "over the next 7 days. Consider maintaining current strategy."
                            )
                        elif change_pct < -5:
                            insights.append(
                                f"🔮 Predictive model forecasts a {abs(change_pct):.1f}% decrease in revenue "
                                "over the next 7 days. Review and optimize campaigns proactively."
                            )

            if "conversions" in predictions:
                pred_data = predictions["conversions"]
                if pred_data:
                    total_predicted = sum(p["predicted_value"] for p in pred_data)
                    insights.append(
                        f"🎯 Model predicts approximately {int(total_predicted)} conversions "
                        "over the next 7 days based on current trends."
                    )

        except Exception:
            logger.exception("Predictive insight generation failed")

        return insights

    def generate_budget_insights(self) -> List[str]:
        insights = []
        overall = self.analytics.get("overall_metrics", {})
        best = self.analytics.get("best_performing", [])
        worst = self.analytics.get("worst_performing", [])

        total_spend = overall.get("total_spend", 0)

        if best and worst and total_spend > 0:
            best_spend = sum(ad.get("spend", 0) for ad in best[:3])
            worst_spend = sum(ad.get("spend", 0) for ad in worst[:3])

            best_pct = (best_spend / total_spend) * 100
            worst_pct = (worst_spend / total_spend) * 100

            if worst_pct > 20:
                insights.append(
                    f"💡 {worst_pct:.1f}% of spend is allocated to underperforming ads. "
                    "Reallocating even 50% of this budget to top performers could significantly "
                    "improve overall ROAS."
                )

            if best_pct < 30:
                insights.append(
                    f"💡 Only {best_pct:.1f}% of spend is on top performers. "
                    "Consider shifting budget from underperformers to scale successful campaigns."
                )

        return insights

    def generate_all_insights(self) -> Dict[str, Any]:
        all_insights = []
        all_insights.extend(self.generate_performance_insights())
        all_insights.extend(self.generate_top_performer_insights())
        all_insights.extend(self.generate_underperformer_insights())
        all_insights.extend(self.generate_trend_insights())
        all_insights.extend(self.generate_predictive_insights())
        all_insights.extend(self.generate_budget_insights())

        priority_keywords = ["⚠️", "💸", "🔮"]
        prioritized = [i for i in all_insights if any(k in i for k in priority_keywords)]
        regular = [i for i in all_insights if i not in prioritized]

        return {
            "insights": prioritized + regular,
            "count": len(all_insights),
            "priority_count": len(prioritized),
            "generated_at": datetime.now().isoformat(),
        }
