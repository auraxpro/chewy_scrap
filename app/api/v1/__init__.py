"""
API v1 module for the Dog Food Scoring API.

This module contains version 1 of the REST API endpoints.
"""

from app.api.v1.router import api_router

__all__ = [
    "api_router",
]
