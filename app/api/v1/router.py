"""
Main API v1 router for the Dog Food Scoring API.

This module aggregates all v1 API endpoints into a single router.
"""

from fastapi import APIRouter

from app.api.v1 import health

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)