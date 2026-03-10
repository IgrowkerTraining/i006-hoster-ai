"""API dependencies and utilities."""
from pydoc import text
from datetime import date

from fastapi import HTTPException, status
from typing import Optional

from app.services.ai_service import ai_service
from app.core.logging import get_logger
from app.db.database_ai import MainSessionLocal, AIAsyncSessionLocal
from app.db.models.report_model import Report

logger = get_logger(__name__)


async def get_ai_service():
    """Get AI service instance."""
    try:
        # Check if AI service is healthy
        if not await ai_service.health_check():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is currently unavailable"
            )
        return ai_service
    except Exception as e:
        logger.error(f"AI service dependency error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to AI service"
        )


async def get_main_db():
    async with MainSessionLocal() as session:
        yield session


async def get_ai_db():
    async with AIAsyncSessionLocal() as session:
        yield session
           