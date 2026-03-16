import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Backend.retrieval.vector_retriever import FAISSRetriever
from Backend.models.database_models import ProcessedChunk
from Backend.core.database import get_db_context
from loguru import logger
import numpy as np
import pickle

logger.add("logs/faiss_build.log",rotation="100 MB",level="INFO")

def build_faiss_index():
    logger.info("Loading embeddings...")

    embeddings_path = Path("data/embeddings/chunk_embeddings.npy")
    metadata_path = Path("data/embeddings/embeddings_metadata.pkl")

    if not embeddings_path.exists():
        logger.error(f"Embeddings not found. run generate_embeddings.py first")
    embeddings = np.load(embeddings_path)

    with open(metadata_path,'rb') as f:
        metadata = pickle.load(f)
    
    chunk_ids = metadata['chunk_ids']
    embedding_dim = metadata['embedding_dim']

    logger.info(f"Loaded {len(embeddings)} embeddings(dim:{embedding_dim})")

    logger.info(f"Loading document metadata from database...")

    with get_db_context() as db:
        documents = []

        for chunk_id in chunk_ids:
            chunk = db.query(ProcessedChunk).get(chunk_id)

            if chunk:
                documents.append({
                    'chunk_id':chunk.id,
                    'pmid':chunk.pmid,
                    'chunk_index':chunk.chunk_index,
                    'text':chunk.chunk_text,
                    'title':chunk.title,
                    'study_type':chunk.study_type,
                    'publication_year':chunk.publication_year
                })

    logger.info(f"Loaded {len(documents)} document records")

    retriever = FAISSRetriever(embedding_dim=embedding_dim)

    retriever.build_index(
        embeddings = embeddings,
        documents = documents,
        save_path="data/embeddings/medical.faiss",
        use_gpu=False
    )

    logger.info("✅ FAISS index built successfully!")

    logger.info("Testing index...")
    
    # Test query (use first embedding as test)
    test_results = retriever.retrieve(embeddings[0], top_k=3)

    print("\n" + "="*60)
    print("FAISS INDEX TEST")
    print("="*60)
    print(f"Test query: {documents[0]['text'][:100]}...")
    print(f"\nTop 3 similar documents:")
    
    for i, result in enumerate(test_results, 1):
        print(f"\n{i}. Similarity: {result['score']:.4f}")
        print(f"   PMID: {result['pmid']}")
        print(f"   Study: {result['study_type']}")
        print(f"   Text: {result['text'][:100]}...")


if __name__ == "__main__":
    build_faiss_index()




    
