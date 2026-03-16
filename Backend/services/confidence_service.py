from turtle import st
from typing import List, Dict
from loguru import logger
import re


class EnhancedConfidenceScorer:
    """
    Multi-factor confidence scoring
    
    Factors:
    1. Retrieval quality (35%) - How relevant are sources?
    2. Evidence quality (30%) - What's the study quality?
    3. Consistency (20%) - Do sources agree?
    4. Completeness (10%) - Does answer address query fully?
    5. Recency (5%) - How recent is the evidence?
    
    Output: 0.0 to 1.0 confidence score
    """

    def __init__(self):
        logger.info("Enhanced confidence scorer initialized")

    def calculate_confidence(
        self,
        query: str,
        answer: str,
        documents: List[Dict],
        evidence_summary: Dict,
        hallucination_result: Dict
    ) -> Dict:
        """
        Calculate comprehensive confidence score
        
        Returns:
            {
                'confidence': float,
                'breakdown': Dict[str, float],
                'reasoning': List[str],
                'recommendation': str
            }
        """

        retrieval_score = self._score_retrieval_quality(documents)

        evidence_score = self._score_evidence_quality(evidence_summary)
        
        consistency_score = self._score_consistency(documents)

        completeness_score = self._score_completeness(query,answer)

        recency_score = self._score_recency(documents)

        confidence = (
            0.35 * retrieval_score +
            0.30 * evidence_score +
            0.20 * consistency_score +
            0.10 * completeness_score +
            0.05 * recency_score
        )

        confidence += hallucination_result.get('confidence_adjustment', 0.0)

        confidence = max(0.0,min(1.0,confidence))

        reasoning = self._generate_reasoning(
            retrieval_score,
            evidence_score,
            consistency_score,
            completeness_score,
            recency_score,
            hallucination_result
        )

        recommendation = self._generate_recommendation(confidence)

        return {
            'confidence': round(confidence, 2),
            'breakdown': {
                'retrieval_quality': round(retrieval_score, 2),
                'evidence_quality': round(evidence_score, 2),
                'consistency': round(consistency_score, 2),
                'completeness': round(completeness_score, 2),
                'recency': round(recency_score, 2)
            },
            'reasoning': reasoning,
            'recommendation': recommendation
        }

    def _score_retrieval_quality(self,documents: List[Dict]) -> float:
        if not documents:
            return 0.0

        scores = [d.get('fused_score',0) for d in documents]
        avg_score = sum(scores)/len(scores)

        return min(avg_score,1.0)

    def _score_evidence_quality(self,evidence_summary: Dict) -> float:
        if not evidence_summary:
            return 0.5
        
        total = evidence_summary.get('total_documents',0)

        if total == 0:
            return 0.5

        level_a = evidence_summary.get('level_a_count', 0)
        level_b = evidence_summary.get('level_b_count', 0)
        level_c = evidence_summary.get('level_c_count', 0)

        score = (
            1.0 * level_a + 0.7 * level_b + 0.4 * level_c
        )/total

        return min(score,1.0)


    def _score_consistency(self,documents: List[Dict]) -> float:
        if not documents or len(documents) < 2:
            return 0.7

        study_types = [d.get('study_type','Unknown') for d in documents]

        unique_types = len(set(study_types))

        if unique_types <= 2:
            return 0.9

        elif unique_types <= 3:
            return 0.7

        else:
            return 0.5

    def _score_completeness(self,query: str,answer: str) -> float:

        if len(answer) < 100:
            return 0.5

        elif len(answer) < 200:
            return 0.7
        else:
            return 0.9

    def _score_recency(self,documents: List[Dict]) -> float:
        if not documents:
            return 0.5

        from datetime import datetime
        current_year = datetime.now().year;

        years = []
        for doc in documents:
            year = doc.get('publication_year')
            if year:
                years.append(year)

        if not years:
            return 0.5
        
        avg_year = sum(years)/len(years)
        years_old = current_year - avg_year

        if years_old <= 2:
            return 1.0

        elif years_old <= 5:
            return 0.8

        else:
            return 0.6

    def _generate_reasoning(
        self,
        retrieval: float,
        evidence: float,
        consistency: float,
        completeness: float,
        recency: float,
        hallucination: Dict
    ) -> List[str]:
        reasoning = []

        # Retrieval quality
        if retrieval >= 0.8:
            reasoning.append("✓ High retrieval relevance")
        elif retrieval >= 0.6:
            reasoning.append("• Moderate retrieval relevance")
        else:
            reasoning.append("⚠ Lower retrieval relevance")
        
        # Evidence quality
        if evidence >= 0.8:
            reasoning.append("✓ High-quality evidence (RCTs, Meta-analyses)")
        elif evidence >= 0.6:
            reasoning.append("• Mixed evidence quality")
        else:
            reasoning.append("⚠ Lower evidence quality")
        
        # Consistency
        if consistency >= 0.8:
            reasoning.append("✓ Sources are consistent")
        elif consistency >= 0.6:
            reasoning.append("• Some variation between sources")
        else:
            reasoning.append("⚠ Sources show variability")
        
        # Hallucination risk
        if hallucination.get('hallucination_risk') == 'high':
            reasoning.append("⚠ Potential hallucination detected")
        
        return reasoning

    def _generate_recommendation(self,confidence: float) -> str:

        if confidence >= 0.85:
            return "High confidence - Information appears reliable"
        elif confidence >= 0.70:
            return "Moderate confidence - Verify with healthcare provider"
        elif confidence >= 0.50:
            return "Lower confidence - Consult medical professional"
        else:
            return "Low confidence - Seek professional medical advice"

if __name__ == "__main__":
    """Test confidence scorer"""
    
    scorer = EnhancedConfidenceScorer()
    
    # Test data
    documents = [
        {
            'fused_score': 0.9,
            'study_type': 'Meta-Analysis',
            'publication_year': 2024,
            'evidence_level': 'A'
        },
        {
            'fused_score': 0.85,
            'study_type': 'Randomized Controlled Trial',
            'publication_year': 2023,
            'evidence_level': 'A'
        }
    ]
    
    evidence_summary = {
        'total_documents': 2,
        'level_a_count': 2,
        'level_b_count': 0,
        'level_c_count': 0
    }
    
    hallucination_result = {
        'hallucination_risk': 'low',
        'confidence_adjustment': 0.0
    }
    
    result = scorer.calculate_confidence(
        query="What is the first-line treatment for type 2 diabetes?",
        answer="Metformin is widely recognized as the first-line treatment...",
        documents=documents,
        evidence_summary=evidence_summary,
        hallucination_result=hallucination_result
    )
    
    print("="*70)
    print("CONFIDENCE SCORING TEST")
    print("="*70)
    print(f"\nOverall Confidence: {result['confidence']:.2%}")
    print(f"\nBreakdown:")
    for factor, score in result['breakdown'].items():
        print(f"  {factor}: {score:.2f}")
    
    print(f"\nReasoning:")
    for reason in result['reasoning']:
        print(f"  {reason}")
    
    print(f"\nRecommendation: {result['recommendation']}")


    