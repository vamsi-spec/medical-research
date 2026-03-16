from typing import List, Dict, Set
import numpy as np
from loguru import logger


class RetrievalEvaluator:
    def __init__(self):
        pass
    
    def precision_at_k(
        self,
        retrieved: List[str],
        relevant: List[str],
        k : int = 10
    ) -> float:
        top_k = retrieved[:k]
        relevant_in_k = sum(1 for doc_id in top_k if doc_id in relevant)

        return relevant_in_k / k if k > 0 else 0.0

    def recall_at_k(
        self,
        retrieved: List[str],
        relevant: Set[str],
        k: int = 10
    ) -> float:
        if not relevant:
            return 0.0
        top_k = retrieved[:k]
        relevant_in_k = sum(1 for doc_id in top_k if doc_id in relevant)

        return relevant_in_k / len(relevant)
    
    def mrr(
        self,
        retrieved: List[str],
        relevant: Set[str]
    ) -> float:
        for rank,doc_id in enumerate(retrieved,start=1):
            if doc_id in relevant:
                return 1.0 / rank
        return 0.0

    def ndcg_at_k(
        self,
        retrieved: List[str],
        relevant: Dict[str,float],
        k: int = 10
    ) -> float:
        top_k = retrieved[:k]

        dcg = 0.0
        for rank,doc_id in enumerate(top_k,start=1):
            relevance = relevant.get(doc_id,0.0)
            dcg += relevance / np.log2(rank + 1)

        sorted_relevance = sorted(relevant.values(),reverse=True)[:k]
        idcg = sum(rel / np.log2(rank + 1) for rank, rel in enumerate(sorted_relevance,start=1))

        return dcg / idcg if idcg > 0 else 0.0

    def evaluate_retrieval(
        self,
        queries: List[Dict],
        retriever,
        k_values: List[int] = [1,3,5,10]
    ) -> Dict:
        results = {
            'precision': {k: [] for k in k_values},
            'recall': {k: [] for k in k_values},
            'mrr': []
        }

        for query_data in queries:
            query = query_data['query']
            relevant = query_data['relevant']

            retrieved_docs = retriever.retrieve(query,top_k = max(k_values))
            retrieved_ids = [f"{d['pmid']}_{d['chunk_index']}" for d in retrieved_docs]

            for k in k_values:
                precision = self.precision_at_k(retrieved_ids,relevant,k)
                recall = self.recall_at_k(retrieved_ids,relevant,k)
                results['precision'][k].append(precision)
                results['recall'][k].append(recall)
            
            mrr = self.mrr(retrieved_ids,relevant)
            results['mrr'].append(mrr)

        averaged = {
            'precision': {k: np.mean(values) for k,values in results['precision'].items()},
            'recall':{k: np.mean(values) for k,values in results['recall'].items()},
            'mrr': np.mean(results['mrr'])
        }

        return averaged

if __name__ == "__main__":
    evaluator = RetrievalEvaluator()
    
    # Test data
    retrieved = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    relevant = {'A', 'D', 'E', 'K', 'L'}
    
    print("Evaluation Metrics Test")
    print("="*60)
    print(f"Retrieved: {retrieved[:10]}")
    print(f"Relevant: {relevant}")
    
    # Precision@K
    for k in [1, 3, 5, 10]:
        precision = evaluator.precision_at_k(retrieved, relevant, k=k)
        print(f"\nPrecision@{k}: {precision:.3f}")
    
    # Recall@K
    for k in [1, 3, 5, 10]:
        recall = evaluator.recall_at_k(retrieved, relevant, k=k)
        print(f"Recall@{k}: {recall:.3f}")
    
    # MRR
    mrr = evaluator.mrr(retrieved, relevant)
    print(f"\nMRR: {mrr:.3f}")
    
    print("\n" + "="*60)
    print("Interpretation:")
    print("- Precision@10 = 0.3: 30% of top 10 are relevant")
    print("- Recall@10 = 0.6: Found 60% of all relevant docs")
    print("- MRR = 1.0: First result is relevant")