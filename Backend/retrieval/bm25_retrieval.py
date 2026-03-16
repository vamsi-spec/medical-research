from typing import List,Dict
from rank_bm25 import BM25Okapi
import pickle
from pathlib import Path
from loguru import logger
import numpy as np
import re


class BM25Retriever:
    def __init__(self):
        self.bm25 = None
        self.documents = []
        self.corpus_tokens = []

    def build_index(
        self,documents: List[Dict[str,str]],
        save_path: str = "data/processed/bm25_index.pkl"
    ):

        logger.info(f"Building BM25 index from {len(documents)} documents")

        self.documents = documents
        self.corpus_tokens = [self._tokenize(doc['text']) for doc in documents]

        self.bm25 = BM25Okapi(self.corpus_tokens)

        self.save_index(save_path)

        logger.info(f"BM25 index saved to {save_path}")

    def save_index(self,path: str):
        Path(path).parent.mkdir(parents=True,exist_ok=True)

        with open(path,'wb') as f:
            pickle.dump({
                'bm25': self.bm25,
                'documents': self.documents,
                'corpus_tokens': self.corpus_tokens
            },f)

        logger.info(f"Index Saved: {path}")

    def load_index(self,path: str):
        with open(path,'rb') as f:
            data = pickle.load(f)

        self.bm25 = data['bm25']
        self.documents = data['documents']
        self.corpus_tokens = data['corpus_tokens']

        logger.info(f"Index loaded: {path} ({len(self.documents)} docs)")

    def retrieve(
        self,query: str,top_k: int = 10
    )-> List[Dict]:

        if not self.bm25:
            raise ValueError("BM25 Index not loaded") 

        query_tokens = self._tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                **self.documents[idx],
                'score':float(scores[idx]),
                'retrieval_method':'bm25'
            })
        return results

    def _tokenize(self,text: str):
        # Remove punctuation and split by whitespace
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = text.split()

        tokens = [t for t in tokens if len(t) > 1 or t in ['a','i']]

        return tokens
    
if __name__ == "__main__":
    # Sample documents
    documents = [
        {
            'pmid': '12345',
            'chunk_index': 0,
            'text': 'Metformin is used for treating type 2 diabetes mellitus.',
            'study_type': 'Review'
        },
        {
            'pmid': '12346',
            'chunk_index': 0,
            'text': 'Insulin therapy is essential for type 1 diabetes management.',
            'study_type': 'Clinical Trial'
        },
        {
            'pmid': '12347',
            'chunk_index': 0,
            'text': 'Hypertension treatment includes lifestyle modifications and medications.',
            'study_type': 'Systematic Review'
        },
    ]
    
    # Build index
    retriever = BM25Retriever()
    retriever.build_index(documents, save_path="test_bm25.pkl")
    
    # Test retrieval
    query = "diabetes treatment metformin"
    results = retriever.retrieve(query, top_k=3)
    
    print(f"\nQuery: {query}")
    print(f"Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.4f}")
        print(f"   PMID: {result['pmid']}")
        print(f"   Text: {result['text'][:60]}...")
