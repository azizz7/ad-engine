import io
import logging

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.dataset import DatasetRead, DateRange, UploadResponse
from app.services.forecasting import forecast_all
from app.services.ingestion import ingest_dataframe
from app.services.serialization import dataframe_records_to_json_safe

router = APIRouter(prefix="/api", tags=["datasets"])
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["date", "impressions", "clicks", "spend"]


def _resolve_dataset_id(db: Session, user_id: int, dataset_id: int | None) -> int:
    """Resolve an optional dataset_id query param to a concrete one, defaulting
    to the user's most recently created dataset."""
    if dataset_id is not None:
        return dataset_id

    datasets = crud.list_datasets(db, user_id)
    if not datasets:
        raise HTTPException(status_code=404, detail="No datasets found")
    return datasets[0].id


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and process a CSV file of ad performance data."""
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV file: {exc}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing)}. "
            f"Required: {', '.join(REQUIRED_COLUMNS)}.",
        )

    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Could not parse 'date' column as dates: {exc}"
        ) from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV contains no rows")

    dataset_name = name or f"{file.filename} - {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"

    result = ingest_dataframe(
        db=db,
        user_id=current_user.id,
        df=df,
        name=dataset_name,
        filename=file.filename,
    )

    return UploadResponse(
        message="File uploaded successfully",
        dataset_id=result.dataset_id,
        name=dataset_name,
        rows=result.rows,
        columns=result.columns,
        date_range=DateRange(
            start=df["date"].min().isoformat(), end=df["date"].max().isoformat()
        ),
        warnings=result.warnings,
    )


@router.get("/datasets", response_model=list[DatasetRead])
async def list_datasets(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return crud.list_datasets(db, current_user.id)


@router.get("/datasets/{dataset_id}", response_model=DatasetRead)
async def get_dataset_info(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = crud.get_dataset(db, current_user.id, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/datasets/{dataset_id}")
async def delete_dataset_endpoint(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = crud.delete_dataset(db, current_user.id, dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return {"message": "Dataset deleted successfully"}


@router.get("/analytics")
async def get_analytics_endpoint(
    dataset_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset_id = _resolve_dataset_id(db, current_user.id, dataset_id)
    analytics = crud.get_analytics(db, current_user.id, dataset_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Analytics not found for this dataset")
    return analytics


@router.get("/insights")
async def get_insights_endpoint(
    dataset_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset_id = _resolve_dataset_id(db, current_user.id, dataset_id)
    insights = crud.get_insights(db, current_user.id, dataset_id)
    if insights is None:
        raise HTTPException(status_code=404, detail="Insights not found for this dataset")
    return insights


@router.get("/predictions")
async def get_predictions(
    days_ahead: int = 7,
    dataset_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset_id = _resolve_dataset_id(db, current_user.id, dataset_id)

    df = crud.get_dataset_data(db, current_user.id, dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset data not found")

    return forecast_all(df, days_ahead=days_ahead)


@router.get("/data")
async def get_data(
    dataset_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get raw dataset rows (for charts)."""
    dataset_id = _resolve_dataset_id(db, current_user.id, dataset_id)

    df = crud.get_dataset_data(db, current_user.id, dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset data not found")

    return dataframe_records_to_json_safe(df.to_dict("records"))
