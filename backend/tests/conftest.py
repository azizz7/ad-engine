import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    """A fresh in-memory SQLite database per test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    """Log in as the bootstrapped default admin and return an Authorization header."""
    response = client.post("/token", data={"username": "admin@example.com", "password": "admin"})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_df():
    return pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10),
            "platform": ["Facebook"] * 5 + ["Google"] * 5,
            "ad_name": [f"Ad_{i}" for i in range(10)],
            "impressions": [1000 + i * 10 for i in range(10)],
            "clicks": [50 + i for i in range(10)],
            "spend": [100.0 + i for i in range(10)],
            "conversions": [5 + i for i in range(10)],
            "revenue": [300.0 + i * 5 for i in range(10)],
        }
    )
