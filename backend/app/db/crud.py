"""
Data access layer for datasets and their cached analytics/insights.

All dataset reads/writes are scoped to a `user_id` so one user can never
see or modify another user's uploaded data.
"""
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.dataset import AnalyticsCache, Dataset, DatasetData, InsightsCache
from app.services.serialization import dataframe_records_to_json_safe


def create_dataset(
    db: Session,
    user_id: int,
    name: str,
    filename: str,
    df: pd.DataFrame,
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None,
) -> int:
    """Create a new dataset and store its raw data."""
    db_dataset = Dataset(
        user_id=user_id,
        name=name,
        filename=filename,
        row_count=len(df),
        columns=list(df.columns),
        date_range_start=date_range_start,
        date_range_end=date_range_end,
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)

    serialized_data = dataframe_records_to_json_safe(df.to_dict("records"))
    db.add(DatasetData(dataset_id=db_dataset.id, data_json=serialized_data))
    db.commit()

    return db_dataset.id


def get_dataset(db: Session, user_id: int, dataset_id: int) -> Optional[Dataset]:
    return (
        db.query(Dataset)
        .filter(Dataset.id == dataset_id, Dataset.user_id == user_id)
        .first()
    )


def list_datasets(db: Session, user_id: int) -> List[Dataset]:
    return (
        db.query(Dataset)
        .filter(Dataset.user_id == user_id)
        .order_by(Dataset.created_at.desc())
        .all()
    )


def get_dataset_data(db: Session, user_id: int, dataset_id: int) -> Optional[pd.DataFrame]:
    """Get a dataset's raw rows as a DataFrame, scoped to the owning user."""
    dataset = get_dataset(db, user_id, dataset_id)
    if dataset is None:
        return None

    data_record = (
        db.query(DatasetData).filter(DatasetData.dataset_id == dataset_id).first()
    )
    if not data_record:
        return None

    df = pd.DataFrame(data_record.data_json)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df


def save_analytics(db: Session, dataset_id: int, analytics: Dict[str, Any]) -> None:
    existing = (
        db.query(AnalyticsCache).filter(AnalyticsCache.dataset_id == dataset_id).first()
    )
    if existing:
        existing.analytics_json = analytics
    else:
        db.add(AnalyticsCache(dataset_id=dataset_id, analytics_json=analytics))
    db.commit()


def get_analytics(db: Session, user_id: int, dataset_id: int) -> Optional[Dict[str, Any]]:
    dataset = get_dataset(db, user_id, dataset_id)
    if dataset is None:
        return None
    record = (
        db.query(AnalyticsCache).filter(AnalyticsCache.dataset_id == dataset_id).first()
    )
    return record.analytics_json if record else None


def save_insights(db: Session, dataset_id: int, insights: Dict[str, Any]) -> None:
    existing = (
        db.query(InsightsCache).filter(InsightsCache.dataset_id == dataset_id).first()
    )
    if existing:
        existing.insights_json = insights
    else:
        db.add(InsightsCache(dataset_id=dataset_id, insights_json=insights))
    db.commit()


def get_insights(db: Session, user_id: int, dataset_id: int) -> Optional[Dict[str, Any]]:
    dataset = get_dataset(db, user_id, dataset_id)
    if dataset is None:
        return None
    record = (
        db.query(InsightsCache).filter(InsightsCache.dataset_id == dataset_id).first()
    )
    return record.insights_json if record else None


def delete_dataset(db: Session, user_id: int, dataset_id: int) -> bool:
    dataset = get_dataset(db, user_id, dataset_id)
    if dataset is None:
        return False
    db.delete(dataset)
    db.commit()
    return True
