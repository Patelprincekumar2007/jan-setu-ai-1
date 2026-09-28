import argparse
import logging
from backend.database import SessionLocal
import backend.public_data.models  # Ensure SQLAlchemy sees Dataset model
from backend.knowledge.vector_index import build_vector_index, VectorIndexUnavailableException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nagriklens.knowledge.indexer")

def main():
    parser = argparse.ArgumentParser(description="NagrikLens AI Vector Indexer")
    parser.add_argument(
        "--dataset",
        type=str,
        help="Optional dataset ID to filter which evidence to index.",
        default=None,
    )
    args = parser.parse_args()

    logger.info("Connecting to database...")
    db = SessionLocal()
    try:
        logger.info("Building vector index...")
        summary = build_vector_index(db=db, dataset_id=args.dataset)
        
        print("\n=== Vector Index Build Summary ===")
        print(f"Status:          {summary['status']}")
        print(f"Embedding model: {summary['embedding_model']}")
        print(f"Evidence count:  {summary['evidence_count']}")
        print(f"Dimension:       {summary['dimension']}")
        print(f"Index path:      {summary['index_path']}")
        print("==================================\n")
        
    except ValueError as e:
        logger.error(f"Failed to build index: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
