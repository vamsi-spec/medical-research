import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from Backend.retrieval.bm25_retrieval import BM25Retriever
from Backend.retrieval.vector_retriever import FAISSRetriever
from Backend.retrieval.hybrid_retriever import HybridRetriever
from Backend.services.embedding_service import OllamaEmbeddingService
from Backend.services.llm_service import OllamaLLMService
from Backend.services.rag_service import RAGService

def test_evidence_ranking():
    print("="*70)
    print("EVIDENCE RANKING INTEGRATION TEST")
    print("="*70)

    print("\n📦 Loading components...")

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
        top_k=5,
        use_evidence_ranking=True
    )

    print("✅ All components loaded\n")
    
    # Test query
    query = "What is the most effective first-line treatment for type 2 diabetes?"

    print("="*70)
    print(f"Query: {query}")
    print("="*70)

    result = rag_service.answer_query(query)

    print("\nANSWER:")
    print("-"*70)
    print(result['answer'])
    print("-"*70)

    print(f"\nCITATIONS (Evidence-Ranked):")
    print("-"*70)

    for citation in result['citations']:
        # Get evidence level
        evidence_level = citation.get('evidence_level', 'C')
        evidence_marker = {
            'A': '🟢',
            'B': '🟡',
            'C': '🔴'
        }.get(evidence_level, '⚪')
        
        print(f"{evidence_marker} Level {evidence_level} - [{citation['index']}] {citation['title']}")
        print(f"   Study: {citation['study_type']} ({citation['publication_year']})")
        print(f"   PMID: {citation['pmid']}")
        
        # Show evidence score if available
        if 'evidence_score' in citation:
            print(f"   Evidence Score: {citation['evidence_score']:.3f}")
        
        print()
    
    # Display evidence summary
    if result.get('evidence_summary'):
        summary = result['evidence_summary']
        
        print("="*70)
        print("EVIDENCE QUALITY SUMMARY")
        print("="*70)
        print(f"Total Sources: {summary['total_documents']}")
        print(f"🟢 Level A (High Quality): {summary['level_a_count']}")
        print(f"🟡 Level B (Moderate Quality): {summary['level_b_count']}")
        print(f"🔴 Level C (Low Quality): {summary['level_c_count']}")
        print(f"Average Evidence Score: {summary['avg_evidence_score']:.3f}")
        
        print(f"\nStudy Type Distribution:")
        for study_type, count in summary['study_type_distribution'].items():
            print(f"  • {study_type}: {count}")
    
    # Display confidence
    print(f"\nOVERALL CONFIDENCE: {result['confidence']:.2%}")
    
    # Display disclaimer
    print(f"\n{result['disclaimer']}")
    
    print("\n" + "="*70)
    print("KEY INSIGHTS:")
    print("="*70)
    print("✓ Citations ranked by evidence quality (not just relevance)")
    print("✓ High-quality studies (Meta-Analyses, RCTs) prioritized")
    print("✓ Recent research weighted higher")
    print("✓ Confidence score considers evidence quality")
    print("✓ Evidence levels help users assess source reliability")


if __name__ == "__main__":
    test_evidence_ranking()