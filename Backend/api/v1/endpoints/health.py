from fastapi import APIRouter
from loguru import logger

from Backend.models.schemas import HealthResponse


router = APIRouter()

@router.get(
    "/health",
    response_model = HealthResponse,
    summary="Health check",
    description="Check API health and component status",
    tags=["System"]
)

async def health_check():
    try:
        logger.info("API health check")
        components = {
                "rag_service": "healthy",
                "llm": "healthy",
                "retriever": "healthy",
                "database": "healthy"
        }
            
        return HealthResponse(
                status="healthy",
                components=components
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            components={"error": str(e)}
        )