import json
import pandas as pd
from sqlalchemy.orm import Session
from models import Dataset, DatasetData, AnalyticsCache, InsightsCache
from typing import Dict, List, Any, Optional

def create_dataset(
    db: Session,
    name: str,
    filename: str,
    df: pd.DataFrame,
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None
) -> int:
    """Create a new dataset and store its data"""
    # Create dataset record
    db_dataset = Dataset(
        name=name,
        filename=filename,
        row_count=len(df),
        columns=list(df.columns),
        date_range_start=date_range_start,
        date_range_end=date_range_end
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    
    # Store raw data
    data_records = df.to_dict('records')
    # Convert timestamps to string for JSON serialization
    serialized_data = []
    for record in data_records:
        serialized_record = {}
        for key, value in record.items():
            if pd.isna(value):
                serialized_record[key] = None
            elif isinstance(value, pd.Timestamp):
                serialized_record[key] = value.isoformat()
            else:
                serialized_record[key] = value
        serialized_data.append(serialized_record)
        
    db_data = DatasetData(
        dataset_id=db_dataset.id,
        data_json=serialized_data
    )
    db.add(db_data)
    db.commit()
    
    return db_dataset.id

def get_dataset(db: Session, dataset_id: int):
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()

def list_datasets(db: Session):
    return db.query(Dataset).order_by(Dataset.created_at.desc()).all()

def get_dataset_data(db: Session, dataset_id: int) -> Optional[pd.DataFrame]:
    """Get dataset raw data as DataFrame"""
    data_record = db.query(DatasetData).filter(DatasetData.dataset_id == dataset_id).first()
    
    if not data_record:
        return None
    
    df = pd.DataFrame(data_record.data_json)
    
    # Convert date column back to datetime if it exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    return df

def save_analytics(db: Session, dataset_id: int, analytics: Dict[str, Any]):
    # Check if exists
    existing = db.query(AnalyticsCache).filter(AnalyticsCache.dataset_id == dataset_id).first()
    if existing:
        existing.analytics_json = analytics
        existing.updated_at = pd.Timestamp.now()
    else:
        db_analytics = AnalyticsCache(dataset_id=dataset_id, analytics_json=analytics)
        db.add(db_analytics)
    db.commit()

def get_analytics(db: Session, dataset_id: int):
    record = db.query(AnalyticsCache).filter(AnalyticsCache.dataset_id == dataset_id).first()
    return record.analytics_json if record else None

def save_insights(db: Session, dataset_id: int, insights: Dict[str, Any]):
    existing = db.query(InsightsCache).filter(InsightsCache.dataset_id == dataset_id).first()
    if existing:
        existing.insights_json = insights
        existing.updated_at = pd.Timestamp.now()
    else:
        db_insights = InsightsCache(dataset_id=dataset_id, insights_json=insights)
        db.add(db_insights)
    db.commit()

def get_insights(db: Session, dataset_id: int):
    record = db.query(InsightsCache).filter(InsightsCache.dataset_id == dataset_id).first()
    return record.insights_json if record else None

def delete_dataset(db: Session, dataset_id: int) -> bool:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset:
        db.delete(dataset)
        db.commit()
        return True
    return False
