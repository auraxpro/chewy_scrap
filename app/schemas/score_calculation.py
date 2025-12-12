"""
Score calculation schemas for the Dog Food Scoring API.

This module contains Pydantic schemas for score calculation requests and responses.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ScoreCalculationRequest(BaseModel):
    """Schema for score calculation request."""

    base_products: int = Field(..., description="Base product ID")
    topper_products: Optional[int] = Field(None, description="Topper product ID")
    pet_name: str = Field(..., description="Pet Name")
    breed: str = Field(..., description="Breed Name")
    years: int = Field(..., description="Age year of Pet")
    month: int = Field(..., description="Age month of Pet")
    weight: int = Field(..., description="Weight of Pet")
    storage: str = Field(..., description="Storage of food")
    packaging_size: str = Field(..., description="Packaging Size of Food")
    shelf_life: str = Field(..., description="Shelf Life of Food")
    topper_storage: Optional[str] = Field(None, description="Storage of topper food")
    topper_packaging_size: Optional[str] = Field(None, description="Packaging size of topper food")
    topper_shelf_life: Optional[str] = Field(None, description="Shelf Life of Topper Food")

    class Config:
        json_schema_extra = {
            "example": {
                "base_products": 1,
                "topper_products": 2,
                "pet_name": "Max",
                "breed": "Golden Retriever",
                "years": 3,
                "month": 6,
                "weight": 30,
                "storage": "Cool Dry Space (Away from moisture)",
                "packaging_size": "a month",
                "shelf_life": "15+Day",
                "topper_storage": "Refrigerator",
                "topper_packaging_size": "a month",
                "topper_shelf_life": "7Day",
            }
        }


class MicroScoreComponent(BaseModel):
    """Schema for micro score component."""

    grade: str = Field(..., description="Grade")
    score: int = Field(..., description="Score")


class MicroScore(BaseModel):
    """Schema for micro score breakdown."""

    food: MicroScoreComponent = Field(..., description="Food score")
    sourcing: MicroScoreComponent = Field(..., description="Sourcing score")
    processing: MicroScoreComponent = Field(..., description="Processing score")
    adequacy: MicroScoreComponent = Field(..., description="Adequacy score")
    carb: MicroScoreComponent = Field(..., description="Carb score")
    ingredient_quality_protein: MicroScoreComponent = Field(..., description="Ingredient quality protein score")
    ingredient_quality_fat: MicroScoreComponent = Field(..., description="Ingredient quality fat score")
    ingredient_quality_fiber: MicroScoreComponent = Field(..., description="Ingredient quality fiber score")
    ingredient_quality_carbohydrate: MicroScoreComponent = Field(..., description="Ingredient quality carbohydrate score")
    dirty_dozen: MicroScoreComponent = Field(..., description="Dirty dozen score")
    synthetic: MicroScoreComponent = Field(..., description="Synthetic score")
    longevity: MicroScoreComponent = Field(..., description="Longevity score")
    storage: MicroScoreComponent = Field(..., description="Storage score")
    packaging: MicroScoreComponent = Field(..., description="Packaging score")
    shelf_life: MicroScoreComponent = Field(..., description="Shelf life score")


class ScoreCalculationResponse(BaseModel):
    """Schema for score calculation response."""

    score: float = Field(..., description="Total Score")
    classification: str = Field(..., description="Classification of total Score")
    carb_percent: float = Field(..., description="Carb percentage")
    micro_score: MicroScore = Field(..., description="Micro score breakdown")

    class Config:
        json_schema_extra = {
            "example": {
                "score": 85.5,
                "classification": "Excellent",
                "carb_percent": 25.3,
                "micro_score": {
                    "food": {"grade": "A", "score": 90},
                    "sourcing": {"grade": "A", "score": 88},
                    "processing": {"grade": "B", "score": 82},
                    "adequacy": {"grade": "A", "score": 95},
                    "carb": {"grade": "B", "score": 80},
                    "ingredient_quality_protein": {"grade": "A", "score": 92},
                    "ingredient_quality_fat": {"grade": "A", "score": 85},
                    "ingredient_quality_fiber": {"grade": "B", "score": 78},
                    "ingredient_quality_carbohydrate": {"grade": "B", "score": 75},
                    "dirty_dozen": {"grade": "A", "score": 100},
                    "synthetic": {"grade": "B", "score": 80},
                    "longevity": {"grade": "A", "score": 90},
                    "storage": {"grade": "A", "score": 88},
                    "packaging": {"grade": "B", "score": 82},
                    "shelf_life": {"grade": "A", "score": 90},
                },
            }
        }

