import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Backend.retrieval.bm25_retrieval import BM25Retriever
from Backend.retrieval.vector_retriever import FAISSRetriever
from Backend.retrieval.hybrid_retriever import HybridRetriever
from Backend.services.embedding_service import OllamaEmbeddingService
from Backend.services.llm_service import OllamaLLMService
from Backend.services.rag_service import RAGService
from loguru import logger

def test_rag_pipeline():
    print("="*70)
    print("RAG PIPELINE TEST")
    print("="*70)

    print("\n loading components")

    bm25 = BM25Retriever()
    bm25.load_index("data/processed/bm25_index.pkl")

    faiss = FAISSRetriever()
    faiss.load_index("data/embeddings/medical.faiss")

    embedding_service = OllamaEmbeddingService()

    hybrid = HybridRetriever(
        bm25_retriever=bm25,
        faiss_retriever=faiss,
        embedding_service=embedding_service
    )

    llm_service = OllamaLLMService()
    rag_service = RAGService(
        retriever=hybrid,
        llm_service=llm_service,
        top_k=5
    )
    print("All components loaded\n")

    test_queries = [
        "What is the first-line treatment for type 2 diabetes?",
        "What are the side effects of metformin?",
        "How effective is insulin therapy for diabetes management?",
    ]

    for i, query in enumerate(test_queries, 1):
        print("\n" + "="*70)
        print(f"TEST {i}/3")
        print("="*70)
        print(f"Query: {query}\n")
        
        # Get answer
        result = rag_service.answer_query(query, top_k=5)
        
        # Display answer
        print("ANSWER:")
        print("-"*70)
        print(result['answer'])
        print("-"*70)
        
        # Display citations
        print(f"\nCITATIONS ({len(result['citations'])} sources):")
        print("-"*70)
        for citation in result['citations']:
            from Backend.services.citation_service import CitationExtractor
            extractor = CitationExtractor()
            formatted = extractor.format_citation_text(citation)
            print(formatted)
        
        # Display confidence
        print(f"\nCONFIDENCE: {result['confidence']:.2%}")
        
        # Display disclaimer
        print(f"\n{result['disclaimer']}")
        
        print("\n")
    
    print("="*70)
    print("✅ RAG PIPELINE TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_rag_pipeline()