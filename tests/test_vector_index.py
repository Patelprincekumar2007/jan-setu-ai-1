import os
import pytest
import shutil
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
import backend.public_data.models  # Ensure SQLAlchemy sees these
from backend.knowledge.models import KnowledgeEvidence
from backend.knowledge.embedding_service import MockEmbeddingService
from backend.knowledge.vector_index import (
    build_vector_index,
    search_vector_index,
    get_vector_index_status,
    VectorIndexUnavailableException,
    compute_evidence_content_hash,
)

# Use test-specific vector directory
TEST_VECTOR_DIR = "./data/test_vector"

test_engine = create_engine("sqlite:///:memory:")
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    
    # Add dummy evidence
    evidence1 = KnowledgeEvidence(
        evidence_id="ev-1",
        dataset_id="ds-1",
        record_id="rec-1",
        title="Test Evidence 1",
        content="water problem in Dharashiv",
        state="Maharashtra",
        district="Dharashiv",
        category="Water",
        metric_name="metric1",
        source_name="source1",
        source_reference="ref1",
    )
    evidence2 = KnowledgeEvidence(
        evidence_id="ev-2",
        dataset_id="ds-1",
        record_id="rec-2",
        title="Test Evidence 2",
        content="rural tap water coverage in Maharashtra",
        state="Maharashtra",
        district="Pune",
        category="Water",
        metric_name="metric2",
        source_name="source1",
        source_reference="ref2",
    )
    
    db.add(evidence1)
    db.add(evidence2)
    db.commit()
    
    yield db
    
    db.query(KnowledgeEvidence).delete()
    db.commit()
    db.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function", autouse=True)
def cleanup_vector_dir():
    if os.path.exists(TEST_VECTOR_DIR):
        shutil.rmtree(TEST_VECTOR_DIR)
    os.makedirs(TEST_VECTOR_DIR, exist_ok=True)
    yield
    if os.path.exists(TEST_VECTOR_DIR):
        shutil.rmtree(TEST_VECTOR_DIR)


def test_embedding_service_normalization():
    service = MockEmbeddingService(dimension=4)
    docs = ["hello world", "test"]
    vectors = service.encode_documents(docs)
    
    for vec in vectors:
        norm = np.linalg.norm(vec)
        assert np.isclose(norm, 1.0, atol=1e-5), f"Vector is not L2 normalized, norm={norm}"


def test_vector_index_creation_and_status(setup_db):
    db = setup_db
    service = MockEmbeddingService(model_name="test-model", dimension=64)
    
    status = get_vector_index_status(db, service, TEST_VECTOR_DIR)
    assert not status["available"]
    assert status["reason"] == "index_not_found"
    
    build_summary = build_vector_index(db, service, TEST_VECTOR_DIR)
    assert build_summary["status"] == "built"
    assert build_summary["evidence_count"] == 2
    
    status = get_vector_index_status(db, service, TEST_VECTOR_DIR)
    assert status["available"]
    assert status["embedding_model"] == "test-model"
    assert status["dimension"] == 64
    assert status["evidence_count"] == 2


def test_stale_index_detection_model_mismatch(setup_db):
    db = setup_db
    service1 = MockEmbeddingService(model_name="model-1", dimension=64)
    build_vector_index(db, service1, TEST_VECTOR_DIR)
    
    service2 = MockEmbeddingService(model_name="model-2", dimension=64)
    status = get_vector_index_status(db, service2, TEST_VECTOR_DIR)
    
    assert not status["available"]
    assert status["stale"]
    assert status["reason"] == "model_mismatch"


def test_stale_index_detection_content_hash(setup_db):
    db = setup_db
    service = MockEmbeddingService(model_name="test-model", dimension=64)
    build_vector_index(db, service, TEST_VECTOR_DIR)
    
    # Modify db to trigger hash mismatch
    ev = db.query(KnowledgeEvidence).first()
    old_content = ev.content
    ev.content = "New changed content"
    db.commit()
    
    status = get_vector_index_status(db, service, TEST_VECTOR_DIR)
    assert not status["available"]
    assert status["stale"]
    assert status["reason"] == "stale_index"
    
    # Revert for other tests
    ev.content = old_content
    db.commit()


def test_semantic_search_functionality(setup_db):
    db = setup_db
    service = MockEmbeddingService(model_name="test-model", dimension=64)
    build_vector_index(db, service, TEST_VECTOR_DIR)
    
    results, total = search_vector_index(db, "water problem in Dharashiv", top_k=5, embedding_service=service, vector_dir=TEST_VECTOR_DIR)
    
    assert total > 0
    assert len(results) > 0
    # First result should be the one closest to query (mock embedding uses hash, so identical string should be closest)
    assert results[0][0].content == "water problem in Dharashiv"
    
    # Test filtering
    results_filtered, total_filtered = search_vector_index(db, "water", district="Pune", embedding_service=service, vector_dir=TEST_VECTOR_DIR)
    assert total_filtered == 1
    assert results_filtered[0][0].district == "Pune"


def test_missing_index_behavior(setup_db):
    db = setup_db
    service = MockEmbeddingService(model_name="test-model", dimension=64)
    
    # Do not build index
    with pytest.raises(VectorIndexUnavailableException):
        search_vector_index(db, "query", embedding_service=service, vector_dir=TEST_VECTOR_DIR)
