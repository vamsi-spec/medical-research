from re import search
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from Backend.models.schemas import (
    DrugInteractionRequest,
    DrugInteractionResponse,
    ClinicalTrialsRequest,
    ClinicalTrialsResponse,
    ClinicalTrial,
    MedicalCodeRequest,
    MedicalCodeResponse,
    MedicalCode
)


from Backend.api.dependencies import (
    get_drug_checker,
    get_trials_searcher,
    get_code_lookup
)


router = APIRouter()

@router.post(
    "/drug-interaction",
    response_model=DrugInteractionResponse,
    summary="Check for drug interaction",
    description="Check for interactions between two medications using RxNav API",
    tags=["Tools"]
)


async def check_drug_interaction(
    request: DrugInteractionRequest,
    drug_checker=Depends(get_drug_checker)
):
    try:
        logger.info(f"API request: /drug-interaction: {request.drug1} and {request.drug2}")

        result = drug_checker.check_interaction(
            drug1 = request.drug1,
            drug2 = request.drug2
        )

        return DrugInteractionResponse(**result)

    except Exception as e:
        logger.error(f"Error checking drug interaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking drug interaction: {str(e)}"
        )

@router.post(
    "/clinical-trials",
    response_model=ClinicalTrialsResponse,
    summary="Search clinical trials",
    description="Search for recruiting clinical trials from ClinicalTrials.gov",
    tags=["Tools"]
)

async def search_clinical_trials(
    request: ClinicalTrialsRequest,
    trials_searcher = Depends(get_trials_searcher)
):
    """
    Search for recruiting clinical trials.
    
    **Data Source:** ClinicalTrials.gov API v2
    
    **Example:**
```json
    {
        "condition": "type 2 diabetes",
        "status": ["RECRUITING"],
        "max_results": 10
    }
```
    """

    try:
        logger.info(f"API request: /clinical-trials: {request.condition}")

        trials = trials_searcher.search_trials(
            condition = request.condition,
            status = request.status,
            max_results = request.max_results
        )
        return ClinicalTrialsResponse(
            trials=[ClinicalTrial(**trial) for trial in trials],
            total_found=len(trials),
            query=request.condition
        )
    
    except Exception as e:
        logger.error(f"Error searching clinical trials: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching clinical trials: {str(e)}"
        )

@router.post(
    "/medical-code",
    response_model = MedicalCodeResponse,
    summary="Look up medical codes",
    description="Look up ICD-10 or CPT codes using NLM API",
    tags=["tools"]
)

async def lookup_medical_code(
    request: MedicalCodeRequest,
    code_lookup = Depends(get_code_lookup)
):
    try:
        logger.info(f"API request: /medical-code - {request.code_type}: {request.search_term}")

        if request.code_type == 'ICD10':
            codes = code_lookup.lookup_icd10(
                search_term = request.search_term,
                max_results = request.max_results
            )
        elif request.code_type == 'CPT':
            codes = code_lookup.lookup_cpt(
                search_term=request.search_term,
                max_results=request.max_results
            )
        else:
            raise ValueError(f"Invalid code_type: {request.code_type}")
        
        return MedicalCodeResponse(
            codes=[MedicalCode(**code) for code in codes],
            total_found=len(codes),
            search_term=request.search_term,
            code_type=request.code_type
        )
    except Exception as e:
        logger.error(f"Error looking up medical code: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error looking up medical code: {str(e)}"
        )