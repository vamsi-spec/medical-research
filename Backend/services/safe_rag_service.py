from typing import Dict, List, Optional
from loguru import logger

from Backend.retrieval.hybrid_retriever import HybridRetriever
from Backend.services.llm_service import OllamaLLMService
from Backend.services.citation_service import CitationExtractor
from Backend.services.evidence_ranking_service import EvidenceRankingService
from Backend.services.safety_service import (
    MedicalSafetyClassifier,
    HallucinationDetector,
    AnswerValidator
)
from Backend.services.confidence_service import EnhancedConfidenceScorer

class SafeRagService:
    """
    Production RAG service with comprehensive safety layer
    
    Safety features:
    1. Query safety classification (refuses unsafe queries)
    2. Evidence-based ranking (prioritizes quality sources)
    3. Hallucination detection (identifies potential errors)
    4. Answer validation (checks quality and completeness)
    5. Enhanced confidence scoring (multi-factor assessment)
    6. Medical disclaimers (appropriate warnings)
    """

    def __init__(
        self,
        retriever: HybridRetriever,
        llm_service: OllamaLLMService,
        top_k: int = 5,
        use_evidence_ranking: bool = True,
        min_confidence_threshold: float = 0.5
    ):
        self.retriever = retriever
        self.llm_service = llm_service
        self.citation_extractor = CitationExtractor()
        self.top_k = top_k
        self.use_evidence_ranking = use_evidence_ranking
        self.min_confidence_threshold = min_confidence_threshold

        if use_evidence_ranking:
            self.evidence_ranker = EvidenceRankingService()
            logger.info("Evidence ranking service initialized")
        else:
            self.evidence_ranker = None

        self.safety_classifier = MedicalSafetyClassifier()
        self.hallucination_detector = HallucinationDetector()
        self.answer_validator = AnswerValidator()
        self.confidence_scorer = EnhancedConfidenceScorer()

        logger.info(f"Safe RAG Service initialized with safety layer")

    def answer_query(
        self,
        query: str,
        top_k: Optional[int] = None,
        bypass_safety: bool = False
    ) -> Dict:
        """
        Answer query with comprehensive safety pipeline
        
        Args:
            query: User's medical question
            top_k: Number of documents to retrieve
            bypass_safety: Skip safety checks (testing only)
            
        Returns:
            Complete response with answer, citations, confidence, and safety metadata
        """

        k = top_k or self.top_k

        logger.info(f"Processing query with safety:{query}")

        if not bypass_safety:
            safety_result = self.safety_classifier.classify_query(query)
            if not safety_result['safe']:
                logger.warning(f"Unsafe query detected: {safety_result['category']}")

                return {
                    'answer': self._generate_refusal_message(safety_result),
                    'citations': [],
                    'confidence': 0.0,
                    'confidence_breakdown': {},
                    'safety': safety_result,
                    'refused': True,
                    'warning': safety_result['refusal_reason']
                }

            else:
                safety_result = safety_result = {'safe': True, 'category': 'bypassed', 'risk_level': 'unknown'}
            logger.debug(f"Retrieving top {k} documents...")
            retrieve_k = k * 2 if self.use_evidence_ranking else k
            documents = self.retriever.retrieve(query,top_k=retrieve_k)
            
            if not documents:
                logger.warning("No documents retrieved")
                return self._generate_no_results_response(safety_result)
            
            logger.debug(f"Retrieved {len(documents)} documents")

            if self.use_evidence_ranking and self.evidence_ranker:
                logger.debug("Ranking documents by evidence quality...")
                documents = self.evidence_ranker.rank_documents(documents)
                documents = documents[:k]
                evidence_summary = self.evidence_ranker.get_evidence_summary(documents)
                logger.debug(f"Evidence: {evidence_summary['level_a_count']} Level A, "
                            f"{evidence_summary['level_b_count']} Level B")
            else:
                evidence_summary = None

        citations = self.citation_extractor.extract_citations(documents, max_citations=k)
        
        # ===== CONTEXT BUILDING =====
        context = self.citation_extractor.build_citation_context(
            documents,
            include_full_text=False
        )

        logger.debug("Generating answer with LLM...")
        answer = self._generate_safe_answer(query, context, len(citations))

        # ===== SAFETY LAYER 2: Hallucination Detection =====
        hallucination_result = self.hallucination_detector.detect_hallucination(
            answer=answer,
            citations=citations,
            documents=documents
        )

        if hallucination_result['hallucination_risk'] == 'high':
            logger.warning(f"High hallucination risk detected: {hallucination_result['issues']}")


        validation_result = self.answer_validator.validate_answer(
            answer=answer,
            query=query,
            citations=citations,
            confidence=0.7  # Preliminary
        )

        if not validation_result['valid']:
            logger.warning(f"Answer validation issues: {validation_result['issues']}")

        confidence_result = self.confidence_scorer.calculate_confidence(
            query=query,
            answer=answer,
            documents=documents,
            evidence_summary=evidence_summary or {},
            hallucination_result=hallucination_result
        )


        confidence = confidence_result['confidence']

        logger.info(f"Final confidence: {confidence:.2%}")

        if confidence < self.min_confidence_threshold:
            logger.warning(f"Confidence {confidence:.2f} below threshold {self.min_confidence_threshold}")
            answer = self._add_low_confidence_disclaimer(answer, confidence)

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
            'warning': self._generate_warnings(validation_result, hallucination_result, confidence)
        }

    def _generate_safe_answer(self, query: str, context: str, num_citations: int) -> str:
        """Generate answer with safety-focused prompting"""
        
        prompt = f"""You are a medical research assistant. Answer the question using ONLY the provided research abstracts.

CRITICAL SAFETY INSTRUCTIONS:
1. Base your answer ONLY on the provided research abstracts - DO NOT add information from your training
2. Use citation markers [1], [2], etc. for EVERY specific claim
3. If information is uncertain, explicitly state "The available research suggests..." or "Evidence indicates..."
4. NEVER provide:
   - Specific medical diagnoses
   - Specific treatment plans
   - Medication dosing instructions
   - Emergency medical advice
5. Use hedging language when appropriate (may, might, suggests, indicates, appears)
6. If the abstracts don't contain enough information, say "Based on the available research, there is limited information..."
7. Always remind users to consult healthcare providers for medical decisions

RESEARCH ABSTRACTS:
{context}

QUESTION: {query}

ANSWER (with citations [1], [2], etc. and appropriate disclaimers):"""

        try:
            answer = self.llm_service.generate_with_retry(
                prompt,
                temperature=0.1,  # Low temperature for factual accuracy
                max_tokens=800
            )
            
            return answer.strip()
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "I apologize, but I encountered an error generating the answer. Please try again."


    def _generate_refusal_message(self, safety_result: Dict) -> str:
        """Generate appropriate refusal message based on safety classification"""
        
        messages = {
            'emergency': (
                "🚨 MEDICAL EMERGENCY DETECTED\n\n"
                f"{safety_result['refusal_reason']}.\n\n"
                f"⚠️ IMMEDIATE ACTION REQUIRED:\n{safety_result['suggested_action']}\n\n"
                "This system is for informational purposes only and cannot handle medical emergencies."
            ),
            'diagnosis_request': (
                "I cannot provide medical diagnoses.\n\n"
                f"{safety_result['suggested_action']}\n\n"
                "I can provide general information about medical conditions, but only a licensed "
                "healthcare provider can diagnose your specific situation after proper examination."
            ),
            'treatment_request': (
                "I cannot provide specific treatment recommendations.\n\n"
                f"{safety_result['suggested_action']}\n\n"
                "I can share general medical information, but treatment decisions must be made "
                "with your healthcare provider based on your individual medical history, current "
                "conditions, and comprehensive evaluation."
            ),
            'dosage_question': (
                "I cannot provide medication dosing instructions.\n\n"
                f"{safety_result['suggested_action']}\n\n"
                "Medication dosing must be determined by your healthcare provider based on your "
                "specific medical history, current medications, kidney/liver function, and other "
                "individual factors. Never adjust medication doses without professional guidance."
            ),
            'self_harm': (
                "🆘 CRISIS SUPPORT NEEDED\n\n"
                "If you're experiencing thoughts of self-harm, please reach out for immediate help:\n\n"
                "• National Suicide Prevention Lifeline: 988 or 1-800-273-8255 (24/7)\n"
                "• Crisis Text Line: Text HOME to 741741\n"
                "• Emergency Services: 911\n\n"
                "You don't have to face this alone. Professional help is available."
            )
        }
        
        return messages.get(
            safety_result['category'],
            f"{safety_result['refusal_reason']}.\n\n{safety_result['suggested_action']}"
        )


    def _generate_no_results_response(self, safety_result: Dict) -> Dict:
        """Generate response when no documents retrieved"""
        
        return {
            'answer': (
                "I couldn't find relevant research to answer this question.\n\n"
                "This could mean:\n"
                "• The question is outside my knowledge base\n"
                "• The topic requires more specific search terms\n"
                "• Limited research exists on this specific question\n\n"
                "Please try rephrasing your question or consult a healthcare provider."
            ),
            'citations': [],
            'confidence': 0.0,
            'confidence_breakdown': {},
            'evidence_summary': None,
            'safety': safety_result,
            'refused': False,
            'warning': "No relevant documents found"
        }


    def _add_low_confidence_disclaimer(self, answer: str, confidence: float) -> str:
        """Add disclaimer for low confidence answers"""
        
        disclaimer = (
            f"\n\n⚠️ LOW CONFIDENCE ({confidence:.0%}): The available evidence for this answer is limited. "
            f"This information should be verified with a healthcare professional before making any decisions."
        )
        
        return answer + disclaimer


    def _generate_warnings(
        self,
        validation_result: Dict,
        hallucination_result: Dict,
        confidence: float
    ) -> Optional[str]:
        """Generate warnings based on validation results"""
        
        warnings = []
        
        # Validation warnings
        if validation_result['warnings']:
            warnings.extend(validation_result['warnings'])
        
        # Hallucination warnings
        if hallucination_result['hallucination_risk'] in ['medium', 'high']:
            warnings.append(f"Potential accuracy issues detected ({hallucination_result['hallucination_risk']} risk)")
        
        # Confidence warnings
        if confidence < 0.5:
            warnings.append("Low confidence - verify with healthcare provider")
        
        return "; ".join(warnings) if warnings else None

    def _get_medical_disclaimer(self) -> str:
        """Standard medical disclaimer"""
        
        return (
            "⚕️ Medical Disclaimer: This information is for educational and informational purposes only. "
            "It is not intended to be a substitute for professional medical advice, diagnosis, or treatment. "
            "Always seek the advice of your physician or other qualified health provider with any questions "
            "you may have regarding a medical condition. Never disregard professional medical advice or delay "
            "seeking it because of something you have read here. In case of emergency, call 911 immediately."
        )


if __name__ == "__main__":
    """Test Safe RAG Service"""
    
    print("="*70)
    print("SAFE RAG SERVICE TEST")
    print("="*70)
    print("\nThis is a component test. For full system test, use test_complete_system.py")