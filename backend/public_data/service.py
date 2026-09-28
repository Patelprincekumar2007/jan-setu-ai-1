import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.public_data.models import Dataset, PublicDataRecord
from backend.public_data.schemas import DatasetCreate, PublicDataRecordCreate
from backend.public_data import repository
from backend.public_data.loaders import BaseDatasetLoader, JJMWaterCoverageLoader

logger = logging.getLogger("nagriklens.public_data")


class PublicDataService:
    @staticmethod
    def register_dataset(db: Session, dataset_in: DatasetCreate) -> Dataset:
        """Register a new public dataset metadata record."""
        existing = repository.get_dataset(db, dataset_in.dataset_id)
        if existing:
            logger.info(f"Dataset '{dataset_in.dataset_id}' already registered.")
            return existing
        return repository.create_dataset(db, dataset_in)

    @staticmethod
    def ingest_from_loader(db: Session, loader: BaseDatasetLoader) -> Tuple[Dataset, int]:
        """Runs loader normalization and stores dataset metadata and records in SQLite."""
        dataset_meta, records = loader.load_and_normalize()

        # 1. Register or update dataset metadata
        existing = repository.get_dataset(db, dataset_meta.dataset_id)
        if not existing:
            dataset = repository.create_dataset(db, dataset_meta)
        else:
            dataset = existing
            repository.update_dataset_status(
                db,
                dataset_id=dataset.dataset_id,
                status="INGESTED" if records else "NOT_INGESTED",
                record_count=len(records),
            )

        # 2. Bulk insert normalized records
        inserted_count = repository.bulk_create_public_records(db, records)
        logger.info(f"Ingested {inserted_count} records for dataset '{dataset.dataset_id}'.")
        return dataset, inserted_count

    @staticmethod
    def get_dataset(db: Session, dataset_id: str) -> Optional[Dataset]:
        """Fetch dataset metadata by ID."""
        return repository.get_dataset(db, dataset_id)

    @staticmethod
    def list_datasets(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[Dataset], int]:
        """Fetch list of all datasets."""
        return repository.list_datasets(db, skip=skip, limit=limit)

    @staticmethod
    def list_records_for_dataset(
        db: Session,
        dataset_id: str,
        state: Optional[str] = None,
        district: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[PublicDataRecord], int]:
        """Fetch records belonging to a dataset with optional geographic/category filters."""
        return repository.list_public_records(
            db,
            dataset_id=dataset_id,
            state=state,
            district=district,
            category=category,
            skip=skip,
            limit=limit,
        )

    @classmethod
    def seed_default_datasets(cls, db: Session) -> None:
        """Seeds verified initial public datasets on startup."""
        try:
            loader = JJMWaterCoverageLoader()
            dataset_meta, _ = loader.load_and_normalize()
            existing = repository.get_dataset(db, dataset_meta.dataset_id)
            if not existing or existing.record_count == 0:
                logger.info("Auto-ingesting verified baseline dataset: JJM Rural Water Coverage")
                cls.ingest_from_loader(db, loader)
        except Exception as e:
            logger.error(f"Error during default dataset seeding: {e}", exc_info=True)
