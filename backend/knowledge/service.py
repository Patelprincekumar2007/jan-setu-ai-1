import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.public_data import repository as public_data_repo
from backend.knowledge.builders import build_knowledge_evidence
from backend.knowledge import repository as knowledge_repo
from backend.knowledge.schemas import (
    KnowledgeEvidenceResponse,
    KnowledgeEvidenceCreate,
    KnowledgeDatasetSummaryResponse,
)

logger = logging.getLogger("nagriklens.knowledge")


class BaseKnowledgeRetriever(ABC):
    """
    Abstract Retrieval Contract for NagrikLens AI.
    All future retrievers (e.g. VectorKnowledgeRetriever, HybridKnowledgeRetriever) must implement this contract.
    """

    @abstractmethod
    def retrieve(
        self,
        query: Optional[str] = None,
        *,
        state: Optional[str] = None,
        district: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> Tuple[List[KnowledgeEvidenceResponse], int]:
        """
        Retrieves matching KnowledgeEvidence objects based on query and metadata filters.
        """
        pass


class DeterministicMetadataRetriever(BaseKnowledgeRetriever):
    """
    Baseline deterministic metadata-driven retriever.
    Performs deterministic filtering over structured public knowledge records.
    """

    def __init__(self, db: Session):
        self.db = db

    def retrieve(
        self,
        query: Optional[str] = None,
        *,
        state: Optional[str] = None,
        district: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
    ) -> Tuple[List[KnowledgeEvidenceResponse], int]:
        # Validate top_k
        if top_k < 1 or top_k > 20:
            raise ValueError("top_k must be an integer between 1 and 20.")

        records, total = knowledge_repo.query_knowledge_evidence_deterministic(
            db=self.db,
            query_text=query,
            state=state,
            district=district,
            category=category,
            top_k=top_k,
        )

        results = [
            KnowledgeEvidenceResponse(
                evidence_id=r.evidence_id,
                dataset_id=r.dataset_id,
                record_id=r.record_id,
                title=r.title,
                content=r.content,
                state=r.state,
                district=r.district,
                locality=r.locality,
                category=r.category,  # type: ignore
                metric_name=r.metric_name,
                metric_value=r.metric_value,
                unit=r.unit,
                year=r.year,
                period=r.period,
                geographic_level=r.geographic_level,
                source_name=r.source_name,
                source_url=r.source_url,
                source_reference=r.source_reference,
                publisher=r.publisher,
                license=r.license,
                last_updated=r.last_updated,
                notes=r.notes,
                created_at=r.created_at,
            )
            for r in records
        ]

        return results, total


class KnowledgeService:
    @staticmethod
    def ingest_dataset_to_knowledge(db: Session, dataset_id: str) -> int:
        """
        Converts all PublicDataRecords of a dataset into KnowledgeEvidence and stores them idempotently.
        """
        dataset = public_data_repo.get_dataset(db, dataset_id)
        if not dataset:
            raise ValueError(f"Dataset '{dataset_id}' not found.")

        records, _ = public_data_repo.list_public_records(db, dataset_id=dataset_id, limit=1000)
        if not records:
            logger.warning(f"No records found for dataset '{dataset_id}' to ingest into knowledge.")
            return 0

        evidence_list: List[KnowledgeEvidenceCreate] = []
        for r in records:
            evidence = build_knowledge_evidence(record=r, dataset=dataset)
            evidence_list.append(evidence)

        count = knowledge_repo.bulk_upsert_knowledge_evidence(db, dataset_id=dataset_id, evidence_list=evidence_list)
        logger.info(f"Ingested {count} evidence records for dataset '{dataset_id}'.")
        return count

    @staticmethod
    def get_dataset_summary(db: Session, dataset_id: str) -> Optional[KnowledgeDatasetSummaryResponse]:
        """Returns knowledge layer summary for a dataset."""
        dataset = public_data_repo.get_dataset(db, dataset_id)
        if not dataset:
            return None

        evidence_count = knowledge_repo.count_knowledge_evidence_by_dataset(db, dataset_id)

        return KnowledgeDatasetSummaryResponse(
            dataset_id=dataset.dataset_id,
            title=dataset.title,
            source_name=dataset.source_name,
            source_url=dataset.source_url,
            publisher=dataset.publisher,
            license=dataset.license,
            ingestion_status=dataset.ingestion_status,
            evidence_count=evidence_count,
            last_updated=dataset.last_updated,
        )

    @classmethod
    def seed_default_knowledge(cls, db: Session) -> None:
        """Auto-seeds default public datasets into the knowledge evidence store."""
        try:
            dataset_id = "ds-jjm-water-coverage-2024"
            dataset = public_data_repo.get_dataset(db, dataset_id)
            if dataset and dataset.record_count > 0:
                cls.ingest_dataset_to_knowledge(db, dataset_id)
        except Exception as e:
            logger.error(f"Error during default knowledge seeding: {e}", exc_info=True)
