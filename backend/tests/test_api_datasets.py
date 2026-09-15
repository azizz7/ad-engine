import io


def _csv_bytes(sample_df):
    return io.BytesIO(sample_df.to_csv(index=False).encode("utf-8"))


def test_upload_requires_auth(client, sample_df):
    response = client.post(
        "/api/upload", files={"file": ("data.csv", _csv_bytes(sample_df), "text/csv")}
    )
    assert response.status_code == 401


def test_upload_rejects_missing_required_columns(client, auth_headers):
    bad_csv = io.BytesIO(b"date,spend\n2024-01-01,10\n")
    response = client.post(
        "/api/upload",
        headers=auth_headers,
        files={"file": ("bad.csv", bad_csv, "text/csv")},
    )
    assert response.status_code == 400
    assert "Missing required columns" in response.json()["detail"]


def test_upload_then_fetch_analytics_and_insights(client, auth_headers, sample_df):
    upload = client.post(
        "/api/upload",
        headers=auth_headers,
        files={"file": ("data.csv", _csv_bytes(sample_df), "text/csv")},
    )
    assert upload.status_code == 200, upload.text
    dataset_id = upload.json()["dataset_id"]
    assert upload.json()["rows"] == len(sample_df)

    analytics = client.get(f"/api/analytics?dataset_id={dataset_id}", headers=auth_headers)
    assert analytics.status_code == 200
    assert analytics.json()["overall_metrics"]["total_impressions"] > 0

    insights = client.get(f"/api/insights?dataset_id={dataset_id}", headers=auth_headers)
    assert insights.status_code == 200
    assert "insights" in insights.json()
    # ai_summary is always present (None when ANTHROPIC_API_KEY isn't set)
    # so the frontend has a consistent shape to render either way.
    assert "ai_summary" in insights.json()

    listing = client.get("/api/datasets", headers=auth_headers)
    assert listing.status_code == 200
    assert any(d["id"] == dataset_id for d in listing.json())


def test_predictions_forecast_forward_without_a_persisted_model(client, auth_headers, sample_df):
    """Predictions are computed on demand now (no joblib cache on disk);
    this just confirms the endpoint still returns a sane forecast shape."""
    upload = client.post(
        "/api/upload",
        headers=auth_headers,
        files={"file": ("data.csv", _csv_bytes(sample_df), "text/csv")},
    )
    dataset_id = upload.json()["dataset_id"]

    response = client.get(f"/api/predictions?dataset_id={dataset_id}&days_ahead=5", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "revenue" in body
    assert len(body["revenue"]) == 5
    assert all("lower_bound" in p and "upper_bound" in p for p in body["revenue"])


def test_dataset_lookup_is_scoped_to_owner(client, db_session, auth_headers, sample_df):
    """Dataset reads are filtered by user_id; a dataset owned by a different
    user must 404 rather than leak, even though the row exists."""
    upload = client.post(
        "/api/upload",
        headers=auth_headers,
        files={"file": ("data.csv", _csv_bytes(sample_df), "text/csv")},
    )
    dataset_id = upload.json()["dataset_id"]

    from app.core.security import get_password_hash
    from app.models.dataset import Dataset
    from app.models.user import User

    other_user = User(email="other@example.com", hashed_password=get_password_hash("x"))
    db_session.add(other_user)
    db_session.commit()

    owned_dataset = db_session.query(Dataset).filter(Dataset.id == dataset_id).one()
    assert owned_dataset.user_id != other_user.id

    response = client.get("/api/datasets/999999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_dataset(client, auth_headers, sample_df):
    upload = client.post(
        "/api/upload",
        headers=auth_headers,
        files={"file": ("data.csv", _csv_bytes(sample_df), "text/csv")},
    )
    dataset_id = upload.json()["dataset_id"]

    delete = client.delete(f"/api/datasets/{dataset_id}", headers=auth_headers)
    assert delete.status_code == 200

    missing = client.get(f"/api/datasets/{dataset_id}", headers=auth_headers)
    assert missing.status_code == 404

    delete_again = client.delete(f"/api/datasets/{dataset_id}", headers=auth_headers)
    assert delete_again.status_code == 404


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
