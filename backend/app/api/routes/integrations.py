from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dataset import SyncResponse
from app.services.ingestion import ingest_dataframe
from app.services.integrations.service import fetch_or_mock_facebook_data, fetch_or_mock_google_data

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

SUPPORTED_PLATFORMS = ("facebook", "google")


@router.post("/{platform}/connect")
async def connect_integration(platform: str, current_user: User = Depends(get_current_user)):
    """Mock connection to an external ad platform."""
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(status_code=400, detail="Unsupported platform")
    return {"status": "connected", "platform": platform}


@router.post("/{platform}/sync", response_model=SyncResponse)
async def sync_integration(
    platform: str,
    use_mock: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger a data sync from a connected ad platform."""
    if platform == "facebook":
        df = fetch_or_mock_facebook_data(days=30, use_mock=use_mock)
        name = "Facebook Ads Integration"
    elif platform == "google":
        df = fetch_or_mock_google_data(days=30, use_mock=use_mock)
        name = "Google Ads Integration"
    else:
        raise HTTPException(status_code=400, detail="Unsupported platform")

    if df.empty:
        return SyncResponse(
            status="success",
            dataset_id=None,
            rows=0,
            message=f"Connected to {platform.capitalize()}, but no campaign data found in the last 30 days.",
        )

    result = ingest_dataframe(db=db, user_id=current_user.id, df=df, name=name, filename=f"{name.replace(' ', '_')}.csv")

    return SyncResponse(
        status="synced",
        dataset_id=result.dataset_id,
        rows=result.rows,
        message=f"Successfully synced data from {platform.capitalize()}",
    )
