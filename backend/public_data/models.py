import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    dataset_id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_name = Column(String(200), nullable=False)
    source_url = Column(String(500), nullable=True)
    publisher = Column(String(200), nullable=True)
    data_type = Column(String(100), nullable=False)
    geographic_scope = Column(String(100), nullable=False)
    last_updated = Column(String(50), nullable=True)
    license = Column(String(200), nullable=False)
    ingestion_status = Column(String(30), default="NOT_INGESTED", nullable=False)
    record_count = Column(Integer, default=0, nullable=False)
    ingested_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )

    records = relationship("PublicDataRecord", back_populates="dataset", cascade="all, delete-orphan")


class PublicDataRecord(Base):
    __tablename__ = "public_data_records"

    record_id = Column(String(100), primary_key=True, index=True)
    dataset_id = Column(String(100), ForeignKey("datasets.dataset_id"), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    locality = Column(String(150), nullable=True)
    category = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(150), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    period = Column(String(50), nullable=True)
    geographic_level = Column(String(50), default="District", nullable=False)
    source_reference = Column(String(150), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    dataset = relationship("Dataset", back_populates="records")
