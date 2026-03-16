from typing import List, Dict, Optional
from Backend.retrieval.bm25_retrieval import BM25Retriever
from Backend.retrieval.vector_retriever import FAISSRetriever
from Backend.services.embedding_service import OllamaEmbeddingService
from loguru import logger
import numpy as np

class HybridRetriever:
    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        faiss_retriever: FAISSRetriever,
        embedding_service: OllamaEmbeddingService,
        bm25_weight: float = 0.4,
        faiss_weight: float = 0.6
    ):
        self.bm25_retriever = bm25_retriever
        self.faiss_retriever = faiss_retriever
        self.embedding_service = embedding_service

        self.bm25_weight = bm25_weight
        self.faiss_weight = faiss_weight

        assert abs(bm25_weight + faiss_weight - 1.0) < 0.01, "Weights must sum to 1.0"

        logger.info(f"Hybrid retriever initialized with BM25 weight: {bm25_weight}, FAISS weight: {faiss_weight}")

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        bm25_top_k: Optional[int] = None,
        faiss_top_k: Optional[int] = None,
        fusion_method: str = "weighted"
    ) -> List[Dict]:
        bm25_k = bm25_top_k or (top_k * 2)
        faiss_k = faiss_top_k or (top_k * 2)

        logger.debug(f"BM25 retrieval:{query}")
        bm25_results = self.bm25_retriever.retrieve(query,top_k = bm25_k)

        logger.debug(f"FAISS retrieval...")
        query_embedding = np.array(self.embedding_service.embed_text(query))

        faiss_results = self.faiss_retriever.retrieve(query_embedding,top_k = faiss_k)

        if fusion_method == "weighted":
            fused_results = self._weighted_fusion(bm25_results,faiss_results)
        elif fusion_method == "rrf":
            fused_results = self._rrf_fusion(bm25_results,faiss_results)
        else:
            raise ValueError(f"Invalid fusion method: {fusion_method}")

        return fused_results[:top_k]


    def _weighted_fusion(self,bm25_results: List[Dict],faiss_results: List[Dict]) -> List[Dict]:
        bm25_results = self._normalize_bm25_scores(bm25_results)

        doc_scores = {}

        for result in bm25_results:
            doc_id = f"{result['pmid']}_{result['chunk_index']}"
            doc_scores[doc_id] = {
                'bm25':result['score'],
                'faiss':0.0,
                'doc':result
            }

        for result in faiss_results:
            doc_id = f"{result['pmid']}_{result['chunk_index']}"
            if doc_id in doc_scores:
                doc_scores[doc_id]['faiss'] = result['score']
            else:
                doc_scores[doc_id] = {
                    'bm25':0.0,
                    'faiss':result['score'],
                    'doc':result
                }

        fused_results = []

        for doc_id,scores in doc_scores.items():
            fused_score = (
                self.bm25_weight * scores['bm25'] +
                self.faiss_weight * scores['faiss']
            )

            result = scores['doc'].copy()
            result['fused_score'] = fused_score
            result['bm25_score'] = scores['bm25']
            result['faiss_score'] = scores['faiss']
            result['retrieval_method'] = 'hybrid'
            
            fused_results.append(result)
        
        return fused_results

    def _rrf_fusion(
        self,
        bm25_results: List[Dict],
        faiss_results: List[Dict],
        k: int = 60
    ) -> List[Dict]:
        doc_scores = {}

        for rank,result in enumerate(bm25_results,start=1):
            doc_id = f"{result['pmid']}_{result['chunk_index']}"
            rrf_score = 1.0 / (k+rank)

            doc_scores[doc_id] = {
                'rrf_score':rrf_score,
                'doc':result
            }

        for rank,result in enumerate(faiss_results,start=1):
            doc_id = f"{result['pmid']}_{result['chunk_index']}"
            rrf_score = 1.0 / (k+rank)

            if doc_id in doc_scores:
                doc_scores[doc_id]['rrf_score'] += rrf_score
            else:
                doc_scores[doc_id] = {
                    'rrf_score':rrf_score,
                    'doc':result
                }
        fused_results = []

        for doc_id,data in doc_scores.items():
            result = data['doc'].copy()
            result['rrf_score'] = data['rrf_score']
            result['retrieval_method'] = 'hybrid_rrf'
            fused_results.append(result)

        return fused_results

    def _normalize_bm25_scores(self,results: List[Dict]) -> List[Dict]:
        if not results:
            return results

        scores = [r['score'] for r in results]
        min_score = min(scores)
        max_score = max(scores)

        score_range = max_score - min_score
        if score_range == 0:
            score_range = 1.0

        for result in results:
            result['score'] = (result['score'] - min_score) / score_range

        return results

if __name__ == "__main__":
    # This is a conceptual test
    # In practice, load actual indices
    
    print("Hybrid Retriever Test")
    print("="*60)
    print("\nHybrid retrieval combines:")
    print("1. BM25 (keyword matching)")
    print("2. FAISS (semantic similarity)")
    print("\nFusion strategies:")
    print("- Weighted: Combine normalized scores")
    print("- RRF: Combine ranks (score-independent)")
    print("\nWeights (default):")
    print("- BM25: 0.4 (exact terms)")
    print("- FAISS: 0.6 (semantic meaning)")
    print("\nBest for:")
    print("✓ Medical queries (need both exact terms and semantics)")
    print("✓ Handles synonyms (semantic)")
    print("✓ Handles exact codes/drugs (keyword)")
