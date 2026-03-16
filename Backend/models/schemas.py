"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union
from datetime import datetime


# ============================================================================
# REQUEST MODELS
# ============================================================================

class AskQueryRequest(BaseModel):
    """
    Request model for /ask endpoint
    """
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Medical question to answer",
        example="What is the first-line treatment for type 2 diabetes?"
    )
    
    top_k: Optional[int] = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of sources to retrieve"
    )
    
    bypass_safety: Optional[bool] = Field(
        default=False,
        description="Bypass safety checks (for testing only)"
    )
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class DrugInteractionRequest(BaseModel):
    """
    Request model for drug interaction checking
    """
    drug1: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="First drug name",
        example="warfarin"
    )
    
    drug2: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Second drug name",
        example="aspirin"
    )


class ClinicalTrialsRequest(BaseModel):
    """
    Request model for clinical trials search
    """
    condition: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Medical condition",
        example="type 2 diabetes"
    )
    
    status: Optional[List[str]] = Field(
        default=["RECRUITING"],
        description="Trial status filters",
        example=["RECRUITING", "ACTIVE_NOT_RECRUITING"]
    )
    
    max_results: Optional[int] = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of trials to return"
    )


class MedicalCodeRequest(BaseModel):
    """
    Request model for medical code lookup
    """
    search_term: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Diagnosis or code to search",
        example="diabetes"
    )
    
    code_type: str = Field(
        default="ICD10",
        description="Code system type",
        example="ICD10"
    )
    
    max_results: Optional[int] = Field(
        default=10,
        ge=1,
        le=20,
        description="Maximum results"
    )
    
    @validator('code_type')
    def validate_code_type(cls, v):
        allowed = ['ICD10', 'CPT']
        if v.upper() not in allowed:
            raise ValueError(f'code_type must be one of {allowed}')
        return v.upper()


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class Citation(BaseModel):
    """Citation information"""
    index: int
    pmid: str
    title: str
    study_type: str
    publication_year: Optional[int]
    score: Optional[float]


class ConfidenceBreakdown(BaseModel):
    """Confidence score breakdown"""
    retrieval_quality: float
    evidence_quality: float
    consistency: float
    completeness: float
    recency: float


class EvidenceSummary(BaseModel):
    """Evidence quality summary"""
    total_documents: int
    level_a_count: int
    level_b_count: int
    level_c_count: int
    avg_evidence_score: float
    study_type_distribution: Dict[str, int]


class SafetyInfo(BaseModel):
    """Safety classification information"""
    safe: bool
    category: str
    risk_level: str
    refusal_reason: Optional[str] = None
    suggested_action: Optional[str] = None


class HallucinationCheck(BaseModel):
    """Hallucination detection results"""
    hallucination_risk: str
    risk_score: float
    issues: List[str]
    confidence_adjustment: float


class ValidationResult(BaseModel):
    """Answer validation results"""
    valid: bool
    issues: List[str]
    warnings: List[str]
    quality_score: float


class AskQueryResponse(BaseModel):
    """
    Response model for /ask endpoint
    """
    answer: str = Field(
        ...,
        description="Generated answer with citations"
    )
    
    citations: List[Citation] = Field(
        default=[],
        description="Source citations"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence score"
    )
    
    confidence_breakdown: Optional[ConfidenceBreakdown] = Field(
        default=None,
        description="Detailed confidence breakdown"
    )
    
    confidence_reasoning: Optional[List[str]] = Field(
        default=[],
        description="Human-readable confidence reasoning"
    )
    
    recommendation: Optional[str] = Field(
        default=None,
        description="Usage recommendation"
    )
    
    disclaimer: str = Field(
        ...,
        description="Medical disclaimer"
    )
    
    documents_used: int = Field(
        ...,
        description="Number of source documents used"
    )
    
    evidence_summary: Optional[EvidenceSummary] = Field(
        default=None,
        description="Evidence quality summary"
    )
    
    safety: SafetyInfo = Field(
        ...,
        description="Safety classification"
    )
    
    hallucination_check: Optional[HallucinationCheck] = Field(
        default=None,
        description="Hallucination detection results"
    )
    
    validation: Optional[ValidationResult] = Field(
        default=None,
        description="Answer validation results"
    )
    
    refused: bool = Field(
        ...,
        description="Whether query was refused"
    )
    
    warning: Optional[str] = Field(
        default=None,
        description="Warning message if any"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response timestamp"
    )


class DrugInteractionResponse(BaseModel):
    """Response for drug interaction check"""
    interaction_found: bool
    drug1: str
    drug2: str
    severity: Optional[str]
    description: str
    clinical_recommendation: str
    source: str
    data_source: str


class ClinicalTrial(BaseModel):
    """Clinical trial information"""
    nct_id: str
    title: str
    status: str
    phase: str
    enrollment: Optional[Union[int, str]] = None
    conditions: Optional[List[str]] = []
    interventions: Optional[List[str]] = []
    locations: Optional[List[Dict]] = []
    url: str


class ClinicalTrialsResponse(BaseModel):
    """Response for clinical trials search"""
    trials: List[ClinicalTrial]
    total_found: int
    query: str
    timestamp: datetime = Field(default_factory=datetime.now)


class MedicalCode(BaseModel):
    """Medical code information"""
    code: str
    description: str
    code_system: str
    category: Optional[str] = None
    billable: Optional[bool] = None
    source: str


class MedicalCodeResponse(BaseModel):
    """Response for medical code lookup"""
    codes: List[MedicalCode]
    total_found: int
    search_term: str
    code_type: str
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    components: Dict[str, str]


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# EXAMPLE RESPONSES (for API docs)
# ============================================================================

class Config:
    """Pydantic config for all models"""
    schema_extra = {
        "example": {
            "answer": "Metformin is widely recognized as the first-line treatment...",
            "citations": [
                {
                    "index": 1,
                    "pmid": "38234567",
                    "title": "Metformin efficacy in type 2 diabetes",
                    "study_type": "Meta-Analysis",
                    "publication_year": 2024
                }
            ],
            "confidence": 0.87,
            "refused": False
        }
    }