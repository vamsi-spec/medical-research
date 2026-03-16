from typing import Dict, List, Optional
from loguru import logger
import re

class MedicalSafetyClassifier:
    """
    Classify queries for safety
    
    Unsafe query types:
    1. Requests for specific medical diagnosis
    2. Requests for specific treatment plans
    3. Emergency medical situations
    4. Prescription dosage questions
    5. Self-harm or dangerous behavior
    6. Minors' health without parental consent
    
    Safe query types:
    - General medical information
    - Research literature questions
    - Drug interaction checking (informational)
    - ICD code lookup (billing)
    """

    def __init__(self):
        self.unsafe_patterns = self._build_unsafe_patterns()

        self.emergency_keywords = [
            'chest pain', 'can\'t breathe', 'difficulty breathing',
            'severe bleeding', 'unconscious', 'seizure',
            'overdose', 'poisoning', 'suicide', 'heart attack',
            'stroke', 'choking', 'severe burn'
        ]

        self.diagnosis_patterns = [
            r'\bdo i have\b',
            r'\bwhat\'s wrong with me\b',
            r'\bdiagnose me\b',
            r'\bis it\b.*\?',
            r'\bcould (it|this) be\b'
        ]

        self.treatment_patterns = [
            r'\bshould i take\b',
            r'\bhow much.*should i\b',
            r'\bwhat should i do (about|for)\b',
            r'\btreat my\b',
            r'\bcure my\b'
        ]

        logger.info("Medical safety classifier initialized")


    def classify_query(self, query: str) -> Dict:
        """
        Classify query for safety
        
        Args:
            query: User's question
            
        Returns:
            {
                'safe': bool,
                'category': str,
                'risk_level': str,
                'refusal_reason': str,
                'suggested_action': str
            }
        """
        query_lower = query.lower()

        if self._is_emergency(query_lower):
            return {
                'safe': False,
                'category': 'emergency',
                'risk_level': 'critical',
                'refusal_reason': 'This appears to be a medical emergency',
                'suggested_action': 'Call emergency services (911) immediately or go to the nearest emergency room.'
            }

        if self._is_diagnosis_request(query_lower):
            return {
                'safe': False,
                'category': 'diagnosis_request',
                'risk_level': 'high',
                'refusal_reason': 'I cannot provide medical diagnoses',
                'suggested_action': 'Please consult a licensed healthcare provider for proper diagnosis and treatment.'
            }

        if self._is_treatment_request(query_lower):
            return {
                'safe': False,
                'category': 'treatment_request',
                'risk_level': 'high',
                'refusal_reason': 'I cannot provide specific treatment recommendations',
                'suggested_action': 'Please consult your healthcare provider for personalized treatment advice.'
            }

        if self._is_dosage_question(query_lower):
            return {
                'safe': False,
                'category': 'dosage_question',
                'risk_level': 'high',
                'refusal_reason': 'I cannot provide specific medication dosing instructions',
                'suggested_action': 'Always follow your doctor\'s prescription or consult a pharmacist for dosing information.'
            }


        if self._is_self_harm(query_lower):
            return {
                'safe': False,
                'category': 'self_harm',
                'risk_level': 'critical',
                'refusal_reason': 'This query involves potential self-harm',
                'suggested_action': 'If you\'re in crisis, please contact: National Suicide Prevention Lifeline: 988 or 1-800-273-8255'
            }

        return {
            'safe': True,
            'category': 'informational',
            'risk_level': 'low',
            'refusal_reason': None,
            'suggested_action': None
        }

    def _is_emergency(self, query: str) -> bool:
        """Detect medical emergencies"""
        
        for keyword in self.emergency_keywords:
            if keyword in query:
                return True
        
        return False

    def _is_diagnosis_request(self, query: str) -> bool:
        """Detect requests for medical diagnosis"""
        
        for pattern in self.diagnosis_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                # Additional context check
                if any(symptom in query for symptom in ['pain', 'symptom', 'feeling', 'sick', 'hurt']):
                    return True
        
        return False

    def _is_treatment_request(self, query: str) -> bool:
        """Detect requests for treatment advice"""
        
        for pattern in self.treatment_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        # Check for "should I" + medical action
        if 'should i' in query:
            medical_actions = ['take', 'stop', 'start', 'increase', 'decrease', 'use']
            if any(action in query for action in medical_actions):
                return True
        
        return False

    def _is_dosage_question(self, query: str) -> bool:
        """Detect medication dosage questions"""
        
        dosage_keywords = [
            'how much', 'how many', 'what dose', 'dosage',
            'mg', 'ml', 'pills', 'tablets'
        ]
        
        # Must have dosage keyword + drug context
        has_dosage = any(kw in query for kw in dosage_keywords)
        
        # Common drug-related words
        drug_context = any(word in query for word in [
            'medication', 'medicine', 'drug', 'pill', 'tablet',
            'prescription', 'take', 'metformin', 'aspirin', 'ibuprofen'
        ])
        
        return has_dosage and drug_context

    def _is_self_harm(self, query: str) -> bool:
        """Detect self-harm or suicide-related queries"""
        
        self_harm_keywords = [
            'kill myself', 'end my life', 'suicide',
            'want to die', 'how to die', 'overdose on'
        ]
        
        for keyword in self_harm_keywords:
            if keyword in query:
                return True
        
        return False

    def _build_unsafe_patterns(self) -> List[str]:
        """Build comprehensive unsafe pattern list"""
        
        return [
            # Diagnosis patterns
            r'do i have',
            r'what\'s wrong with',
            r'diagnose',
            
            # Treatment patterns
            r'should i take',
            r'how should i treat',
            
            # Emergency patterns
            r'emergency',
            r'urgent',
            
            # Dosage patterns
            r'how much.*should i',
            r'what dose'
        ]

class HallucinationDetector:
    """
    Detect potential hallucinations in LLM outputs
    
    Detection methods:
    1. Citation verification (are citations valid?)
    2. Internal consistency (contradictions?)
    3. Confidence markers (hedging language)
    4. Specific claims without citations
    """

    def __init__(self):

        self.uncertainty_phrases = [
            'may', 'might', 'could', 'possibly',
            'perhaps', 'unclear', 'uncertain',
            'not enough information', 'limited evidence'
        ]

        self.strong_claim_indicators = [
            'studies show', 'research indicates',
            'proven to', 'known to', 'always',
            'never', 'definitely', 'certainly'
        ]


        logger.info("Hallucination detector initialized")

    def detect_hallucination(
        self, answer: str,
            citations: List[Dict],
            documents: List[Dict]
        ):
            """
        Detect potential hallucinations
        
        Args:
            answer: Generated answer text
            citations: Citation references used
            documents: Source documents retrieved
            
        Returns:
            {
                'hallucination_risk': str,  # 'low', 'medium', 'high'
                'issues': List[str],
                'confidence_adjustment': float  # -0.2 to 0.0
            }
        """
            issues = []
            risk_score = 0

            citation_issues = self._verify_citations(answer, citations)
            if citation_issues:
                issues.extend(citation_issues)
                risk_score += len(citation_issues) * 0.2

            uncited_claims = self._detect_uncited_claims(answer)
            if uncited_claims:
                issues.append(f"Strong claims without citations: {len(uncited_claims)}")
                risk_score += len(uncited_claims) * 0.15

            contradictions = self._detect_contradictions(answer)
            if contradictions:
                issues.extend(contradictions)
                risk_score += len(contradictions) * 0.3

            numeric_issues = self._check_numeric_precision(answer, citations)
            if numeric_issues:
                issues.extend(numeric_issues)
                risk_score += len(numeric_issues) * 0.25

            if risk_score >= 0.6:
                risk_level = 'high'
                confidence_adjustment = -0.3
            elif risk_score >= 0.3:
                risk_level = 'medium'
                confidence_adjustment = -0.15
            else:
                risk_level = 'low'
                confidence_adjustment = 0.0
            
            return {
                'hallucination_risk': risk_level,
                'risk_score': min(risk_score, 1.0),
                'issues': issues,
                'confidence_adjustment': confidence_adjustment
            }

    def _verify_citations(self, answer: str, citations: List[Dict]) -> List[str]:
        """Verify citation markers are valid"""
        issues = []
        citation_markers = re.findall(r'\[(\d+)\]', answer)
        valid_indices = {c['index'] for c in citations}

        for marker in citation_markers:
            try:
                marker_num = int(marker)
                if marker_num not in valid_indices:
                    issues.append(f"Invalid citation marker: [{marker}]")
            except ValueError:
                issues.append(f"Non-integer citation marker found: [{marker}]")

        return issues

    def _detect_uncited_claims(self, answer: str) -> List[str]:
        """Detect strong claims without citations"""
        uncited_claims = []
        sentences = re.split(r'[.!?]+', answer)

        for sentence in sentences:
            has_strong_claim = any(
                indicator in sentence.lower()
                for indicator in self.strong_claim_indicators
            )
            has_citation = bool(re.search(r'\[\d+\]', sentence))

            if has_strong_claim and not has_citation:
                uncited_claims.append(sentence.strip()[:50] + "...")

        return uncited_claims

    def _detect_contradictions(self, answer: str) -> List[str]:
        """Detect contradictions in answer"""
        contradictions = []
        contradiction_pairs = [
                ('safe', 'dangerous'),
                ('effective', 'ineffective'),
                ('recommended', 'not recommended'),
                ('increase', 'decrease')
            ]

        answer_lower = answer.lower()

        for word1, word2 in contradiction_pairs:
            if word1 in answer_lower and word2 in answer_lower:
                # Check if they're not just alternatives being discussed
                sentences = answer.split('.')
                for sent in sentences:
                    if word1 in sent.lower() and word2 in sent.lower():
                        contradictions.append(f"Potential contradiction: {sent.strip()[:60]}...")
        
        return contradictions

    def _check_numeric_precision(self, answer: str, citations: List[Dict]) -> List[str]:
        """Check for specific numbers without citations"""
        issues = []
        numeric_patterns = [
            r'\d+\.?\d*\s*%',  # Percentages
            r'\d+\.?\d*\s*(mg|ml|units)',  # Dosages
            r'\d{1,3}(?:,\d{3})*\s*patients?',  # Study sizes
        ]

        for pattern in numeric_patterns:
            matches = re.finditer(pattern, answer, re.IGNORECASE)
            for match in matches:
                # Check if this number has a nearby citation
                match_pos = match.start()
                
                # Look for citation within 100 chars
                surrounding = answer[max(0, match_pos - 50):min(len(answer), match_pos + 100)]
                
                if not re.search(r'\[\d+\]', surrounding):
                    issues.append(f"Specific number without citation: {match.group()}")
        
        return issues

class AnswerValidator:
    """
    Validate generated answers for quality and safety
    """
    def __init__(self):
        self.min_answer_length = 50
        self.max_answer_length = 2000

        logger.info("Answer validator initialized")

    def validate_answer(
        self,
        answer: str,
            query: str,
            citations: List[Dict],
            confidence: float
        ) -> Dict:
        """
        Validate answer quality
        
        Returns:
            {
                'valid': bool,
                'issues': List[str],
                'warnings': List[str],
                'quality_score': float
            }
        """
        issues = []
        warnings = []
        quality_score = 1.0

        if len(answer) < self.min_answer_length:
            issues.append("Answer too short")
            quality_score -= 0.3

        if len(answer) > self.max_answer_length:
            warnings.append("Answer very long - may be too detailed")
            quality_score -= 0.1

        if not citations or len(citations) == 0:
            warnings.append("Answer lacks citations")
            quality_score -= 0.2

        if not self._answers_question(answer, query):
            issues.append("Answer may not address the question")
            quality_score -= 0.4

        if not self._has_disclaimer(answer):
            warnings.append("Missing medical disclaimer")
            quality_score -= 0.1

        if confidence < 0.5 and not self._has_uncertainty_language(answer):
            warnings.append("Low confidence but answer lacks uncertainty language")
            quality_score -= 0.15

        valid = len(issues) == 0 and quality_score >= 0.5

        return {
            'valid': valid,
            'issues': issues,
            'warnings': warnings,
            'quality_score': max(0.0, quality_score)
        }

    def _answers_question(self, answer: str, query: str) -> bool:
        query_words = set(query.lower().split())
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why', 'when', 'where'}
        query_words = query_words - stop_words
        answer_lower = answer.lower()
        matching_words = sum(1 for word in query_words if word in answer_lower)

        if not query_words:
            return True

        return (matching_words / len(query_words)) >= 0.3

    def _has_disclaimer(self, answer: str) -> bool:
        """Check if medical disclaimer is present"""
        disclaimer_keywords = [
            'consult', 'healthcare provider', 'medical professional', 'doctor',
            'not medical advice', 'informational purposes'
        ]
        return any(kw in answer.lower() for kw in disclaimer_keywords)

    def _has_uncertainty_language(self, answer: str) -> bool:
        """Check for uncertainty/hedging language"""
        uncertainty_markers = [
            'may', 'might', 'could', 'possibly', 'suggest', 'indicate', 'appear',
            'limited evidence', 'unclear'
        ]
        return any(marker in answer.lower() for marker in uncertainty_markers)


