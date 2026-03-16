from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from loguru import logger

from Backend.models.schemas import (
    AskQueryRequest,
    AskQueryResponse,
    Citation,
    ConfidenceBreakdown,
    EvidenceSummary,
    SafetyInfo,
    HallucinationCheck,
    ValidationResult
)

from Backend.services.safe_rag_service import SafeRagService
from Backend.api.dependencies import get_rag_service

router = APIRouter()

@router.post(
    "/ask",
    response_model=AskQueryResponse,
    summary="Ask a medical question",
    description="Submit a medical question and receive an evidence-based answer with citations",
    response_description="Answer with citations, confidence score, and safety metadata",
    tags=["Query"]
)


async def ask_question(
    request: AskQueryRequest,
    rag_service: SafeRagService = Depends(get_rag_service)
):
    """
    Ask a medical question and receive an evidence-based answer.
    
    **Safety Features:**
    - Query safety classification (refuses dangerous queries)
    - Evidence-based ranking (prioritizes high-quality sources)
    - Hallucination detection (identifies potential errors)
    - Confidence scoring (multi-factor assessment)
    - Medical disclaimers (appropriate warnings)
    
    **Example Query:**
```json
    {
        "query": "What is the first-line treatment for type 2 diabetes?",
        "top_k": 5
    }
```
    """
    try:
        logger.info(f"API request: /ask-query: {request.query[:50]}...")
        result = rag_service.answer_query(
            query=request.query,
            top_k=request.top_k,
            bypass_safety=request.bypass_safety
        )

        response = AskQueryResponse(
            answer=result['answer'],
            citations=[
                Citation(**citation) for citation in result.get('citations', [])
            ],
            confidence=result['confidence'],
            confidence_breakdown=ConfidenceBreakdown(**result['confidence_breakdown']) 
                if result.get('confidence_breakdown') else None,
            confidence_reasoning=result.get('confidence_reasoning', []),
            recommendation=result.get('recommendation'),
            disclaimer=result.get('disclaimer', ''),
            documents_used=result.get('documents_used', 0),
            evidence_summary=EvidenceSummary(**result['evidence_summary'])
                if result.get('evidence_summary') else None,
            safety=SafetyInfo(**result['safety']),
            hallucination_check=HallucinationCheck(**result['hallucination_check'])
                if result.get('hallucination_check') else None,
            validation=ValidationResult(**result['validation'])
                if result.get('validation') else None,
            refused=result.get('refused', False),
            warning=result.get('warning')
        )

        if response.refused:
            logger.warning(f"Query refused: {response.safety.category}")
        elif response.confidence < 0.5:
            logger.warning(f"Low confidence response: {response.confidence:.2%}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error in /ask endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
