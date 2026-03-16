import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from Backend.retrieval.bm25_retrieval import BM25Retriever
from Backend.models.database_models import ProcessedChunk
from Backend.core.database import get_db_context
from loguru import logger

logger.add("logs/build_indices.log", rotation="100 MB", level="INFO")


def build_bm25_index():
    logger.info("Building BM25 index...")

    with get_db_context() as db:
        chunks = db.query(ProcessedChunk).all()

        documents = [
            {
                'chunk_id': chunk.id,
                'pmid': chunk.pmid,
                'chunk_index': chunk.chunk_index,
                'text': chunk.chunk_text,
                'title': chunk.title,
                'study_type': chunk.study_type,
                'publication_year': chunk.publication_year
            }
            for chunk in chunks
        ]

        logger.info(f"Preparing {len(documents)} documents for BM25")

        bm25 = BM25Retriever()
        bm25.build_index(documents, save_path="data/processed/bm25_index.pkl")
        
        logger.info("✅ BM25 index complete")


def main():
    """Build all indices"""
    
    print("="*70)
    print("BUILDING ALL RETRIEVAL INDICES")
    print("="*70)
    
    # Build BM25
    build_bm25_index()
    
    # Note: FAISS index already built in previous step
    # If not, run: python scripts/build_faiss_index.py
    
    print("\n" + "="*70)
    print("✅ ALL INDICES BUILT!")
    print("="*70)
    print("\nIndex locations:")
    print("• BM25: data/processed/bm25_index.pkl")
    print("• FAISS: data/embeddings/medical.faiss")
    print("\nNext steps:")
    print("• Test retrieval: python scripts/test_retrieval.py")
    print("• Move to Phase 4: LLM Integration")


if __name__ == "__main__":
    main()

