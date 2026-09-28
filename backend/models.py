import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.database import Base

class CitizenRequest(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reference_id = Column(String(32), unique=True, index=True, nullable=False)
    citizen_request = Column(Text, nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    locality = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    affected_households = Column(Integer, nullable=True)
    status = Column(String(50), default="RECEIVED", nullable=False)
    
    # Phase 2 Step 2: Gemini Structured AI Extraction Fields
    ai_extraction_status = Column(String(30), default="NOT_PROCESSED", nullable=False)
    language = Column(String(50), nullable=True)
    problem_summary = Column(Text, nullable=True)
    severity = Column(String(20), nullable=True)
    affected_group = Column(String(200), nullable=True)
    location_hint = Column(String(200), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )
