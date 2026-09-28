import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.database import Base, get_db
from backend.public_data.service import PublicDataService
from backend.knowledge.service import KnowledgeService
from backend.knowledge.embedding_service import get_embedding_service, MockEmbeddingService
from backend.knowledge.vector_index import build_vector_index
import backend.public_data.models
import backend.knowledge.models

from sqlalchemy.pool import StaticPool

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_semantic_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # 1. Seed data
    PublicDataService.seed_default_datasets(db)
    KnowledgeService.seed_default_knowledge(db)
    
    # 2. Build mock vector index
    temp_dir = tempfile.mkdtemp()
    os.environ["VECTOR_DIR"] = temp_dir
    os.environ["EMBEDDING_MODEL"] = "mock-model"
    
    embedding_service = MockEmbeddingService(dimension=384)
    # mock get_embedding_service
    import backend.knowledge.embedding_service
    original_get = backend.knowledge.embedding_service.get_embedding_service
    backend.knowledge.embedding_service.get_embedding_service = lambda: embedding_service
    
    build_vector_index(db, embedding_service=embedding_service, vector_dir=temp_dir)
    
    yield db
    
    # Teardown
    backend.knowledge.embedding_service.get_embedding_service = original_get
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_basic_semantic_search(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=water%20problem%20in%20Dharashiv&top_k=5")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["retriever"] == "semantic_faiss"
    assert data["result_count"] > 0
    
    first_result = data["results"][0]
    assert "evidence_id" in first_result
    assert "title" in first_result
    assert "similarity_score" in first_result
    assert "source_name" in first_result
    assert "source_url" in first_result
    assert "source_reference" in first_result

def test_ranking_descending(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=water&top_k=5")
    assert response.status_code == 200
    results = response.json()["results"]
    if len(results) > 1:
        scores = [r["similarity_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

def test_top_k(setup_semantic_db):
    for k in [1, 3, 5]:
        response = client.get(f"/api/knowledge/semantic-search?q=water&top_k={k}")
        assert response.status_code == 200
        assert len(response.json()["results"]) <= k

def test_maximum_top_k(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=water&top_k=25")
    assert response.status_code == 422 # FastAPI query validation error

def test_empty_query(setup_semantic_db):
    # Depending on how the query is defined (q: str) FastAPI might throw 422 or our custom 400
    response = client.get("/api/knowledge/semantic-search?q=&top_k=5")
    assert response.status_code in [400, 422]

def test_whitespace_query(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=%20%20%20&top_k=5")
    assert response.status_code in [400, 422]

def test_state_filter(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=water&state=Maharashtra&top_k=10")
    assert response.status_code == 200
    for r in response.json()["results"]:
        assert r["state"] == "Maharashtra"

def test_district_filter(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=water&district=Dharashiv")
    assert response.status_code == 200
    for r in response.json()["results"]:
        assert r["district"] == "Dharashiv"

def test_category_filter(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=water&category=Water")
    assert response.status_code == 200
    for r in response.json()["results"]:
        assert r["category"] == "Water"

def test_combined_filters(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=water&state=Maharashtra&category=Water")
    assert response.status_code == 200
    for r in response.json()["results"]:
        assert r["state"] == "Maharashtra"
        assert r["category"] == "Water"

def test_no_matching_metadata(setup_semantic_db):
    response = client.get("/api/knowledge/semantic-search?q=water&state=NonExistentState")
    assert response.status_code == 200
    assert response.json()["results"] == []

def test_missing_vector_index(setup_semantic_db):
    # Temporarily point VECTOR_DIR to an empty folder
    with tempfile.TemporaryDirectory() as empty_dir:
        import backend.config
        original_dir = backend.config.settings.vector_dir
        backend.config.settings.vector_dir = empty_dir
        try:
            response = client.get("/api/knowledge/semantic-search?q=water")
            assert response.status_code == 503
        finally:
            backend.config.settings.vector_dir = original_dir
    
    # Restore mock index env will happen naturally if needed, but not strictly required since it's the end of tests
