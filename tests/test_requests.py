import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db
from backend.schemas import GeminiExtractionResult

# Initialize database schema for tests
init_db()
client = TestClient(app)

def test_health_endpoint():
    """Verify health endpoint remains intact."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "nagriklens-ai-api"

def test_post_valid_request_without_gemini():
    """Verify request submission succeeds with ai_extraction_status NOT_PROCESSED when Gemini is unavailable."""
    payload = {
        "citizen_request": "Primary school needs drinking water pipeline connection urgently.",
        "state": "Maharashtra",
        "district": "Pune",
        "locality": "Ward 4",
        "category": "Water",
        "affected_households": 120,
    }
    with patch("backend.routes.requests.extract_request_intelligence", return_value=None):
        response = client.post("/api/requests", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["reference_id"].startswith("NL-")
    assert data["status"] == "RECEIVED"
    assert data["ai_extraction_status"] == "NOT_PROCESSED"
    assert "Request submitted successfully" in data["message"]

def test_post_valid_request_with_mocked_gemini():
    """Verify request submission populates AI extraction fields and returns PROCESSED when Gemini succeeds."""
    payload = {
        "citizen_request": "Primary health centre lacks clean drinking water facility and borewell is non-functional.",
        "state": "Maharashtra",
        "district": "Dharashiv",
        "locality": "Ward 4",
        "category": "Water",
        "affected_households": 85,
    }
    
    mocked_ai_result = GeminiExtractionResult(
        language="English",
        category="Water",
        problem_summary="Primary health centre has a non-functional borewell and lacks clean drinking water.",
        severity="HIGH",
        affected_group="Patients and healthcare workers",
        location_hint="Ward 4",
    )

    with patch("backend.routes.requests.extract_request_intelligence", return_value=mocked_ai_result):
        response = client.post("/api/requests", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["reference_id"].startswith("NL-")
    assert data["status"] == "RECEIVED"
    assert data["ai_extraction_status"] == "PROCESSED"

def test_missing_citizen_request():
    """Reject payload missing citizen request or with whitespace-only."""
    payload = {
        "citizen_request": "   ",
        "state": "Maharashtra",
        "district": "Pune",
        "locality": "Ward 4",
        "category": "Water",
    }
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422

def test_missing_state():
    """Reject payload missing state."""
    payload = {
        "citizen_request": "Need road repair on main street.",
        "district": "Pune",
        "locality": "Ward 4",
        "category": "Roads",
    }
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422

def test_missing_district():
    """Reject payload missing district."""
    payload = {
        "citizen_request": "Need road repair on main street.",
        "state": "Maharashtra",
        "locality": "Ward 4",
        "category": "Roads",
    }
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422

def test_missing_locality():
    """Reject payload missing locality."""
    payload = {
        "citizen_request": "Need road repair on main street.",
        "state": "Maharashtra",
        "district": "Pune",
        "category": "Roads",
    }
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422

def test_missing_category():
    """Reject payload missing category."""
    payload = {
        "citizen_request": "Need road repair on main street.",
        "state": "Maharashtra",
        "district": "Pune",
        "locality": "Ward 4",
    }
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422

def test_negative_affected_household_count():
    """Reject negative affected household count."""
    payload = {
        "citizen_request": "Hospital facility lacks emergency supplies.",
        "state": "Karnataka",
        "district": "Bengaluru Rural",
        "locality": "Ward 8",
        "category": "Healthcare",
        "affected_households": -10,
    }
    response = client.post("/api/requests", json=payload)
    assert response.status_code == 422

def test_reference_id_generation_and_uniqueness():
    """Verify format and uniqueness across sequential submissions."""
    payload1 = {
        "citizen_request": "Drainage overflow during monsoon season.",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "locality": "Locality A",
        "category": "Sanitation",
    }
    payload2 = {
        "citizen_request": "Street lights not functioning on main road.",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "locality": "Locality B",
        "category": "Other",
    }
    with patch("backend.routes.requests.extract_request_intelligence", return_value=None):
        res1 = client.post("/api/requests", json=payload1)
        res2 = client.post("/api/requests", json=payload2)

    assert res1.status_code == 201
    assert res2.status_code == 201

    ref1 = res1.json()["reference_id"]
    ref2 = res2.json()["reference_id"]

    assert ref1 != ref2
    assert ref1.startswith("NL-")
    assert ref2.startswith("NL-")

def test_get_existing_request():
    """GET existing request returns correct details and status RECEIVED."""
    payload = {
        "citizen_request": "Borewell motor damaged, no water supply for past two weeks.",
        "state": "Tamil Nadu",
        "district": "Madurai",
        "locality": "South Ward 11",
        "category": "Water",
        "affected_households": 80,
    }
    with patch("backend.routes.requests.extract_request_intelligence", return_value=None):
        create_res = client.post("/api/requests", json=payload)
    assert create_res.status_code == 201
    ref_id = create_res.json()["reference_id"]

    get_res = client.get(f"/api/requests/{ref_id}")
    assert get_res.status_code == 200
    data = get_res.json()

    assert data["reference_id"] == ref_id
    assert data["status"] == "RECEIVED"
    assert data["category"] == "Water"
    assert data["location"]["state"] == "Tamil Nadu"
    assert data["location"]["district"] == "Madurai"
    assert data["location"]["locality"] == "South Ward 11"
    assert "created_at" in data

def test_get_nonexistent_request_returns_404():
    """GET nonexistent reference ID returns 404 with proper message."""
    response = client.get("/api/requests/NL-20260928-INVALID999")
    assert response.status_code == 404
    data = response.json()
    assert "Request not found" in data["detail"]
