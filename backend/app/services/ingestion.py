"""
Shared dataset ingestion pipeline.

Both the CSV upload endpoint and the integration-sync endpoints funnel
through `ingest_dataframe` so dataset creation, analytics, and insight
generation only have one implementation to maintain.

Forecasting is computed on demand (see `forecasting.py`) rather than
trained and pickled here - it's cheap enough to skip the disk-cache
entirely, which also removes a class of stale-cache and unpickling risks
the old joblib-based approach carried.
"""
import logging
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.db import crud
from app.services.ai_narrative import generate_ai_summary
from app.services.analytics_engine import AnalyticsEngine
from app.services.insights_generator import InsightsGenerator
from app.services.ml_models import MLModels

logger = logging.getLogger(__name__)


class IngestionResult:
    def __init__(self, dataset_id: int, rows: int, columns: List[str], warnings: List[str]):
        self.dataset_id = dataset_id
        self.rows = rows
        self.columns = columns
        self.warnings = warnings


def ingest_dataframe(
    db: Session,
    user_id: int,
    df: pd.DataFrame,
    name: str,
    filename: str,
) -> IngestionResult:
    """
    Persist a dataframe as a new dataset, then compute and cache analytics
    and insights for it.

    Analytics/insights failures do not fail the whole ingestion (the
    dataset itself is still usable), but are reported back as `warnings`
    instead of being silently swallowed.
    """
    warnings: List[str] = []
    date_range_start = df["date"].min().isoformat()
    date_range_end = df["date"].max().isoformat()

    dataset_id = crud.create_dataset(
        db=db,
        user_id=user_id,
        name=name,
        filename=filename,
        df=df,
        date_range_start=date_range_start,
        date_range_end=date_range_end,
    )

    analytics = None
    try:
        analytics = AnalyticsEngine(df).compute_all_metrics()
        crud.save_analytics(db, dataset_id, analytics)
    except Exception:
        logger.exception("Analytics computation failed for dataset %s", dataset_id)
        warnings.append("Analytics could not be computed for this dataset.")

    if analytics is not None:
        try:
            ml_models = MLModels(df)
            insights = InsightsGenerator(df, analytics, ml_models).generate_all_insights()

            # Optional: one LLM call per dataset (never per page view) to add
            # a short executive summary on top of the rule-based insights.
            # `None` (unconfigured or failed) is a normal, expected outcome.
            insights["ai_summary"] = generate_ai_summary(
                analytics.get("overall_metrics", {}), insights.get("insights", [])
            )

            crud.save_insights(db, dataset_id, insights)
        except Exception:
            logger.exception("Insight generation failed for dataset %s", dataset_id)
            warnings.append("Insights could not be generated for this dataset.")
    else:
        warnings.append("Insights were skipped because analytics failed.")

    return IngestionResult(
        dataset_id=dataset_id,
        rows=len(df),
        columns=list(df.columns),
        warnings=warnings,
    )
