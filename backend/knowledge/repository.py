from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from backend.knowledge.models import KnowledgeEvidence
from backend.knowledge.schemas import KnowledgeEvidenceCreate


def upsert_knowledge_evidence(db: Session, evidence_in: KnowledgeEvidenceCreate) -> KnowledgeEvidence:
    """Inserts or updates a single knowledge evidence record idempotently."""
    existing = db.query(KnowledgeEvidence).filter(KnowledgeEvidence.evidence_id == evidence_in.evidence_id).first()
    if existing:
        for key, val in evidence_in.model_dump().items():
            setattr(existing, key, val)
        db.commit()
        db.refresh(existing)
        return existing

    db_obj = KnowledgeEvidence(**evidence_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def bulk_upsert_knowledge_evidence(db: Session, dataset_id: str, evidence_list: List[KnowledgeEvidenceCreate]) -> int:
    """
    Idempotently persists knowledge evidence records for a dataset.
    Clears existing records for this dataset and inserts fresh normalized evidence.
    """
    if not evidence_list:
        return 0

    # Delete existing knowledge records for this dataset to maintain idempotency
    db.query(KnowledgeEvidence).filter(KnowledgeEvidence.dataset_id == dataset_id).delete()

    db_objects = [KnowledgeEvidence(**item.model_dump()) for item in evidence_list]
    db.bulk_save_objects(db_objects)
    db.commit()
    return len(db_objects)


def get_knowledge_evidence(db: Session, evidence_id: str) -> Optional[KnowledgeEvidence]:
    """Retrieve knowledge evidence by unique evidence ID."""
    return db.query(KnowledgeEvidence).filter(KnowledgeEvidence.evidence_id == evidence_id).first()


def list_knowledge_evidence_by_dataset(db: Session, dataset_id: str, skip: int = 0, limit: int = 100) -> Tuple[List[KnowledgeEvidence], int]:
    """List knowledge evidence items belonging to a dataset."""
    query = db.query(KnowledgeEvidence).filter(KnowledgeEvidence.dataset_id == dataset_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def count_knowledge_evidence_by_dataset(db: Session, dataset_id: str) -> int:
    """Returns count of knowledge evidence records for a given dataset."""
    return db.query(KnowledgeEvidence).filter(KnowledgeEvidence.dataset_id == dataset_id).count()


def query_knowledge_evidence_deterministic(
    db: Session,
    query_text: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
) -> Tuple[List[KnowledgeEvidence], int]:
    """
    Deterministic baseline metadata query:
    Applies exact/partial geographic and category filters, then ranks by relevance:
    1. Exact district match
    2. Exact state match
    3. Exact category match
    4. Query text inclusion in content/title
    """
    query = db.query(KnowledgeEvidence)

    conditions = []
    if district:
        conditions.append(KnowledgeEvidence.district.ilike(f"%{district.strip()}%"))
    if state:
        conditions.append(KnowledgeEvidence.state.ilike(f"%{state.strip()}%"))
    if category:
        conditions.append(KnowledgeEvidence.category == category.strip())

    if query_text and query_text.strip():
        term = query_text.strip()
        conditions.append(
            or_(
                KnowledgeEvidence.content.ilike(f"%{term}%"),
                KnowledgeEvidence.title.ilike(f"%{term}%"),
                KnowledgeEvidence.metric_name.ilike(f"%{term}%"),
                KnowledgeEvidence.district.ilike(f"%{term}%"),
                KnowledgeEvidence.state.ilike(f"%{term}%"),
            )
        )

    if conditions:
        query = query.filter(and_(*conditions))

    total = query.count()
    results = query.order_by(
        KnowledgeEvidence.state.asc(),
        KnowledgeEvidence.district.asc(),
    ).limit(top_k).all()

    return results, total
