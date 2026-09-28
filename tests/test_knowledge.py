import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.main import app
from backend.database import init_db, SessionLocal
from backend.public_data.models import PublicDataRecord, Dataset
from backend.public_data.service import PublicDataService
from backend.knowledge.schemas import KnowledgeEvidenceCreate
from backend.knowledge.builders import build_knowledge_evidence, build_evidence_content
from backend.knowledge import repository as knowledge_repo
from backend.knowledge.service import KnowledgeService, DeterministicMetadataRetriever

# Ensure DB initialized and seeded
init_db()
db = SessionLocal()
try:
    PublicDataService.seed_default_datasets(db)
    KnowledgeService.seed_default_knowledge(db)
finally:
    db.close()

client = TestClient(app)


# ==========================================
# 1. SCHEMA & BUILDER TESTS
# ==========================================

def test_knowledge_evidence_schema_valid():
    """Verify KnowledgeEvidenceCreate accepts valid attributes."""
    evidence = KnowledgeEvidenceCreate(
        evidence_id="EVID-ds-test-01-ROW-01",
        dataset_id="ds-test-01",
        record_id="REC-01",
        title="Dharashiv (Maharashtra) - Rural Tap Water Coverage",
        content="District Dharashiv, Maharashtra had rural household tap water coverage of 50.76% according to the Jal Jeevan Mission baseline dataset for 2024.",
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
        source_name="Open Government Data Platform India / Ministry of Jal Shakti",
        source_url="https://data.gov.in/resource/test",
        source_reference="OGD-JJM-2024-MH-01",
    )
    assert evidence.evidence_id == "EVID-ds-test-01-ROW-01"
    assert evidence.category == "Water"
    assert evidence.metric_value == 50.76


def test_knowledge_evidence_schema_invalid_category_rejected():
    """Verify schema rejects invalid categories."""
    with pytest.raises(ValidationError):
        KnowledgeEvidenceCreate(
            evidence_id="EVID-test-02",
            dataset_id="ds-test",
            record_id="REC-02",
            title="Test Title",
            content="Valid factual content description",
            state="Maharashtra",
            district="Pune",
            category="INVALID_CATEGORY",  # type: ignore
            metric_name="Metric",
            source_name="Source",
            source_reference="REF-01",
        )


def test_knowledge_evidence_schema_empty_content_rejected():
    """Verify schema rejects empty or whitespace-only content."""
    with pytest.raises(ValidationError):
        KnowledgeEvidenceCreate(
            evidence_id="EVID-test-03",
            dataset_id="ds-test",
            record_id="REC-03",
            title="Test Title",
            content="   ",
            state="Maharashtra",
            district="Pune",
            category="Water",
            metric_name="Metric",
            source_name="Source",
            source_reference="REF-01",
        )


def test_deterministic_evidence_builder():
    """Verify builder produces factual content and preserves complete provenance without LLM."""
    dummy_dataset = {
        "dataset_id": "ds-test-water",
        "title": "Jal Jeevan Mission Baseline 2024",
        "source_name": "Ministry of Jal Shakti",
        "source_url": "https://data.gov.in/test",
        "publisher": "Department of Drinking Water",
        "license": "GODL",
        "last_updated": "2024-03-31",
    }
    dummy_record = PublicDataRecord(
        record_id="REC-TEST-MH-01",
        dataset_id="ds-test-water",
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
        notes="Total Rural Households: 312450",
    )

    evidence = build_knowledge_evidence(dummy_record, dummy_dataset)
    assert evidence.evidence_id == "EVID-ds-test-water-OGD-JJM-2024-MH-01"
    assert evidence.state == "Maharashtra"
    assert evidence.district == "Dharashiv"
    assert evidence.source_reference == "OGD-JJM-2024-MH-01"
    assert "District Dharashiv, Maharashtra recorded rural tap water coverage of 50.76%" in evidence.content
    assert "Jal Jeevan Mission Baseline 2024 for 2024" in evidence.content
    assert "Total Rural Households: 312450" in evidence.content


# ==========================================
# 2. INGESTION & IDEMPOTENCY TESTS
# ==========================================

def test_idempotent_dataset_knowledge_ingestion():
    """Verify running knowledge ingestion multiple times produces identical record counts with no duplicates."""
    db_session = SessionLocal()
    try:
        dataset_id = "ds-jjm-water-coverage-2024"
        count_1 = KnowledgeService.ingest_dataset_to_knowledge(db_session, dataset_id)
        assert count_1 == 25

        count_2 = KnowledgeService.ingest_dataset_to_knowledge(db_session, dataset_id)
        assert count_2 == 25

        total_in_db = knowledge_repo.count_knowledge_evidence_by_dataset(db_session, dataset_id)
        assert total_in_db == 25
    finally:
        db_session.close()


