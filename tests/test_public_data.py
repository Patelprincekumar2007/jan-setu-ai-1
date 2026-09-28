import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.main import app
from backend.database import init_db, SessionLocal
from backend.public_data.schemas import (
    DatasetCreate,
    PublicDataRecordCreate,
)
from backend.public_data.normalizer import (
    normalize_geographic_name,
    normalize_numeric_metric,
    normalize_category,
    normalize_integer,
)
from backend.public_data import repository
from backend.public_data.loaders import JJMWaterCoverageLoader
from backend.public_data.service import PublicDataService

# Ensure database tables exist and default datasets are seeded
init_db()
db = SessionLocal()
try:
    PublicDataService.seed_default_datasets(db)
finally:
    db.close()

client = TestClient(app)


# ==========================================
# 1. NORMALIZATION & CLEANUP TESTS
# ==========================================

def test_geographic_normalization_casing_and_whitespace():
    """Test whitespace trimming, internal space collapse, and state standard casing."""
    assert normalize_geographic_name("  MAHARASHTRA  ") == "Maharashtra"
    assert normalize_geographic_name("tamil   nadu") == "Tamil Nadu"
    assert normalize_geographic_name("GUJARAT") == "Gujarat"
    assert normalize_geographic_name("  dharashiv  ") == "Dharashiv"
    assert normalize_geographic_name("BENGALURU   RURAL") == "Bengaluru Rural"


def test_geographic_normalization_empty_and_null_values():
    """Test that missing or placeholder strings return None."""
    assert normalize_geographic_name(None) is None
    assert normalize_geographic_name("") is None
    assert normalize_geographic_name("   ") is None
    assert normalize_geographic_name("NA") is None
    assert normalize_geographic_name("N/A") is None
    assert normalize_geographic_name("null") is None
    assert normalize_geographic_name("-") is None


def test_numeric_metric_normalization():
    """Test deterministic conversion of numeric strings, commas, and floats."""
    assert normalize_numeric_metric("85.0") == 85.0
    assert normalize_numeric_metric(50.76) == 50.76
    assert normalize_numeric_metric("1,450.50") == 1450.50
    assert normalize_numeric_metric("0") == 0.0


def test_numeric_metric_invalid_and_missing_values():
    """Test that non-numeric, null, or invalid strings return None (no invented numbers)."""
    assert normalize_numeric_metric(None) is None
    assert normalize_numeric_metric("") is None
    assert normalize_numeric_metric("N/A") is None
    assert normalize_numeric_metric("invalid_text") is None
    assert normalize_numeric_metric("-") is None


def test_integer_normalization():
    """Test deterministic parsing of integers and years."""
    assert normalize_integer("2024") == 2024
    assert normalize_integer(2024) == 2024
    assert normalize_integer("312,450") == 312450
    assert normalize_integer(None) is None
    assert normalize_integer("N/A") is None


def test_category_normalization():
    """Test deterministic category mapping to valid civic sectors."""
    assert normalize_category("Water") == "Water"
    assert normalize_category("drinking water supply") == "Water"
    assert normalize_category("Rural Roads PMGSY") == "Roads"
    assert normalize_category("Primary Health Centre") == "Healthcare"
    assert normalize_category("Drainage and Sanitation") == "Sanitation"
    assert normalize_category("Arbitrary Unmapped Topic") == "Other"
    assert normalize_category(None) == "Other"


# ==========================================
# 2. SCHEMA & VALIDATION TESTS
# ==========================================

def test_dataset_create_valid_schema():
    """Verify DatasetCreate accepts valid metadata."""
    dataset = DatasetCreate(
        dataset_id="ds-test-01",
        title="Test Water Registry",
        description="Verified test description",
        source_name="National Open Data Portal",
        source_url="https://data.gov.in/resource/test",
        publisher="Ministry of Jal Shakti",
        data_type="Tabular CSV",
        geographic_scope="National (District-Level)",
        last_updated="2024-03-31",
        license="GODL",
        ingestion_status="NOT_INGESTED",
        record_count=0,
    )
    assert dataset.dataset_id == "ds-test-01"
    assert dataset.ingestion_status == "NOT_INGESTED"


def test_dataset_create_missing_source_url_allowed():
    """Verify source_url is optional and can be None."""
    dataset = DatasetCreate(
        dataset_id="ds-test-02",
        title="Test Dataset Without URL",
        source_name="State Census Bureau",
        source_url=None,
        data_type="CSV",
        geographic_scope="State-Level",
        license="GODL",
    )
    assert dataset.source_url is None


def test_dataset_create_invalid_status_rejected():
    """Verify invalid ingestion status is rejected by Pydantic."""
    with pytest.raises(ValidationError):
        DatasetCreate(
            dataset_id="ds-test-03",
            title="Test Dataset",
            source_name="Source",
            data_type="CSV",
            geographic_scope="District",
            license="GODL",
            ingestion_status="INVALID_STATUS",  # type: ignore
        )


def test_dataset_create_empty_title_rejected():
    """Verify empty or whitespace-only title is rejected."""
    with pytest.raises(ValidationError):
        DatasetCreate(
            dataset_id="ds-test-04",
            title="   ",
            source_name="Source",
            data_type="CSV",
            geographic_scope="District",
            license="GODL",
        )


