from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DateRange(BaseModel):
    start: str | None = None
    end: str | None = None


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    filename: str
    row_count: int
    columns: list[str]
    date_range_start: str | None = None
    date_range_end: str | None = None
    created_at: datetime
    updated_at: datetime


class UploadResponse(BaseModel):
    message: str
    dataset_id: int
    name: str
    rows: int
    columns: list[str]
    date_range: DateRange
    warnings: list[str] = []


class SyncResponse(BaseModel):
    status: str
    dataset_id: int | None = None
    rows: int
    message: str
