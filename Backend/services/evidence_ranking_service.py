from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import re



class EvidenceRankingService:

    def __init__(
        self,
        study_type_weight: float = 0.40,
        recency_weight: float= 0.30,
        sample_size_weight: float = 0.20,
        journal_weight: float = 0.10
    ):


        total = study_type_weight + recency_weight + sample_size_weight + journal_weight
        assert abs(total - 1.0) < 0.01, f"Weights must sum to 1.0 (got {total})"

        self.study_type_weight = study_type_weight
        self.recency_weight = recency_weight
        self.sample_size_weight = sample_size_weight
        self.journal_weight = journal_weight

        self.study_type_scores = {
            'Meta-Analysis': 1.0,
            'Systematic Review': 0.95,
            'Randomized Controlled Trial': 0.90,
            'Clinical Trial': 0.75,
            'Cohort Study': 0.60,
            'Case-Control Study': 0.50,
            'Cross-Sectional Study': 0.45,
            'Case Series': 0.30,
            'Case Report': 0.20,
            'Review': 0.40,
            'Expert Opinion': 0.15,
            'Other': 0.25
        }

        self.current_year = datetime.now().year

        logger.info(
            f"Evidence ranking initialized (type: {study_type_weight}, "
            f"recency: {recency_weight}, size: {sample_size_weight})"
        )

    def rank_documents(
        self,
        documents: List[Dict],
        normalize: bool = True
    ) -> List[Dict]:
        logger.debug(f"Ranking {len(documents)} documents by evidence quality")

        for doc in documents:
            evidence_score = self._calculate_evidence_score(doc)
            doc['evidence_score'] = evidence_score

            doc['evidence_level'] = self._determine_evidence_level(doc)

        ranked_docs = sorted(
            documents,
            key=lambda x: x.get('evidence_score', 0),
            reverse=True
        )

        if normalize and ranked_docs:
            max_score = ranked_docs[0]['evidence_score']
            min_score = ranked_docs[-1]['evidence_score']
            score_range = max_score - min_score
            
            if score_range > 0:
                for doc in ranked_docs:
                    normalized = (doc['evidence_score'] - min_score) / score_range
                    doc['evidence_score_normalized'] = normalized
        
        logger.debug(f"Top document evidence score: {ranked_docs[0]['evidence_score']:.3f}")
        
        return ranked_docs

    def _calculate_evidence_score(self,doc:Dict) -> float:
        study_type_score = self._score_study_type(doc.get('study_type','Other'))

        recency_score = self._score_recency(doc.get('publication_year'))

        sample_size_score = self._score_sample_size(doc)

        journal_score = self._score_journal(doc.get('journal',''))

        evidence_score = (
            self.study_type_weight * study_type_score +
            self.recency_weight * recency_score +
            self.sample_size_weight * sample_size_score +
            self.journal_weight * journal_score
        )
        
        return evidence_score


    def _score_study_type(self, study_type: str) -> float:
            """
            Score study type based on evidence hierarchy
            
            Returns: 0.0 to 1.0
            """
            
            return self.study_type_scores.get(study_type, 0.25)

    def _score_recency(self, publication_year: Optional[int]) -> float:
        """
        Score by recency
        
        Formula:
        - 2024: 1.0
        - 2023: 0.95
        - 2022: 0.90
        - 2021: 0.85
        - 2020: 0.80
        - <2020: Decay exponentially
        
        Why recency matters:
        - Medical guidelines update frequently
        - New treatments supersede old
        - Safety data improves over time
        """
        
        if not publication_year:
            return 0.5  # Unknown year = medium score
        
        years_old = self.current_year - publication_year
        
        if years_old < 0:
            # Future publication? Likely data error
            return 0.5
        
        if years_old == 0:
            return 1.0  # Current year
        elif years_old == 1:
            return 0.95
        elif years_old == 2:
            return 0.90
        elif years_old == 3:
            return 0.85
        elif years_old == 4:
            return 0.80
        else:
            # Exponential decay for older papers
            # After 10 years, score = 0.35
            decay_rate = 0.07
            score = max(0.35, 0.80 - (years_old - 4) * decay_rate)
            return score

    def _score_sample_size(self, doc: Dict) -> float:
        """
        Score by sample size
        
        Larger studies = more reliable
        
        Sample size categories:
        - 10,000+: 1.0 (very large)
        - 1,000-9,999: 0.9 (large)
        - 500-999: 0.8 (medium-large)
        - 100-499: 0.6 (medium)
        - 50-99: 0.4 (small)
        - <50: 0.2 (very small)
        - Unknown: 0.5 (default)
        """
        
        # Try to get sample size from metadata
        sample_size = doc.get('sample_size')
        
        # If not available, try to extract from text
        if sample_size is None:
            sample_size = self._extract_sample_size_from_text(doc.get('text', ''))
        
        if sample_size is None:
            return 0.5  # Unknown = medium score
        
        # Score based on size
        if sample_size >= 10000:
            return 1.0
        elif sample_size >= 1000:
            return 0.9
        elif sample_size >= 500:
            return 0.8
        elif sample_size >= 100:
            return 0.6
        elif sample_size >= 50:
            return 0.4
        else:
            return 0.2

    def _extract_sample_size_from_text(self, text: str) -> Optional[int]:
        """
        Extract sample size from abstract text
        
        Look for patterns:
        - "n = 500"
        - "N=500"
        - "500 patients"
        - "500 participants"
        """

        if not text:
            return None

        match = re.search(r'\b[nN]\s*=\s*(\d+)', text)

        if match:
            return int(match.group(1))

        match = re.search(r'\b(\d+)\s+(?:patients|participants|subjects|individuals)', text, re.IGNORECASE)

        if match:
            size = int(match.group(1))
            # Sanity check: typical study sizes are 10-100,000
            if 10 <= size <= 100000:
                return size

        match = re.search(r'study of (\d+)\s+(?:patients|participants)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return None


    def _score_journal(self, journal: str) -> float:
        """
        Score by journal impact
        
        High-impact journals = higher quality review process
        
        Top-tier medical journals:
        - NEJM, Lancet, JAMA, BMJ: 1.0
        - Nature Medicine, Cell: 0.95
        - Other peer-reviewed: 0.7
        - Unknown: 0.5
        
        Note: This is simplified. Production systems would use:
        - Journal Impact Factor database
        - H-index
        - Quartile rankings
        """
        
        if not journal:
            return 0.5
        
        journal_lower = journal.lower()
        
        # Top-tier
        top_tier = [
            'new england journal of medicine',
            'nejm',
            'lancet',
            'jama',
            'british medical journal',
            'bmj'
        ]
        
        if any(j in journal_lower for j in top_tier):
            return 1.0
        
        # High-tier
        high_tier = [
            'nature medicine',
            'cell',
            'science',
            'plos medicine',
            'annals of internal medicine'
        ]
        
        if any(j in journal_lower for j in high_tier):
            return 0.95
        
        # Assume peer-reviewed
        return 0.7
    

    def _determine_evidence_level(self, doc: Dict) -> str:
        """
        Determine evidence level (A, B, C)
        
        Level A (High Quality):
        - Meta-Analysis or Systematic Review of RCTs
        - Recent (≤3 years)
        - Large sample size (≥500)
        
        Level B (Moderate Quality):
        - RCTs, Clinical Trials, Cohort Studies
        - Moderately recent (≤5 years)
        - Medium sample size (≥100)
        
        Level C (Low Quality):
        - Case reports, case series, reviews
        - Older (>5 years)
        - Small sample size (<100)
        """
        
        study_type = doc.get('study_type', 'Other')
        year = doc.get('publication_year')
        sample_size = doc.get('sample_size')
        
        # Calculate years old
        years_old = self.current_year - year if year else 100
        
        # High quality criteria
        high_quality_types = ['Meta-Analysis', 'Systematic Review']
        is_high_quality_type = study_type in high_quality_types
        is_recent = years_old <= 3
        is_large_sample = sample_size and sample_size >= 500
        
        if is_high_quality_type and is_recent:
            return 'A'
        
        # Moderate quality criteria
        moderate_quality_types = [
            'Randomized Controlled Trial',
            'Clinical Trial',
            'Cohort Study'
        ]
        is_moderate_quality_type = study_type in moderate_quality_types
        is_moderately_recent = years_old <= 5
        is_medium_sample = sample_size and sample_size >= 100
        
        if is_moderate_quality_type and is_moderately_recent:
            return 'B'
        
        if is_high_quality_type or (is_moderate_quality_type and is_medium_sample):
            return 'B'
        
        # Everything else is Level C
        return 'C'

    def get_evidence_summary(self,documents: List[Dict]) -> Dict:
        if not documents:
            return {
                'total_documents': 0,
                'level_a_count': 0,
                'level_b_count': 0,
                'level_c_count': 0,
                'avg_evidence_score': 0.0
            }

        level_counts = {'A': 0, 'B': 0, 'C': 0}
        study_types = {}

        for doc in documents:
            level = doc.get('evidence_level', 'C')
            level_counts[level] = level_counts.get(level, 0) + 1

            study_type = doc.get('study_type', 'Other')
            study_types[study_type] = study_types.get(study_type, 0) + 1

            avg_score = sum(d.get('evidence_score', 0) for d in documents) / len(documents)

            return {
                'total_documents': len(documents),
                'level_a_count': level_counts['A'],
                'level_b_count': level_counts['B'],
                'level_c_count': level_counts['C'],
                'avg_evidence_score': round(avg_score, 3),
                'study_type_distribution': study_types
            }

if __name__ == "__main__":
    ranker = EvidenceRankingService()
    
    # Sample documents
    documents = [
        {
            'pmid': '12345',
            'title': 'Meta-Analysis of Diabetes Treatment',
            'study_type': 'Meta-Analysis',
            'publication_year': 2024,
            'sample_size': 5000,
            'journal': 'New England Journal of Medicine',
            'text': 'Study analyzed n = 5000 patients across 20 trials...'
        },
        {
            'pmid': '12346',
            'title': 'Case Report: Rare Diabetes Complication',
            'study_type': 'Case Report',
            'publication_year': 2015,
            'sample_size': 1,
            'journal': 'Local Medical Journal',
            'text': 'We present a case of a 45-year-old patient...'
        },
        {
            'pmid': '12347',
            'title': 'RCT: Metformin vs Placebo',
            'study_type': 'Randomized Controlled Trial',
            'publication_year': 2023,
            'sample_size': 800,
            'journal': 'Lancet',
            'text': 'We enrolled 800 participants in this double-blind trial...'
        },
        {
            'pmid': '12348',
            'title': 'Review of Diabetes Management',
            'study_type': 'Review',
            'publication_year': 2020,
            'sample_size': None,
            'journal': 'Diabetes Care',
            'text': 'This review summarizes current evidence...'
        }
    ]
    
    print("="*70)
    print("EVIDENCE RANKING TEST")
    print("="*70)
    
    # Rank documents
    ranked = ranker.rank_documents(documents, normalize=True)
    
    print(f"\nRanked {len(ranked)} documents:\n")
    
    for i, doc in enumerate(ranked, 1):
        print(f"{i}. {doc['title']}")
        print(f"   Study Type: {doc['study_type']}")
        print(f"   Year: {doc['publication_year']}")
        print(f"   Sample Size: {doc.get('sample_size', 'Unknown')}")
        print(f"   Evidence Score: {doc['evidence_score']:.3f}")
        print(f"   Evidence Level: {doc['evidence_level']}")
        print()
    
    # Evidence summary
    summary = ranker.get_evidence_summary(ranked)
    
    print("="*70)
    print("EVIDENCE SUMMARY")
    print("="*70)
    print(f"Total documents: {summary['total_documents']}")
    print(f"Level A (High): {summary['level_a_count']}")
    print(f"Level B (Moderate): {summary['level_b_count']}")
    print(f"Level C (Low): {summary['level_c_count']}")
    print(f"Average score: {summary['avg_evidence_score']:.3f}")
    print(f"\nStudy type distribution:")
    for study_type, count in summary['study_type_distribution'].items():
        print(f"  {study_type}: {count}")