def test_public_data_record_create_valid_schema():
    """Verify PublicDataRecordCreate creates valid record."""
    record = PublicDataRecordCreate(
        record_id="ds-test-rec-01",
        dataset_id="ds-test-01",
        state="Maharashtra",
        district="Dharashiv",
        locality=None,
        category="Water",
        metric_name="Rural Tap Water Coverage",
        metric_value=50.76,
        unit="%",
        year=2024,
        period="FY 2024",
        geographic_level="District",
        source_reference="OGD-JJM-2024-MH-01",
        notes="Total Households: 312450",
    )
    assert record.state == "Maharashtra"
    assert record.district == "Dharashiv"
    assert record.locality is None
    assert record.metric_value == 50.76
    assert record.source_reference == "OGD-JJM-2024-MH-01"


def test_public_data_record_invalid_category_rejected():
    """Verify invalid category is rejected."""
    with pytest.raises(ValidationError):
        PublicDataRecordCreate(
            record_id="ds-test-rec-02",
            dataset_id="ds-test-01",
            state="Maharashtra",
            district="Pune",
            category="INVALID_CATEGORY",  # type: ignore
            metric_name="Tap Water",
            metric_value=82.5,
            source_reference="ROW-01",
        )


def test_public_data_record_invalid_metric_value_rejected():
    """Verify non-numeric metric_value is rejected."""
    with pytest.raises(ValidationError):
        PublicDataRecordCreate(
            record_id="ds-test-rec-03",
            dataset_id="ds-test-01",
            state="Maharashtra",
            district="Pune",
            category="Water",
            metric_name="Tap Water",
            metric_value="not-a-number",  # type: ignore
            source_reference="ROW-01",
        )


# ==========================================
# 3. REPOSITORY & SERVICE TESTS
# ==========================================

def test_dataset_repository_crud():
    """Verify dataset repository creates, retrieves, lists, and updates datasets."""
    import uuid
    test_id = f"ds-repo-{uuid.uuid4().hex[:6]}"
    db = SessionLocal()
    try:
        dataset_in = DatasetCreate(
            dataset_id=test_id,
            title="Repository Test Dataset",
            source_name="Ministry of Jal Shakti",
            data_type="CSV",
            geographic_scope="National",
            license="GODL",
            ingestion_status="NOT_INGESTED",
        )
        created = repository.create_dataset(db, dataset_in)
        assert created.dataset_id == test_id

        fetched = repository.get_dataset(db, test_id)
        assert fetched is not None
        assert fetched.title == "Repository Test Dataset"

        updated = repository.update_dataset_status(db, test_id, status="INGESTED", record_count=10)
        assert updated.ingestion_status == "INGESTED"
        assert updated.record_count == 10

        datasets, total = repository.list_datasets(db)
        assert total >= 1
    finally:
        db.close()


def test_jjm_loader_and_provenance_preservation():
    """Verify the JJM loader reads raw CSV, preserves provenance IDs, and produces normalized records."""
    loader = JJMWaterCoverageLoader()
    dataset_meta, records = loader.load_and_normalize()

    assert dataset_meta.dataset_id == "ds-jjm-water-coverage-2024"
    assert dataset_meta.title == "District-wise Rural Household Tap Water Coverage (JJM Baseline)"
    assert dataset_meta.license == "Government Open Data License - India (GODL)"
    assert dataset_meta.source_url == "https://data.gov.in/resource/district-wise-rural-drinking-water-supply-and-tap-connections"
    assert len(records) > 0

    # Verify first record provenance
    first_record = records[0]
    assert first_record.state == "Maharashtra"
    assert first_record.district == "Dharashiv"
    assert first_record.metric_name == "Rural Tap Water Coverage"
    assert first_record.metric_value == 50.76
    assert first_record.unit == "%"
    assert first_record.source_reference == "OGD-JJM-2024-MH-01"
    assert first_record.locality is None  # District level data has no locality


# ==========================================
# 4. API ENDPOINT TESTS
# ==========================================

def test_api_list_datasets():
    """Verify GET /api/datasets returns registered datasets."""
    response = client.get("/api/datasets")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "datasets" in data
    assert data["total"] >= 1
    
    jjm_dataset = next((d for d in data["datasets"] if d["dataset_id"] == "ds-jjm-water-coverage-2024"), None)
    assert jjm_dataset is not None
    assert jjm_dataset["license"] == "Government Open Data License - India (GODL)"
    assert jjm_dataset["ingestion_status"] == "INGESTED"


def test_api_get_dataset_by_id():
    """Verify GET /api/datasets/{dataset_id} returns dataset metadata."""
    response = client.get("/api/datasets/ds-jjm-water-coverage-2024")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_id"] == "ds-jjm-water-coverage-2024"
    assert data["publisher"] == "Department of Drinking Water and Sanitation, Ministry of Jal Shakti, Government of India"
    assert data["source_url"] is not None


def test_api_get_dataset_404():
    """Verify GET /api/datasets/{dataset_id} returns 404 for non-existent dataset."""
    response = client.get("/api/datasets/non-existent-dataset-id")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_api_list_dataset_records_and_filters():
    """Verify GET /api/datasets/{dataset_id}/records returns records with filters."""
    response = client.get("/api/datasets/ds-jjm-water-coverage-2024/records?state=Maharashtra")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_id"] == "ds-jjm-water-coverage-2024"
    assert data["total"] >= 1
    for rec in data["records"]:
        assert rec["state"] == "Maharashtra"
        assert rec["source_reference"].startswith("OGD-JJM-2024-MH-")