def test_source_integrity_provenance_test():
    """Verify that every ingested evidence record contains complete provenance."""
    db_session = SessionLocal()
    try:
        dataset_id = "ds-jjm-water-coverage-2024"
        records, total = knowledge_repo.list_knowledge_evidence_by_dataset(db_session, dataset_id, limit=50)
        assert total == 25
        for r in records:
            assert r.dataset_id == dataset_id
            assert r.record_id is not None and len(r.record_id) > 0
            assert r.source_name == "Open Government Data (OGD) Platform India / Ministry of Jal Shakti"
            assert r.source_reference.startswith("OGD-JJM-2024-")
            assert r.source_url == "https://data.gov.in/resource/district-wise-rural-drinking-water-supply-and-tap-connections"
    finally:
        db_session.close()


# ==========================================
# 3. BASELINE RETRIEVER TESTS
# ==========================================

def test_deterministic_retriever_exact_district():
    """Verify baseline retriever finds Dharashiv by exact district filter."""
    db_session = SessionLocal()
    try:
        retriever = DeterministicMetadataRetriever(db_session)
        results, total = retriever.retrieve(query="water", district="Dharashiv", category="Water", top_k=5)
        assert total >= 1
        assert len(results) >= 1

        dharashiv = results[0]
        assert dharashiv.state == "Maharashtra"
        assert dharashiv.district == "Dharashiv"
        assert dharashiv.category == "Water"
        assert dharashiv.metric_value == 50.76
        assert dharashiv.unit == "%"
        assert dharashiv.source_reference == "OGD-JJM-2024-MH-01"
    finally:
        db_session.close()


def test_deterministic_retriever_state_filter():
    """Verify baseline retriever filters by state correctly."""
    db_session = SessionLocal()
    try:
        retriever = DeterministicMetadataRetriever(db_session)
        results, total = retriever.retrieve(state="Karnataka", top_k=10)
        assert total == 3
        for r in results:
            assert r.state == "Karnataka"
    finally:
        db_session.close()


def test_deterministic_retriever_category_filter():
    """Verify baseline retriever filters by category."""
    db_session = SessionLocal()
    try:
        retriever = DeterministicMetadataRetriever(db_session)
        results, total = retriever.retrieve(category="Water", top_k=5)
        assert total == 25
        assert len(results) == 5
        for r in results:
            assert r.category == "Water"
    finally:
        db_session.close()


def test_deterministic_retriever_top_k_bounds():
    """Verify top_k bounds validation."""
    db_session = SessionLocal()
    try:
        retriever = DeterministicMetadataRetriever(db_session)
        with pytest.raises(ValueError):
            retriever.retrieve(top_k=0)

        with pytest.raises(ValueError):
            retriever.retrieve(top_k=25)
    finally:
        db_session.close()


def test_deterministic_retriever_empty_result():
    """Verify non-matching query returns empty result with total=0."""
    db_session = SessionLocal()
    try:
        retriever = DeterministicMetadataRetriever(db_session)
        results, total = retriever.retrieve(district="NonExistentDistrictXYZ", top_k=5)
        assert total == 0
        assert len(results) == 0
    finally:
        db_session.close()


# ==========================================
# 4. API ENDPOINT TESTS
# ==========================================

def test_api_knowledge_search_success():
    """Verify GET /api/knowledge/search endpoint returns structured baseline results."""
    response = client.get("/api/knowledge/search?q=water&district=Dharashiv&category=Water&top_k=5")
    assert response.status_code == 200
    data = response.json()
    assert data["retriever"] == "baseline_metadata"
    assert data["query"] == "water"
    assert data["total"] >= 1
    assert len(data["results"]) >= 1

    first = data["results"][0]
    assert first["district"] == "Dharashiv"
    assert first["state"] == "Maharashtra"
    assert first["metric_value"] == 50.76
    assert first["source_reference"] == "OGD-JJM-2024-MH-01"


def test_api_knowledge_search_invalid_top_k():
    """Verify GET /api/knowledge/search rejects invalid top_k."""
    response = client.get("/api/knowledge/search?top_k=30")
    assert response.status_code == 422  # FastAPI query validation fails


def test_api_knowledge_dataset_summary():
    """Verify GET /api/knowledge/datasets/{dataset_id} returns knowledge evidence summary."""
    response = client.get("/api/knowledge/datasets/ds-jjm-water-coverage-2024")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_id"] == "ds-jjm-water-coverage-2024"
    assert data["evidence_count"] == 25
    assert data["ingestion_status"] == "INGESTED"


def test_api_knowledge_dataset_summary_404():
    """Verify GET /api/knowledge/datasets/{dataset_id} returns 404 for unknown dataset."""
    response = client.get("/api/knowledge/datasets/unknown-ds-999")
    assert response.status_code == 404
