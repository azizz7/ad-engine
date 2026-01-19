from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database_config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    filename = Column(String)
    row_count = Column(Integer)
    columns = Column(JSON)
    date_range_start = Column(String)
    date_range_end = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    data_records = relationship("DatasetData", back_populates="dataset", cascade="all, delete-orphan")
    analytics = relationship("AnalyticsCache", back_populates="dataset", uselist=False, cascade="all, delete-orphan")
    insights = relationship("InsightsCache", back_populates="dataset", uselist=False, cascade="all, delete-orphan")

class DatasetData(Base):
    __tablename__ = "dataset_data"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    data_json = Column(JSON)
    
    dataset = relationship("Dataset", back_populates="data_records")

class AnalyticsCache(Base):
    __tablename__ = "analytics_cache"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), unique=True)
    analytics_json = Column(JSON)
    updated_at = Column(DateTime, default=datetime.now)
    
    dataset = relationship("Dataset", back_populates="analytics")

class InsightsCache(Base):
    __tablename__ = "insights_cache"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), unique=True)
    insights_json = Column(JSON)
    updated_at = Column(DateTime, default=datetime.now)
    
    dataset = relationship("Dataset", back_populates="insights")
