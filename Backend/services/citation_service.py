import enum
from turtle import title
from typing import List, Dict, Set
from loguru import logger
import re


class CitationExtractor:
    def __init__(self):
        pass

    def extract_citations(
        self,
        documents: List[Dict],
        max_citations: int = 10
    ) -> List[Dict]:
        citations = []
        seen_pmids = set()

        for i,doc in enumerate(documents[:max_citations],start = 1):
            pmid = doc.get('pmid','Unknown')

            if pmid in seen_pmids:
                continue
            seen_pmids.add(pmid)

            citation = {
                'index': i,
                'pmid': pmid,
                'title': doc.get('title', 'Unknown Title'),
                'study_type': doc.get('study_type', 'Unknown'),
                'publication_year': doc.get('publication_year', 'Unknown'),
                'score': doc.get('score', 0.0),
                'text_snippet': doc.get('text', '')[:200] + '...'
            }

            citations.append(citation)
        
        return citations

    def format_citation_text(self,citation: Dict) -> str:
        formatted = (
            f"[{citation['index']}] {citation['title']} "
            f"({citation['study_type']}, {citation['publication_year']}). "
            f"PMID: {citation['pmid']}"
        )

        return formatted

    def build_citation_context(
        self,
        documents: List[Dict],
        include_full_text: bool = False
    ) -> str:
        context_parts = []

        for i,doc in enumerate(documents,start=1):
            part = f"[{i}] {doc.get('title', 'Unknown')}\n"
            part += f"Study Type: {doc.get('study_type', 'Unknown')}\n"
            part += f"Year: {doc.get('publication_year', 'Unknown')}\n"

            text = doc.get('text','')
            if include_full_text:
                part += f"Content:{text}\n"
            else:
                part += f"Content:{text[:500]}...\n"
            context_parts.append(part)
        return "\n\n".join(context_parts)

    def inject_citation_markers(
        self,
        answer: str,
        documents: List[Dict]
    ) -> str:
        """
        Inject citation markers into answer
        
        Look for claims that match document content
        Add [1], [2], etc. markers
        
        Simple heuristic approach (can be improved with NLP)
        """
        
        # For now, return answer as-is
        # Advanced: Use sentence matching to auto-inject citations
        # This would require sentence embeddings + similarity matching
        
        return answer

    def validate_citations(
        self,
        answer: str,
        max_citations_index: int 
    ):
        markers = re.findall(r'\[(\d+)\]', answer)

        for marker in markers:
            index = int(marker)
            if index > max_citations_index:
                logger.error(f"Invalid citation marker:{marker} max:{max_citations_index}")
                return False
        return True

if __name__ == "__main__":
    extractor = CitationExtractor()
    
    # Sample documents
    documents = [
        {
            'pmid': '38234567',
            'title': 'Metformin efficacy in Type 2 Diabetes',
            'study_type': 'Randomized Controlled Trial',
            'publication_year': 2024,
            'text': 'Background: Type 2 diabetes affects millions. Metformin is first-line treatment...',
            'score': 0.95
        },
        {
            'pmid': '38234568',
            'title': 'Comparative effectiveness of diabetes medications',
            'study_type': 'Meta-Analysis',
            'publication_year': 2023,
            'text': 'We analyzed 50 studies comparing various diabetes medications...',
            'score': 0.87
        }
    ]
    
    # Extract citations
    citations = extractor.extract_citations(documents)
    
    print("="*70)
    print("CITATION EXTRACTION TEST")
    print("="*70)
    
    print("\nExtracted Citations:")
    for citation in citations:
        formatted = extractor.format_citation_text(citation)
        print(f"\n{formatted}")
    
    # Build context
    context = extractor.build_citation_context(documents)
    print("\n" + "="*70)
    print("CONTEXT FOR LLM:")
    print("="*70)
    print(context)