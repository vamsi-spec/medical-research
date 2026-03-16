from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from Backend.api.v1.endpoints import ask, tools, health
from Backend.models.schemas import ErrorResponse


app = FastAPI(
    title="Medical Literature Research Assistant API",
    description="""
    ## 🏥 Medical Literature Research Assistant
    
    A production-grade medical AI assistant that provides evidence-based answers 
    from peer-reviewed medical literature.
    
    ### Features
    
    - 📚 **Evidence-Based Answers**: Responses backed by PubMed research
    - 🔬 **Quality Sources**: Prioritizes RCTs, Meta-Analyses, Systematic Reviews
    - 🛡️ **Safety Layer**: Query classification, hallucination detection, confidence scoring
    - 💊 **Drug Interactions**: Real-time checking via RxNav API (NLM)
    - 🧪 **Clinical Trials**: Search ClinicalTrials.gov database
    - 🏷️ **Medical Codes**: ICD-10 and CPT code lookup
    
    ### Data Sources
    
    - PubMed (5,000+ medical abstracts)
    - RxNav API (National Library of Medicine)
    - ClinicalTrials.gov API v2
    - NLM ClinicalTables API
    
    ### Safety Notice
    
    ⚠️ This system is for informational purposes only. Always consult qualified 
    healthcare providers for medical advice, diagnosis, or treatment.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License"
    }

)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000",  # FastAPI
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Outgoing response: {response.status_code}")
        return response
    except Exception as e:
        logger.exception(f"Unhandled exception during request: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error", "error": str(e)})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            detail=str(exc.errors())
        ).dict()
    )

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["System"]
)

app.include_router(
    ask.router,
    prefix="/api/v1",
    tags=["Query"]
)

app.include_router(
    tools.router,
    prefix="/api/v1",
    tags=["Tools"]
)


@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint
    """
    return {
        "message": "Medical Literature Research Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    logger.info("="*70)
    logger.info("Medical Literature Research Assistant API - Starting")
    logger.info("="*70)
    logger.info("Version: 1.0.0")
    logger.info("Docs: http://localhost:8000/docs")
    logger.info("="*70)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    logger.info("API shutting down...")

if __name__ == "__main__":
    import uvicorn
    
    # Configure logging
    logger.add(
        "logs/api.log",
        rotation="100 MB",
        retention="10 days",
        level="INFO"
    )
    
    # Run server
    uvicorn.run(
        "Backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (dev only)
        log_level="info"
    )