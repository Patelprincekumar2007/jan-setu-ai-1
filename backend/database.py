from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency yield for database session with automatic lifecycle cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables and ensure all model columns exist."""
    import backend.models  # Ensure citizen request models are imported
    import backend.public_data.models  # Ensure public dataset models are imported
    import backend.knowledge.models  # Ensure knowledge models are imported
    Base.metadata.create_all(bind=engine)

    # Lightweight column migration check for SQLite development
    if settings.database_url.startswith("sqlite"):
        with engine.connect() as conn:
            cursor = conn.execute(text("PRAGMA table_info(requests)"))
            columns = [row[1] for row in cursor.fetchall()]
            
            new_columns = {
                "ai_extraction_status": "VARCHAR(30) DEFAULT 'NOT_PROCESSED' NOT NULL",
                "language": "VARCHAR(50)",
                "problem_summary": "TEXT",
                "severity": "VARCHAR(20)",
                "affected_group": "VARCHAR(200)",
                "location_hint": "VARCHAR(200)",
            }
            
            for col_name, col_type in new_columns.items():
                if col_name not in columns:
                    conn.execute(text(f"ALTER TABLE requests ADD COLUMN {col_name} {col_type}"))
            conn.commit()
