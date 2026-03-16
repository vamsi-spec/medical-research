import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Backend.services.embedding_service import OllamaEmbeddingService
from Backend.retrieval.bm25_retrieval import BM25Retriever
from Backend.retrieval.vector_retriever import FAISSRetriever
from Backend.retrieval.hybrid_retriever import HybridRetriever
from Backend.utils.evaluation import RetrievalEvaluator
from loguru import logger

def test_retrieval_methods():
    print("="*70)
    print("RETRIEVAL METHODS TEST")
    print("="*70)

    print("\nLoading retrievers...")

    bm25 = BM25Retriever()
    bm25.load_index("data/processed/bm25_index.pkl")

    faiss = FAISSRetriever()
    faiss.load_index("data/embeddings/medical.faiss")

    embedding_service = OllamaEmbeddingService()

    hybrid = HybridRetriever(
        bm25_retriever=bm25,
        faiss_retriever=faiss,
        embedding_service=embedding_service,
        bm25_weight=0.4,
        faiss_weight=0.6
    )

    print("✅ All retrievers loaded")

    test_queries = [
        # Exact term query (should favor BM25)
        {
            'query': 'metformin dosage type 2 diabetes',
            'description': 'Exact medical term query'
        },
        
        # Semantic query (should favor FAISS)
        {
            'query': 'medication for high blood sugar',
            'description': 'Semantic query (synonyms)'
        },
        
        # Mixed query (hybrid should win)
        {
            'query': 'latest treatments for cardiovascular disease prevention',
            'description': 'Mixed semantic + recent focus'
        },
    ]
    
    # Run comparisons
    for test in test_queries:
        query = test['query']
        description = test['description']
        
        print("\n" + "="*70)
        print(f"Query: {query}")
        print(f"Type: {description}")
        print("="*70)
        
        # BM25 retrieval
        print("\n[BM25 Results]")
        bm25_results = bm25.retrieve(query, top_k=3)
        for i, result in enumerate(bm25_results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   {result['text'][:100]}...")
        
        # FAISS retrieval
        print("\n[FAISS Results]")
        query_embedding = embedding_service.embed_text(query)
        faiss_results = faiss.retrieve(query_embedding, top_k=3)
        for i, result in enumerate(faiss_results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   {result['text'][:100]}...")
        
        # Hybrid retrieval
        print("\n[Hybrid Results]")
        hybrid_results = hybrid.retrieve(query, top_k=3, fusion_method="weighted")
        for i, result in enumerate(hybrid_results, 1):
            print(f"{i}. Fused: {result['fused_score']:.4f} (BM25: {result.get('bm25_score', 0):.4f}, FAISS: {result.get('faiss_score', 0):.4f})")
            print(f"   {result['text'][:100]}...")
    
    print("\n" + "="*70)
    print("KEY OBSERVATIONS:")
    print("="*70)
    print("• BM25: Best for exact medical terms (metformin, ICD codes)")
    print("• FAISS: Best for semantic queries (synonyms, concepts)")
    print("• Hybrid: Best overall (combines strengths)")
    print("• Fusion weights can be tuned per use case")


if __name__ == "__main__":
    test_retrieval_methods()