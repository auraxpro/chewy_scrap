"""
Score schemas for the Dog Food Scoring API.

This module contains Pydantic schemas for score-related API requests and responses.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# Base Schemas
# ============================================================================


class ScoreComponentBase(BaseModel):
    """Base schema for score component data."""

    component_name: str = Field(..., description="Name of the scoring component")
    component_score: float = Field(
        ..., ge=0, le=100, description="Component score (0-100)"
    )
    weight: float = Field(..., ge=0, le=1, description="Weight in overall calculation")
    weighted_score: float = Field(..., description="Weighted score contribution")


# ============================================================================
# Response Schemas
# ============================================================================


class ScoreComponentResponse(BaseModel):
    """Schema for score component response."""

    id: int = Field(..., description="Component ID")
    score_id: int = Field(..., description="Reference to product score ID")
    component_name: str = Field(..., description="Component name")
    component_score: float = Field(..., description="Component score (0-100)")
    weight: float = Field(..., description="Weight in calculation")
    weighted_score: float = Field(..., description="Weighted score")
    details: Optional[str] = Field(None, description="Detailed breakdown (JSON)")
    confidence: Optional[float] = Field(
        None, ge=0, le=1, description="Confidence level (0-1)"
    )
    created_at: datetime = Field(
        ..., description="Timestamp when component was created"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "score_id": 1,
                "component_name": "ingredient_quality",
                "component_score": 85.0,
                "weight": 0.35,
                "weighted_score": 29.75,
                "details": '{"meat_content": 0.8, "whole_foods": 0.9}',
                "confidence": 0.95,
                "created_at": "2024-01-15T12:00:00",
            }
        }


class ScoreResponse(BaseModel):
    """Schema for product score response."""

    id: int = Field(..., description="Score ID")
    product_id: int = Field(..., description="Reference to product ID")
    total_score: float = Field(..., ge=0, le=100, description="Total score (0-100)")
    score_version: str = Field(..., description="Scoring algorithm version")
    calculated_at: datetime = Field(..., description="When score was calculated")
    created_at: datetime = Field(..., description="When score record was created")
    updated_at: datetime = Field(..., description="When score was last updated")
    components: List[ScoreComponentResponse] = Field(
        default_factory=list, description="Score component breakdown"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_id": 1,
                "total_score": 85.5,
                "score_version": "1.0.0",
                "calculated_at": "2024-01-15T12:00:00",
                "created_at": "2024-01-15T12:00:00",
                "updated_at": "2024-01-15T12:00:00",
                "components": [
                    {
                        "id": 1,
                        "score_id": 1,
                        "component_name": "ingredient_quality",
                        "component_score": 85.0,
                        "weight": 0.35,
                        "weighted_score": 29.75,
                        "confidence": 0.95,
                    },
                    {
                        "id": 2,
                        "score_id": 1,
                        "component_name": "nutritional_value",
                        "component_score": 88.0,
                        "weight": 0.30,
                        "weighted_score": 26.4,
                        "confidence": 0.92,
                    },
                    {
                        "id": 3,
                        "score_id": 1,
                        "component_name": "processing_method",
                        "component_score": 80.0,
                        "weight": 0.20,
                        "weighted_score": 16.0,
                        "confidence": 0.88,
                    },
                    {
                        "id": 4,
                        "score_id": 1,
                        "component_name": "price_value",
                        "component_score": 82.5,
                        "weight": 0.15,
                        "weighted_score": 12.375,
                        "confidence": 0.90,
                    },
                ],
            }
        }


class ScoreWithProductResponse(BaseModel):
    """Schema for score response including product information."""

    score: ScoreResponse = Field(..., description="Product score")
    product_name: str = Field(..., description="Product name")
    product_url: str = Field(..., description="Product URL")
    product_image_url: Optional[str] = Field(None, description="Product image URL")
    category: Optional[str] = Field(None, description="Product category")
    price: Optional[str] = Field(None, description="Product price")

    class Config:
        json_schema_extra = {
            "example": {
                "score": {
                    "id": 1,
                    "product_id": 1,
                    "total_score": 85.5,
                    "score_version": "1.0.0",
                    "components": [],
                },
                "product_name": "American Journey Grain-Free Salmon",
                "product_url": "https://www.chewy.com/american-journey-grain-free-salmon/dp/108423",
                "product_image_url": "https://img.chewy.com/is/image/catalog/108423_MAIN._AC_SL1500_.jpg",
                "category": "dry_kibble",
                "price": "$49.99",
            }
        }


# ============================================================================
# Request Schemas
# ============================================================================


class CalculateScoreRequest(BaseModel):
    """Schema for score calculation request."""

    product_id: int = Field(..., description="Product ID to calculate score for")
    force_recalculate: bool = Field(
        False, description="Force recalculation even if score exists"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "force_recalculate": False,
            }
        }


class BatchCalculateScoreRequest(BaseModel):
    """Schema for batch score calculation request."""

    product_ids: List[int] = Field(
        ..., description="List of product IDs to calculate scores for"
    )
    force_recalculate: bool = Field(
        False, description="Force recalculation even if scores exist"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_ids": [1, 2, 3, 4, 5],
                "force_recalculate": False,
            }
        }


class ScoreFilterRequest(BaseModel):
    """Schema for filtering scores."""

    min_score: Optional[float] = Field(
        None, ge=0, le=100, description="Minimum total score"
    )
    max_score: Optional[float] = Field(
        None, ge=0, le=100, description="Maximum total score"
    )
    component_name: Optional[str] = Field(
        None, description="Filter by specific component name"
    )
    min_component_score: Optional[float] = Field(
        None, ge=0, le=100, description="Minimum component score"
    )
    score_version: Optional[str] = Field(None, description="Filter by score version")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")
    sort_by: str = Field(
        "total_score", description="Sort by field (total_score, calculated_at, etc.)"
    )
    sort_order: str = Field("desc", description="Sort order (asc or desc)")

    class Config:
        json_schema_extra = {
            "example": {
                "min_score": 80.0,
                "max_score": 100.0,
                "component_name": "ingredient_quality",
                "min_component_score": 85.0,
                "score_version": "1.0.0",
                "page": 1,
                "page_size": 50,
                "sort_by": "total_score",
                "sort_order": "desc",
            }
        }


# ============================================================================
# Statistics Schemas
# ============================================================================


class ScoreStatsResponse(BaseModel):
    """Schema for score statistics response."""

    total_scored_products: int = Field(
        ..., description="Total number of scored products"
    )
    average_score: float = Field(..., description="Average score across all products")
    median_score: float = Field(..., description="Median score")
    min_score: float = Field(..., description="Minimum score")
    max_score: float = Field(..., description="Maximum score")
    score_distribution: dict[str, int] = Field(
        ..., description="Distribution of scores by range"
    )
    component_averages: dict[str, float] = Field(
        ..., description="Average scores by component"
    )
    latest_score_version: str = Field(..., description="Latest scoring version")

    class Config:
        json_schema_extra = {
            "example": {
                "total_scored_products": 1000,
                "average_score": 75.5,
                "median_score": 77.0,
                "min_score": 25.0,
                "max_score": 98.5,
                "score_distribution": {
                    "0-20": 10,
                    "20-40": 50,
                    "40-60": 200,
                    "60-80": 500,
                    "80-100": 240,
                },
                "component_averages": {
                    "ingredient_quality": 78.5,
                    "nutritional_value": 76.2,
                    "processing_method": 72.8,
                    "price_value": 74.1,
                },
                "latest_score_version": "1.0.0",
            }
        }


class TopScoredProductsResponse(BaseModel):
    """Schema for top scored products response."""

    top_products: List[ScoreWithProductResponse] = Field(
        ..., description="List of top scored products"
    )
    category: Optional[str] = Field(None, description="Category filter applied")
    limit: int = Field(..., description="Number of products returned")

    class Config:
        json_schema_extra = {
            "example": {
                "top_products": [],
                "category": "dry_kibble",
                "limit": 10,
            }
        }
