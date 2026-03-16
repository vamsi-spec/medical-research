from pydoc import doc
from typing import Dict, List, Optional
from Backend.retrieval.hybrid_retriever import HybridRetriever
from Backend.services.llm_service import OllamaLLMService
from Backend.services.citation_service import CitationExtractor
from Backend.services.evidence_ranking_service import EvidenceRankingService
from Backend.services.confidence_service import EnhancedConfidenceScorer, hallucination_result
from Backend.services.safety_service import MedicalSafetyClassifier
from Backend.services.safety_service import HallucinationDetector
from Backend.services.safety_service import AnswerValidator

from loguru import logger
import json


class RAGService:
    def __init__(
        self,
        retriever: HybridRetriever,
        llm_service: OllamaLLMService,
        top_k: int = 5,
        use_evidence_ranking: bool = True
    ):
        self.retriever = retriever
        self.llm_service = llm_service
        self.top_k = top_k
        self.citation_extractor = CitationExtractor()
        self.use_evidence_ranking = use_evidence_ranking

        if use_evidence_ranking:
            self.evidence_ranker = EvidenceRankingService()
            logger.info("Evidence ranking service initialized")
        else:
            self.evidence_ranker = None

        

        self.safety_classifier = MedicalSafetyClassifier()
        self.hallucination_detector = HallucinationDetector()
        self.confidence_scorer = EnhancedConfidenceScorer()
        self.answer_validator = AnswerValidator()

        logger.info("Safe RAG Service initialized with safety layer")





    def answer_query(
        self,
        query: str,
        top_k: Optional[int] = None,
        include_reasoning: bool = False
    ) -> Dict:
        k = top_k or self.top_k

        logger.info(f"Processing Query..{query}")

        safety_result = self.safety_classifier.classify_query(query)

        if not safety_result['safe']:
            logger.warning(f"Unsafe query detected: {safety_result['category']}")
            return {
                'answer': self._generate_refusal_message(safety_result),
                'citations': [],
                'confidence': 0.0,
                'safety': safety_result,
                'refused': True,
                'warning': safety_result['refusal_reason']
            }

        logger.debug(f"Retrieving top {k} documents...")
        documents = self.retriever.retrieve(query, top_k=k)

        if not documents:
            logger.warning("No documents retrieved")
            return {
                'answer': "I couldn't find the relevant information to answer this question.",
                'citations': [],
                'confidence':0.0,
                'warning':"No relevant documents found"
            }
        
        logger.debug(f"Documents retrieved: {len(documents)}")

        if self.use_evidence_ranking and self.evidence_ranker:
            logger.debug("Ranking documents by evidence quality...")
            documents = self.evidence_ranker.rank_documents(documents)

            documents = documents[:k]

            evidence_summary = self.evidence_ranker.get_evidence_summary(documents)
            logger.debug(f"Evidence: {evidence_summary['level_a_count']} Level A, "
                        f"{evidence_summary['level_b_count']} Level B")
        else:
            evidence_summary = None

        citations = self.citation_extractor.extract_citations(documents,max_citations=k)

        context = self.citation_extractor.build_citation_context(documents)

        logger.debug("Generating answer with LLM...")
        answer = self._generate_answer(query,context,len(citations))

        hallucination_result = self.hallucination_detector.detect_hallucination(answer,citations,documents)

        if hallucination_result['hallucination_risk'] == 'high':
            logger.warning("High hallucination risk detected")

        validation_result = self.answer_validator.validate_answer(
            answer=answer,
            query=query,
            citations=citations,
            confidence=0.7
        )

        if not validation_result['valid']:
            logger.warning(f"Answer validation failed: {validation_result['issues']}")

        confidence_result = self.confidence_scorer.calculate_confidence(
            query=query,
            answer=answer,
            documents=documents,
            evidence_summary=evidence_summary or {},
            hallucination_result=hallucination_result
        )

        confidence = confidence_result['confidence']

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence:.2f}) - adding disclaimer")
            answer = self._add_low_confidence_disclaimer(answer)


        citations_valid = self.citation_extractor.validate_citations(answer,max_citations_index=len(citations))

        if not citations_valid:
            logger.warning("Invalid citations detected")
        

        disclaimer = self._get_medical_disclaimer()

        return {
            'answer': answer,
            'citations': citations,
            'confidence': confidence,
            'confidence_breakdown': confidence_result['breakdown'],
            'confidence_reasoning': confidence_result['reasoning'],
            'recommendation': confidence_result['recommendation'],
            'disclaimer': disclaimer,
            'documents_used': len(documents),
            'evidence_summary': evidence_summary,
            'safety': safety_result,
            'hallucination_check': hallucination_result,
            'validation': validation_result,
            'refused': False,
            'warning': None
        }


    def _calculate_confidence(
        self,
        documents: List[Dict],
        answer: str
    )-> float:
    
            if not documents:
                    return 0.0
    
    # Factor 1: Average retrieval score (25%)
            avg_score = sum(d.get('fused_score', 0) for d in documents) / len(documents)
            retrieval_confidence = min(avg_score, 1.0) * 0.25
        
        # Factor 2: Evidence quality (35%) - NEW!
            if self.use_evidence_ranking:
                # Use evidence scores
                evidence_scores = [d.get('evidence_score', 0.5) for d in documents]
                avg_evidence = sum(evidence_scores) / len(evidence_scores)
                
                # Bonus for high-quality evidence (Level A)
                level_a_count = sum(1 for d in documents if d.get('evidence_level') == 'A')
                level_a_bonus = min(level_a_count / len(documents), 0.3)
                
                evidence_confidence = (avg_evidence + level_a_bonus) * 0.35
            else:
                # Fallback to study type only
                study_type_weights = {
                    'Meta-Analysis': 1.0,
                    'Systematic Review': 0.95,
                    'Randomized Controlled Trial': 0.9,
                    'Clinical Trial': 0.8,
                    'Cohort Study': 0.7,
                    'Case-Control Study': 0.6,
                    'Review': 0.5,
                    'Case Report': 0.3,
                    'Other': 0.2
                }
                
                study_scores = [
                    study_type_weights.get(d.get('study_type', 'Other'), 0.2)
                    for d in documents
                ]
                evidence_confidence = (sum(study_scores) / len(study_scores)) * 0.35
            
            # Factor 3: Answer completeness (25%)
            answer_length = len(answer)
            if answer_length < 50:
                length_confidence = 0.3 * 0.25
            elif answer_length < 150:
                length_confidence = 0.7 * 0.25
            else:
                length_confidence = 1.0 * 0.25
            
            # Factor 4: Citation presence (15%)
            import re
            citations = re.findall(r'\[\d+\]', answer)
            citation_confidence = min(len(citations) / 3, 1.0) * 0.15
            
            # Total confidence
            confidence = (
                retrieval_confidence +
                evidence_confidence +
                length_confidence +
                citation_confidence
            )
            
            return round(confidence, 2)
        


    def _generate_answer(
        self,
        query: str,
        context: str,
        num_citations: int
    ):
        prompt = f"""You are a medical research assistant. Answer the question using ONLY the provided research abstracts.

CRITICAL INSTRUCTIONS:
1. Base your answer ONLY on the provided research abstracts
2. Use citation markers [1], [2], etc. to reference specific sources
3. If the abstracts don't contain enough information, say "Based on the available research..."
4. Be precise and accurate - this is medical information
5. Do NOT add information not found in the abstracts

RESEARCH ABSTRACTS:
{context}

QUESTION: {query}

ANSWER (with citations [1], [2], etc.):"""
        try:
            answer = self.llm_service.generate_with_retry(prompt,temperature=0.1,max_tokens=800)
            return answer.strip()
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "I apologize, but I encountered an error generating the answer. Please try again."

    

    def _calculate_confidence(
        self,
        documents: List[Dict],
        answer: str
    ) -> float:
        if not documents:
            return 0.0
        avg_score = sum(d.get('fused_score',0) for d in documents) / len(documents)
        
        retrieval_confidence = min(avg_score,1.0)

        study_type_weights = {
            'Meta-Analysis': 1.0,
            'Systematic Review': 0.95,
            'Randomized Controlled Trial': 0.9,
            'Clinical Trial': 0.8,
            'Cohort Study': 0.7,
            'Case-Control Study': 0.6,
            'Review': 0.5,
            'Case Report': 0.3,
            'Other': 0.2
        }


        study_scores = [
            study_type_weights.get(d.get('study_type','Other'),0.1) * d.get('fused_score',0)
            for d in documents
        ]
        study_confidence = sum(study_scores) / len(study_scores) if study_scores else 0.5

        answer_length = len(answer)
        if answer_length < 50:
            length_confidence = 0.5
        elif answer_length < 150:
            length_confidence = 0.7
        else:
            length_confidence = 1.0

        import re
        citations = re.findall(r'\[\d+\]', answer)
        citation_confidence = min(len(citations) / 3, 1.0)


        confidence = (
            0.4 * retrieval_confidence +
            0.3 * study_confidence +
            0.2 * length_confidence +
            0.1 * citation_confidence
        )

        return round(confidence, 2)

    def _generate_refusal_message(self, safety_result: Dict) -> str:
        """Generate appropriate refusal message"""
        
        messages = {
            'emergency': (
                "🚨 MEDICAL EMERGENCY DETECTED\n\n"
                f"{safety_result['refusal_reason']}.\n\n"
                f"⚠️ ACTION REQUIRED: {safety_result['suggested_action']}\n\n"
                "This system is for informational purposes only and cannot handle medical emergencies."
            ),
            'diagnosis_request': (
                f"I cannot provide medical diagnoses.\n\n"
                f"{safety_result['suggested_action']}\n\n"
                "I can provide general information about medical conditions, but only a licensed "
                "healthcare provider can diagnose your specific situation."
            ),
            'treatment_request': (
                f"I cannot provide specific treatment recommendations.\n\n"
                f"{safety_result['suggested_action']}\n\n"
                "I can share general medical information, but treatment decisions should be made "
                "with your healthcare provider based on your individual circumstances."
            ),
            'dosage_question': (
                f"I cannot provide medication dosing instructions.\n\n"
                f"{safety_result['suggested_action']}\n\n"
                "Medication dosing must be determined by your healthcare provider based on your "
                "specific medical history, current medications, and health conditions."
            ),
            'self_harm': (
                "🆘 CRISIS SUPPORT NEEDED\n\n"
                f"{safety_result['suggested_action']}\n\n"
                "Please reach out for help:\n"
                "• National Suicide Prevention Lifeline: 988 or 1-800-273-8255\n"
                "• Crisis Text Line: Text HOME to 741741\n"
                "• Emergency: 911"
            )
        }
        
        return messages.get(
            safety_result['category'],
            f"{safety_result['refusal_reason']}. {safety_result['suggested_action']}"
        )

    def _add_low_confidence_disclaimer(self, answer: str) -> str:
        """Add disclaimer for low confidence answers"""
        
        disclaimer = (
            "\n\n⚠️ LOW CONFIDENCE: The available evidence for this answer is limited. "
            "Please verify this information with a healthcare professional."
        )
        
        return answer + disclaimer

    def _get_medical_disclaimer(self) -> str:
        """Medical disclaimer for all answers"""
        return (
            "⚕️ Medical Disclaimer: This information is for educational purposes only "
            "and should not replace professional medical advice. Always consult with a "
            "qualified healthcare provider for medical decisions."
        )

if __name__ == "__main__":
    # This requires full system setup
    # For actual testing, use test_rag.py script
    
    print("="*70)
    print("RAG SERVICE")
    print("="*70)
    print("\nComplete RAG pipeline:")
    print("1. Query → Retrieval")
    print("2. Extract citations")
    print("3. Build context")
    print("4. Generate answer")
    print("5. Validate & score confidence")
    print("\nUse scripts/test_rag.py for full testing")
