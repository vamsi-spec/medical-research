from functools import lru_cache
from loguru import logger

from Backend.retrieval.bm25_retrieval import BM25Retriever
from Backend.retrieval.vector_retriever import FAISSRetriever
from Backend.retrieval.hybrid_retriever import HybridRetriever
from Backend.services import embedding_service
from Backend.services import llm_service
from Backend.services.embedding_service import OllamaEmbeddingService
from Backend.services.llm_service import OllamaLLMService
from Backend.services.safe_rag_service import SafeRagService
from Backend.tools.drug_interaction import RealDrugInteractionChecker
from Backend.tools.clinical_trials import EnhancedClinicalTrialsSearcher
from Backend.tools.medical_codes import RealMedicalCodeLookup


_rag_service = None
_drug_checker = None
_trials_searcher = None
_code_lookup = None

def get_rag_service() -> SafeRagService:
    global _rag_service
    if _rag_service is None:
        logger.info("Initializing RAG service")
        
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

        _rag_service = SafeRagService(
            retriever=hybrid,
            llm_service=llm_service,
            top_k=5,
            use_evidence_ranking=True,
            min_confidence_threshold=0.0        
        )

        logger.info("RAG service initialized")

    return _rag_service

def get_drug_checker() -> RealDrugInteractionChecker:
    global _drug_checker

    if _drug_checker is None:
        logger.info("Initializing drug checker...")
        _drug_checker = RealDrugInteractionChecker()
        logger.info("Drug checker initialized")

    return _drug_checker

def get_trials_searcher() -> EnhancedClinicalTrialsSearcher:
    """Get clinical trials searcher singleton"""
    global _trials_searcher
    
    if _trials_searcher is None:
        logger.info("Initializing clinical trials searcher...")
        _trials_searcher = EnhancedClinicalTrialsSearcher()
        logger.info("✅ Trials searcher initialized")
    
    return _trials_searcher

def get_code_lookup() -> RealMedicalCodeLookup:
    """Get medical code lookup singleton"""
    global _code_lookup
    
    if _code_lookup is None:
        logger.info("Initializing medical code lookup...")
        _code_lookup = RealMedicalCodeLookup()
        logger.info("✅ Code lookup initialized")
    
    return _code_lookup
