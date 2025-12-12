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