if __name__ == "__main__":
    """Test safety services"""
    
    print("="*70)
    print("MEDICAL SAFETY SERVICES TEST")
    print("="*70)
    
    # Test safety classifier
    print("\n1. Safety Classifier:")
    print("-"*70)
    
    classifier = MedicalSafetyClassifier()
    
    test_queries = [
        "What is diabetes?",  # Safe
        "Do I have diabetes?",  # Unsafe - diagnosis
        "How much metformin should I take?",  # Unsafe - dosage
        "I'm having severe chest pain",  # Unsafe - emergency
    ]
    
    for query in test_queries:
        result = classifier.classify_query(query)
        print(f"\nQuery: {query}")
        print(f"Safe: {result['safe']}")
        print(f"Category: {result['category']}")
        print(f"Risk Level: {result['risk_level']}")
        if not result['safe']:
            print(f"Reason: {result['refusal_reason']}")
    
    # Test hallucination detector
    print("\n\n2. Hallucination Detector:")
    print("-"*70)
    
    detector = HallucinationDetector()
    
    test_answer = "Studies show metformin reduces HbA1c by 1.5% [1]. It is 100% safe for all patients."
    test_citations = [{'index': 1, 'pmid': '12345'}]
    
    result = detector.detect_hallucination(test_answer, test_citations, [])
    
    print(f"\nAnswer: {test_answer}")
    print(f"Hallucination Risk: {result['hallucination_risk']}")
    print(f"Issues: {result['issues']}")
    
    # Test answer validator
    print("\n\n3. Answer Validator:")
    print("-"*70)
    
    validator = AnswerValidator()
    
    test_answer_2 = "Diabetes is a metabolic disease. Consult your doctor."
    result = validator.validate_answer(
        test_answer_2,
        "What is diabetes?",
        [{'index': 1}],
        0.8
    )
    
    print(f"\nAnswer: {test_answer_2}")
    print(f"Valid: {result['valid']}")
    print(f"Quality Score: {result['quality_score']:.2f}")
    print(f"Issues: {result['issues']}")
    print(f"Warnings: {result['warnings']}")



            

            








    