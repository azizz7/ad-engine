"""
FastAPI application for Ad Performance Intelligence Engine
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import pandas as pd
from typing import Optional, List
import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import joblib
import os

from analytics import AnalyticsEngine
from ml_models import MLModels
from insights import InsightsGenerator
import database as crud
from database_config import get_db, engine, Base
from auth import get_current_user, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, User
from models import User as UserModel

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ad Performance Intelligence Engine")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for ML models (Phase 1b: Persist these later if needed, or use joblib)
# For now, we will use a simple directory for persistence as per plan
MODELS_DIR = "models_cache"
os.makedirs(MODELS_DIR, exist_ok=True)

# -----------------
# Auth Endpoints
# -----------------

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Simple check for admin/admin if no users exist
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    
    if not user:
        # Create default admin if table is empty (Helper for MVP)
        if db.query(UserModel).count() == 0 and form_data.username == "admin@example.com" and form_data.password == "admin":
             # Create admin on the fly
             hashed = get_password_hash("admin")
             user = UserModel(email="admin@example.com", hashed_password=hashed, full_name="Admin User")
             db.add(user)
             db.commit()
             db.refresh(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    from auth import verify_password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "id": current_user.id
    }

# -----------------
# App Endpoints
# -----------------

def get_model_path(dataset_id: int):
    return os.path.join(MODELS_DIR, f"model_{dataset_id}.joblib")

@app.post("/api/upload")
async def upload_csv(
    file: UploadFile = File(...), 
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process CSV file with ad performance data
    """
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['date', 'impressions', 'clicks', 'spend']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing)}"
            )
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        
        # Generate dataset name if not provided
        dataset_name = name or f"{file.filename} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Store data in database
        date_range_start = df['date'].min().isoformat()
        date_range_end = df['date'].max().isoformat()
        
        dataset_id = crud.create_dataset(
            db=db,
            name=dataset_name,
            filename=file.filename,
            df=df,
            date_range_start=date_range_start,
            date_range_end=date_range_end
        )
        
        # Initialize analytics
        try:
            analytics_engine = AnalyticsEngine(df)
            analytics = analytics_engine.compute_all_metrics()
            crud.save_analytics(db, dataset_id, analytics)
        except Exception as e:
            # Cleanup on failure? For now, just log and raise
            raise HTTPException(status_code=500, detail=f"Error computing analytics: {str(e)}")
        
        # Initialize ML models
        try:
            ml_models = MLModels(df)
            # Persist model
            joblib.dump(ml_models, get_model_path(dataset_id))
        except Exception as e:
            print(f"ML Error: {e}")
            # Non-critical, can continue
        
        # Generate insights
        try:
            # We need the model for trends
            insights_gen = InsightsGenerator(df, analytics, ml_models)
            insights = insights_gen.generate_all_insights()
            crud.save_insights(db, dataset_id, insights)
        except Exception as e:
            print(f"Insights Error: {e}")
            
        return JSONResponse({
            "message": "File uploaded successfully",
            "dataset_id": dataset_id,
            "name": dataset_name,
            "rows": len(df),
            "columns": list(df.columns),
            "date_range": {
                "start": date_range_start,
                "end": date_range_end
            }
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/datasets")
async def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all uploaded datasets"""
    datasets = crud.list_datasets(db)
    return datasets


@app.get("/api/datasets/{dataset_id}")
async def get_dataset_info(
    dataset_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get information about a specific dataset"""
    dataset = crud.get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@app.get("/api/analytics")
async def get_analytics_endpoint(
    dataset_id: Optional[int] = Query(None), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get computed analytics metrics for a dataset"""
    if dataset_id is None:
        datasets = crud.list_datasets(db)
        if not datasets:
            raise HTTPException(status_code=404, detail="No datasets found")
        dataset_id = datasets[0].id
    
    analytics = crud.get_analytics(db, dataset_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Analytics not found for this dataset")
    
    return JSONResponse(analytics)


@app.get("/api/insights")
async def get_insights_endpoint(
    dataset_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get generated insights for a dataset"""
    if dataset_id is None:
        datasets = crud.list_datasets(db)
        if not datasets:
            raise HTTPException(status_code=404, detail="No datasets found")
        dataset_id = datasets[0].id
    
    insights = crud.get_insights(db, dataset_id)
    if insights is None:
        raise HTTPException(status_code=404, detail="Insights not found for this dataset")
    
    return JSONResponse(insights)


@app.get("/api/predictions")
async def get_predictions(
    days_ahead: int = 7, 
    dataset_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ML predictions for future performance"""
    if dataset_id is None:
        datasets = crud.list_datasets(db)
        if not datasets:
            raise HTTPException(status_code=404, detail="No datasets found")
        dataset_id = datasets[0].id
    
    # Try to load model
    model_path = get_model_path(dataset_id)
    if os.path.exists(model_path):
        try:
            ml_models = joblib.load(model_path)
            predictions = ml_models.predict_future(days_ahead=days_ahead)
            return JSONResponse(predictions)
        except Exception as e:
            print(f"Error loading model: {e}")
    
    # Fallback to retraining if model invalid or not found (e.g., old db)
    df = crud.get_dataset_data(db, dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset data not found")
        
    ml_models = MLModels(df)
    # Save it for next time
    joblib.dump(ml_models, model_path)
    
    predictions = ml_models.predict_future(days_ahead=days_ahead)
    return JSONResponse(predictions)


@app.get("/api/data")
async def get_data(
    dataset_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get raw data (for charts)"""
    if dataset_id is None:
        datasets = crud.list_datasets(db)
        if not datasets:
            raise HTTPException(status_code=404, detail="No datasets found")
        dataset_id = datasets[0].id
    
    df = crud.get_dataset_data(db, dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset data not found")
    
    # Convert to records
    records = df.to_dict('records')
    # Serialize dates
    serialized_records = []
    for record in records:
        serialized_record = {}
        for key, value in record.items():
            if pd.isna(value):
                serialized_record[key] = None
            elif isinstance(value, pd.Timestamp):
                serialized_record[key] = value.isoformat()
            else:
                serialized_record[key] = value
        serialized_records.append(serialized_record)
    
    return JSONResponse(serialized_records)


@app.delete("/api/datasets/{dataset_id}")
async def delete_dataset_endpoint(
    dataset_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a dataset and all associated data"""
    deleted = crud.delete_dataset(db, dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Remove model file
    model_path = get_model_path(dataset_id)
    if os.path.exists(model_path):
        os.remove(model_path)
    
    return JSONResponse({"message": "Dataset deleted successfully"})


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# -----------------
# Integration Endpoints
# -----------------

from integrations import fetch_or_mock_facebook_data, fetch_or_mock_google_data

async def process_dataframe_to_db(df: pd.DataFrame, dataset_name: str, db: Session):
    """Reusable logic to process a dataframe into the database"""
    # Create Dataset
    if df.empty:
        raise HTTPException(status_code=400, detail="No data received from integration")
        
    date_range_start = df['date'].min().isoformat()
    date_range_end = df['date'].max().isoformat()
    
    dataset_id = crud.create_dataset(
        db=db,
        name=dataset_name,
        filename=f"{dataset_name.replace(' ', '_')}.csv",
        df=df,
        date_range_start=date_range_start,
        date_range_end=date_range_end
    )
    
    # Analytics
    try:
        analytics_engine = AnalyticsEngine(df)
        analytics = analytics_engine.compute_all_metrics()
        crud.save_analytics(db, dataset_id, analytics)
    except Exception as e:
        print(f"Analytics Error: {e}")
        
    # ML Models
    try:
        ml_models = MLModels(df)
        joblib.dump(ml_models, get_model_path(dataset_id))
    except Exception as e:
        print(f"ML Error: {e}")
        
    # Insights
    try:
        insights_gen = InsightsGenerator(df, analytics, ml_models)
        insights = insights_gen.generate_all_insights()
        crud.save_insights(db, dataset_id, insights)
    except Exception as e:
        print(f"Insights Error: {e}")
        
    return dataset_id

@app.post("/api/integrations/{platform}/connect")
async def connect_integration(
    platform: str,
    current_user: User = Depends(get_current_user)
):
    """Mock connection to external platform"""
    if platform not in ["facebook", "google"]:
        raise HTTPException(status_code=400, detail="Unsupported platform")
    
    return {"status": "connected", "platform": platform}

@app.post("/api/integrations/{platform}/sync")
async def sync_integration(
    platform: str,
    use_mock: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger data sync from connected platform"""
    if platform == "facebook":
        df = fetch_or_mock_facebook_data(days=30, use_mock=use_mock)
        name = "Facebook Ads Integration"
    elif platform == "google":
        df = fetch_or_mock_google_data(days=30, use_mock=use_mock)
        name = "Google Ads Integration"
    else:
        raise HTTPException(status_code=400, detail="Unsupported platform")
    
    # Handle empty real data
    if df.empty:
         return {
            "status": "success",
            "dataset_id": None,
            "rows": 0,
            "message": f"Connected to {platform.capitalize()}, but no campaign data found in the last 30 days."
        }

    dataset_id = await process_dataframe_to_db(df, name, db)
    
    return {
        "status": "synced",
        "dataset_id": dataset_id,
        "rows": len(df),
        "message": f"Successfully synced data from {platform.capitalize()}"
    }

