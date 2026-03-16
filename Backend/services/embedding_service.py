from typing import List
from langchain_ollama import OllamaEmbeddings
from loguru import logger
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv("config/.env")

class OllamaEmbeddingService:
    def __init__(
        self,
        model:str = None,
        base_url: str = None
    ):
        self.model = model or os.getenv("OLLAMA_EMBEDDING_MODEL", "llama3.2")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        logger.info(f"Initializing ollama embeddings (model:{self.model})")

        self.embeddings = OllamaEmbeddings(
            model=self.model,
            base_url=self.base_url
        )

        self._test_connection()

    def _test_connection(self):
        try:
            test_embedding = self.embeddings.embed_query("test")
            logger.info(f"Ollama connected(embedding dim:{len(test_embedding)})")
        except Exception as e:
            logger.error(f"Ollama connection failed:{e}")
            raise

    def embed_text(self,text:str) -> List[float]:
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise

    def embed_batch(self,texts: List[str],batch_size: int = 10)->List[List[float]]:
        all_embeddings = []
        total = len(texts)

        logger.info(f"Embedding {total} texts in batches of {batch_size}")

        for i in range(0,total,batch_size):
            batch = texts[i:i+batch_size]
            try:
                batch_embeddings = self.embeddings.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)

                if(i + batch_size) % 100 == 0:
                    logger.info(f"Embedded{min(i+batch_size,total)}/{total} texts")
            except Exception as e:
                logger.error(f"Error embedding batch: {e}")
                all_embeddings.extend([None] * len(batch))
                continue

        logger.info(f"Embeddings complete:{len(all_embeddings)}/{total} successfull")
        return all_embeddings
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension"""
        test_embedding = self.embed_text("test")
        return len(test_embedding)


# Test embedding service
if __name__ == "__main__":
    service = OllamaEmbeddingService()
    
    # Test single embedding
    text = "Diabetes is a chronic metabolic disease."
    embedding = service.embed_text(text)
    
    print(f"Text: {text}")
    print(f"Embedding dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    
    # Test batch embedding
    texts = [
        "Type 2 diabetes treatment",
        "Hypertension management",
        "Cancer immunotherapy"
    ]
    
    embeddings = service.embed_batch(texts, batch_size=2)
    print(f"\nBatch embedding: {len(embeddings)} embeddings generated")
    
    # Test similarity
    emb1 = np.array(embeddings[0])
    emb2 = np.array(embeddings[1])
    emb3 = np.array(embeddings[2])
    
    # Cosine similarity
    sim_12 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    sim_13 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
    
    print(f"\nSimilarity scores:")
    print(f"Diabetes <-> Hypertension: {sim_12:.4f}")
    print(f"Diabetes <-> Cancer: {sim_13:.4f}")
    print(f"(Higher = more similar)")