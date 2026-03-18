import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from Backend.services.embedding_service import OllamaEmbeddingService
from Backend.models.database_models import ProcessedChunk
from Backend.core.database import get_db_context
from loguru import logger
from tqdm import tqdm
import numpy as np


logger.add("logs/embeddings.log",rotation="100 MB",level="INFO")

def generate_all_embeddings(batch_size: int = 50):
    service = OllamaEmbeddingService()
    embedding_dim = service.get_embedding_dim()

    logger.info(f"Embedding dimension: {embedding_dim}")

    with get_db_context() as db:
        chunks = db.query(ProcessedChunk).filter(
            ProcessedChunk.embedded == False
        ).all()


        total = len(chunks)
        logger.info(f"Embedding {total} chunks")

        if total == 0:
            logger.info("No chunks to embed")
            return

        texts = [chunk.chunk_text for chunk in chunks]
        chunk_ids = [chunk.id for chunk in chunks]

        all_embeddings = []

        for i in tqdm(range(0,total,batch_size),desc="Embedding batches"):
            batch_texts = texts[i:i+batch_size]
            try:
                batch_embeddings = service.embed_batch(batch_texts,batch_size=2)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error embedding batch: {e}")
                all_embeddings.extend([None]*len(batch_texts))
        
        embeddings_array = np.array([emd for emd in all_embeddings if emd is not None])

        output_path = Path("data/embeddings")
        output_path.mkdir(parents=True,exist_ok=True)

        np.save(output_path / "chunk_embeddings.npy", embeddings_array)

        metadata = {
            'chunk_ids':[cid for cid,emb in zip(chunk_ids,all_embeddings) if emb is not None],
            'embedding_dim':embedding_dim,
            'total_embeddings':len(embeddings_array)
        }

        import pickle
        with open(output_path / "embeddings_metadata.pkl", 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Embeddings saved: {len(embeddings_array)} vectors")
        
        # Mark chunks as embedded
        for chunk, embedding in zip(chunks, all_embeddings):
            if embedding is not None:
                chunk.embedded = True
                chunk.embedding_model = service.model
        
        db.commit()
        
        logger.info("Database updated: chunks marked as embedded")


if __name__ == "__main__":
    generate_all_embeddings()
    
    # Verify
    print("\n" + "="*60)
    print("EMBEDDING STATISTICS")
    print("="*60)
    
    # Load and check
    try:
        embeddings = np.load("data/embeddings/chunk_embeddings.npy")
        print(f"Embeddings shape: {embeddings.shape}")
        print(f"Dimension: {embeddings.shape[1]}")
        print(f"Total vectors: {embeddings.shape[0]}")
    except (FileNotFoundError, EOFError) as e:
        print(f"Failed to load embeddings: {e}")
        print("Please ensure there are chunks to embed and the embeddings were successfully generated.")
    
    with get_db_context() as db:
        embedded_count = db.query(ProcessedChunk).filter(
            ProcessedChunk.embedded == True
        ).count()
        print(f"Database: {embedded_count} chunks marked as embedded")
                