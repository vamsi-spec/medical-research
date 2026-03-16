from typing import List,Dict
import faiss
import numpy as np
import pickle
from pathlib import Path
from loguru import logger

class FAISSRetriever:
    def __init__(self,embedding_dim:int = 3072):
        self.embedding_dim = embedding_dim
        self.index = None
        self.documents = []

    def build_index(
        self,
        embeddings: np.ndarray,
        documents:List[Dict],
        save_path: str = "data/embeddings/medical.faiss",
        use_gpu: bool = False
    ):
        logger.info(f"Building FAISS index from {len(embeddings)} vectors")
        logger.info(f"Embedding dimension:{embeddings.shape[1]}")

        assert len(embeddings) == len(documents), "Embeddings and documents must match"
        assert embeddings.shape[1] == self.embedding_dim,f"Excepted dim{self.embedding_dim}"

        self.documents = documents

        embeddings_normalized = self._normalize(embeddings)

        self.index = faiss.IndexFlatIP(self.embedding_dim)

        if use_gpu:
            try:
                res = faiss.StandardGpuResources()
                gpu_index = faiss.index_cpu_to_gpu(res,0,self.index)
                logger.info("FAISS index moved to GPU")
            except  Exception as e:
                logger.warning(f"Failed to move index to CPU:{e}")

        self.index.add(embeddings_normalized.astype('float32'))

        logger.info(f"FAISS index built: {self.index.ntotal} vectors")

        self.save_index(save_path)

    def save_index(self,path: str):
        Path(path).parent.mkdir(parents=True,exist_ok=True)

        faiss.write_index(faiss.index_gpu_to_cpu(self.index) if hasattr(self.index,'getDevice') else self.index,path)

        metadata_path = path.replace(".faiss","_metadata.pkl")
        with open(metadata_path,'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'embedding_dim':self.embedding_dim
            },f)

        logger.info(f"Index saved:{path}")
    
    def load_index(self,path: str):
        self.index = faiss.read_index(path)
        metadata_path = path.replace('.faiss','_metadata.pkl')
        with open(metadata_path,'rb') as f:
            metadata = pickle.load(f)
        self.documents = metadata['documents']
        self.embedding_dim = metadata['embedding_dim']
        logger.info(f"Index loaded:{path}({self.index.ntotal} vectors)")

    def retrieve(
        self,query_embedding: np.ndarray,top_k: int = 10
    ) -> List[Dict]:
        if not self.index:
            raise ValueError("FAISS index not built or loaded")

        query_vector = query_embedding.reshape(1,-1)

        query_normalized = self._normalize(query_vector)

        scores, indices = self.index.search(query_normalized.astype('float32'),top_k)

        results = []
        for score, idx in zip(scores[0],indices[0]):
            if idx < len(self.documents):
                results.append({
                    **self.documents[idx],
                    'score':float(score),
                    'retrieval_method':'faiss'
                
                })
        return results
    
    def _normalize(self,embeddings: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(embeddings,axis=1,keepdims=True)
        norms = np.where(norms == 0, 1,norms)
        return embeddings / norms

if __name__ == "__main__":
    # Sample data
    np.random.seed(42)
    
    # Generate sample embeddings (100 docs, 128 dims)
    n_docs = 100
    embedding_dim = 128
    embeddings = np.random.randn(n_docs, embedding_dim).astype('float32')
    
    # Sample documents
    documents = [
        {
            'pmid': f'PMID{i}',
            'chunk_index': 0,
            'text': f'Document {i} about medical topic',
            'study_type': 'Review'
        }
        for i in range(n_docs)
    ]
    
    # Build index
    retriever = FAISSRetriever(embedding_dim=embedding_dim)
    retriever.build_index(embeddings, documents, save_path="test_faiss.faiss")
    
    # Test retrieval
    query_embedding = np.random.randn(embedding_dim).astype('float32')
    results = retriever.retrieve(query_embedding, top_k=5)
    
    print(f"Query embedding shape: {query_embedding.shape}")
    print(f"\nTop 5 results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.4f}")
        print(f"   PMID: {result['pmid']}")
        print(f"   Text: {result['text']}")    