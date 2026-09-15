from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, index=True)
    filename = Column(String)
    row_count = Column(Integer)
    columns = Column(JSON)
    date_range_start = Column(String)
    date_range_end = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="datasets")
    data_records = relationship(
        "DatasetData", back_populates="dataset", cascade="all, delete-orphan"
    )
    analytics = relationship(
        "AnalyticsCache", back_populates="dataset", uselist=False, cascade="all, delete-orphan"
    )
    insights = relationship(
        "InsightsCache", back_populates="dataset", uselist=False, cascade="all, delete-orphan"
    )


class DatasetData(Base):
    __tablename__ = "dataset_data"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True, nullable=False)
    data_json = Column(JSON)

    dataset = relationship("Dataset", back_populates="data_records")


class AnalyticsCache(Base):
    __tablename__ = "analytics_cache"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), unique=True, nullable=False)
    analytics_json = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="analytics")


class InsightsCache(Base):
    __tablename__ = "insights_cache"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), unique=True, nullable=False)
    insights_json = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="insights")
