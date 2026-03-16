from typing import List, Dict
from loguru import logger


class ContextWindowManager:
    def __init__(
        self,
        max_context_tokens: int = 6000,
        chars_per_token: float = 4.0
    ):
        self.max_context_tokens = max_context_tokens
        self.chars_per_token = chars_per_token
        self.max_context_tokens = int(max_context_tokens * chars_per_token)

    def estimate_tokens(self,text: str) -> int:
        return len(text) // int(self.chars_per_token)

    def fit_documents_in_context(self,documents: List[Dict],max_docs: int = 10,truncate_long_docs: bool = True) -> List[Dict]:
        fitted_docs = []
        current_chars = 0

        for doc in documents[:max_docs]:
            doc_text = doc.get('text','')
            doc_chars = len(doc_text)

            if current_chars + doc_chars > self.max_context_tokens:
                if truncate_long_docs:
                    remaining_chars = self.max_context_chars - current_chars
                    if remaining_chars > 200:
                        truncated_docs = doc.copy()
                        truncated_docs['text'] = doc_text[:remaining_chars]
                        truncated_docs['truncated'] = True
                        fitted_docs.append(truncated_docs)

                        fitted_docs.append(truncated_docs)
                        logger.debug(f"Truncated document to fit context: {doc.get('pmid')}")

                break

            fitted_docs.append(doc)
            current_chars += doc_chars

        logger.info(f"Fitted {len(fitted_docs)}/{len(documents)} documents in context")
        logger.debug(f"Context size: ~{self.estimate_tokens(str(fitted_docs))} tokens")
        
        return fitted_docs

    def build_efficient_context(
        self,
        documents: List[Dict],
        include_full_text: bool = False
    ) -> str:
        if include_full_text:
            return self._build_full_context(documents)
        else:
            return self._build_summary_context(documents)

    def _build_full_context(self,documents: List[Dict]) -> str:
        parts = []
        for i,doc in enumerate(documents,1):
            part = (
                f"[{i}] {doc.get('title', 'Unknown')}\n"
                f"Study: {doc.get('study_type', 'Unknown')}\n"
                f"Year: {doc.get('publication_year', 'Unknown')}\n"
                f"Content: {doc.get('text', '')}\n"
            )
            parts.append(part)

        return "\n\n".join(parts)

    def _build_summary_context(self,documents: List[Dict]) -> str:
        parts = []
        for i,doc in enumerate(documents,1):
            text = doc.get('text','')
            summary_text = text[:400] + "..." if len(text) > 400 else text

            part = (
                f"[{i}] {doc.get('title', 'Unknown')}\n"
                f"Study: {doc.get('study_type', 'Unknown')} ({doc.get('publication_year', 'N/A')})\n"
                f"Summary: {summary_text}\n"
            )
            parts.append(part)
        
        return "\n\n".join(parts)

if __name__ == "__main__":
    manager = ContextWindowManager(max_context_tokens=1000)
    
    # Sample documents
    documents = [
        {
            'pmid': '12345',
            'title': 'Study on Diabetes',
            'study_type': 'RCT',
            'publication_year': 2024,
            'text': 'A' * 2000  # Long text
        },
        {
            'pmid': '12346',
            'title': 'Metformin Efficacy',
            'study_type': 'Meta-Analysis',
            'publication_year': 2023,
            'text': 'B' * 1500
        },
        {
            'pmid': '12347',
            'title': 'Diabetes Management',
            'study_type': 'Review',
            'publication_year': 2024,
            'text': 'C' * 1000
        }
    ]
    
    print("="*70)
    print("CONTEXT WINDOW MANAGEMENT TEST")
    print("="*70)
    
    # Test fitting
    fitted = manager.fit_documents_in_context(documents, truncate_long_docs=True)
    
    print(f"\nOriginal documents: {len(documents)}")
    print(f"Fitted documents: {len(fitted)}")
    
    for doc in fitted:
        print(f"\nPMID: {doc['pmid']}")
        print(f"Text length: {len(doc['text'])} chars")
        print(f"Truncated: {doc.get('truncated', False)}")
    
    # Test context building
    context = manager.build_efficient_context(fitted, include_full_text=False)
    
    print(f"\nContext length: {len(context)} chars")
    print(f"Estimated tokens: {manager.estimate_tokens(context)}")

        