"""
Schemas module for the Dog Food Scoring API.

This module contains Pydantic schemas for request/response validation
and serialization in the REST API.
"""

from app.schemas.processed_product import (
    ProcessedProductCreate,
    ProcessedProductInDB,
    ProcessedProductListResponse,
    ProcessedProductResponse,
    ProcessedProductUpdate,
)
from app.schemas.product import (
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
)
from app.schemas.score import ScoreComponentResponse, ScoreResponse

__all__ = [
    "ProductResponse",
    "ProductListResponse",
    "ProductDetailResponse",
    "ScoreResponse",
    "ScoreComponentResponse",
    "ProcessedProductCreate",
    "ProcessedProductUpdate",
    "ProcessedProductInDB",
    "ProcessedProductResponse",
    "ProcessedProductListResponse",
]
