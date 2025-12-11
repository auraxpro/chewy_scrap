"""
Health check endpoints for the Dog Food Scoring API.

This module provides health check endpoints for monitoring and status checking.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.config import API_VERSION

router = APIRouter()


@router.get("/")
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "Dog Food Scoring API",
        "version": API_VERSION,
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_database)):
    """
    Detailed health check including database connectivity.

    Args:
        db: Database session from dependency injection

    Returns:
        dict: Detailed health status including database status
    """
    database_status = "unknown"
    database_message = ""

    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        database_status = "healthy"
        database_message = "Database connection successful"
    except Exception as e:
        database_status = "unhealthy"
        database_message = f"Database connection failed: {str(e)}"

    return {
        "status": "healthy" if database_status == "healthy" else "degraded",
        "service": "Dog Food Scoring API",
        "version": API_VERSION,
        "checks": {
            "database": {
                "status": database_status,
                "message": database_message,
            }
        },
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_database)):
    """
    Readiness check for Kubernetes/container orchestration.

    Args:
        db: Database session from dependency injection

    Returns:
        dict: Readiness status

    Raises:
        HTTPException: If service is not ready
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "service": "Dog Food Scoring API",
        }
    except Exception as e:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}",
        )


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.

    Returns:
        dict: Liveness status
    """
    return {
        "status": "alive",
        "service": "Dog Food Scoring API",
    }
