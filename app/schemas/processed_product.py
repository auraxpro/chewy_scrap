"""
Pydantic schemas for processed product data.

This module contains Pydantic models for processed product validation,
serialization, and API responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Enums matching the database enums
class FoodCategoryEnum(str, Enum):
    """Food category classifications."""

    RAW = "Raw"
    FRESH = "Fresh"
    DRY = "Dry"
    WET = "Wet"
    SOFT = "Soft"
    OTHER = "Other"


class SourcingIntegrityEnum(str, Enum):
    """Sourcing integrity classifications."""

    HUMAN_GRADE_ORGANIC = "Human Grade (organic)"
    HUMAN_GRADE = "Human Grade"
    FEED_GRADE = "Feed Grade"
    OTHER = "Other"


class ProcessingMethodEnum(str, Enum):
    """Processing method classifications."""

    UNCOOKED_NOT_FROZEN = "Uncooked (Not Frozen)"
    UNCOOKED_FLASH_FROZEN = "Uncooked (Flash Frozen)"
    UNCOOKED_FROZEN = "Uncooked (Frozen)"
    LIGHTLY_COOKED_NOT_FROZEN = "Lightly Cooked (Not Frozen)"
    LIGHTLY_COOKED_FROZEN = "Lightly Cooked (Frozen)"
    FREEZE_DRIED = "Freeze Dried"
    AIR_DRIED = "Air Dried"
    DEHYDRATED = "Dehydrated"
    BAKED = "Baked"
    EXTRUDED = "Extruded"
    RETORTED = "Retorted"
    OTHER = "Other"


class NutritionallyAdequateEnum(str, Enum):
    """Nutritional adequacy assessment."""

    YES = "Yes"
    NO = "No"


class QualityClassEnum(str, Enum):
    """Ingredient quality classifications."""

    HIGH = "High"
    GOOD = "Good"
    MODERATE = "Moderate"
    LOW = "Low"


class FoodStorageEnum(str, Enum):
    """Food storage requirements."""

    FREEZER = "Freezer"
    REFRIGERATOR = "Refrigerator"
    COOL_DRY_AWAY = "Cool Dry Space (Away from moisture)"
    COOL_DRY_NOT_AWAY = "Cool Dry Space (Not away from moisture)"


class PackagingSizeEnum(str, Enum):
    """Estimated packaging consumption duration."""

    ONE_MONTH = "a month"
    TWO_MONTH = "2 month"
    THREE_PLUS_MONTH = "3+ month"


class ShelfLifeEnum(str, Enum):
    """Shelf life after thawing."""

    SEVEN_DAY = "7Day"
    EIGHT_TO_FOURTEEN_DAY = "8-14 Day"
    FIFTEEN_PLUS_DAY = "15+Day"
    OTHER = "Other"


class ProcessedProductBase(BaseModel):
    """Base schema for processed product data."""

    # Basic Information
    flavor: Optional[str] = None

    # Food Category
    food_category: Optional[FoodCategoryEnum] = None
    category_reason: Optional[str] = None

    # Sourcing Integrity
    sourcing_integrity: Optional[SourcingIntegrityEnum] = None
    sourcing_integrity_reason: Optional[str] = None

    # Processing Methods
    processing_method_1: Optional[ProcessingMethodEnum] = None
    processing_method_2: Optional[ProcessingMethodEnum] = None
    processing_adulteration_method: Optional[ProcessingMethodEnum] = None
    processing_adulteration_method_reason: Optional[str] = None

    # Guaranteed Analysis
    guaranteed_analysis_crude_protein_pct: Optional[float] = Field(None, ge=0, le=100)
    guaranteed_analysis_crude_fat_pct: Optional[float] = Field(None, ge=0, le=100)
    guaranteed_analysis_crude_fiber_pct: Optional[float] = Field(None, ge=0, le=100)
    guaranteed_analysis_crude_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    guaranteed_analysis_crude_ash_pct: Optional[float] = Field(None, ge=0, le=100)
    starchy_carb_pct: Optional[float] = Field(None, ge=0, le=100)

    # Nutritional Adequacy
    nutritionally_adequate: Optional[NutritionallyAdequateEnum] = None
    nutritionally_adequate_reason: Optional[str] = None

    # Ingredients - All
    ingredients_all: Optional[str] = None

    # Protein Ingredients
    protein_ingredients_all: Optional[str] = None
    protein_ingredients_high: Optional[int] = Field(None, ge=0)
    protein_ingredients_good: Optional[int] = Field(None, ge=0)
    protein_ingredients_moderate: Optional[int] = Field(None, ge=0)
    protein_ingredients_low: Optional[int] = Field(None, ge=0)
    protein_quality_class: Optional[QualityClassEnum] = None

    # Fat Ingredients
    fat_ingredients_all: Optional[str] = None
    fat_ingredients_high: Optional[int] = Field(None, ge=0)
    fat_ingredients_good: Optional[int] = Field(None, ge=0)
    fat_ingredients_low: Optional[int] = Field(None, ge=0)
    fat_quality_class: Optional[QualityClassEnum] = None

    # Carb Ingredients
    carb_ingredients_all: Optional[str] = None
    carb_ingredients_high: Optional[int] = Field(None, ge=0)
    carb_ingredients_good: Optional[int] = Field(None, ge=0)
    carb_ingredients_moderate: Optional[int] = Field(None, ge=0)
    carb_ingredients_low: Optional[int] = Field(None, ge=0)
    carb_quality_class: Optional[QualityClassEnum] = None

    # Fiber Ingredients
    fiber_ingredients_all: Optional[str] = None
    fiber_ingredients_high: Optional[int] = Field(None, ge=0)
    fiber_ingredients_good: Optional[int] = Field(None, ge=0)
    fiber_ingredients_moderate: Optional[int] = Field(None, ge=0)
    fiber_ingredients_low: Optional[int] = Field(None, ge=0)
    fiber_quality_class: Optional[QualityClassEnum] = None

    # Dirty Dozen and Additives
    dirty_dozen_ingredients: Optional[str] = None
    dirty_dozen_ingredients_count: Optional[int] = Field(None, ge=0)
    synthetic_nutrition_addition: Optional[str] = None
    synthetic_nutrition_addition_count: Optional[int] = Field(None, ge=0)
    longevity_additives: Optional[str] = None
    longevity_additives_count: Optional[int] = Field(None, ge=0)

    # Storage and Shelf Life
    food_storage: Optional[FoodStorageEnum] = None
    food_storage_reason: Optional[str] = None
    packaging_size: Optional[PackagingSizeEnum] = None
    shelf_life_thawed: Optional[ShelfLifeEnum] = None

    # Metadata
    processor_version: Optional[str] = Field(None, max_length=50)


class ProcessedProductCreate(ProcessedProductBase):
    """Schema for creating a new processed product record."""

    product_detail_id: int = Field(
        ..., gt=0, description="Foreign key to product_details.id"
    )


class ProcessedProductUpdate(ProcessedProductBase):
    """Schema for updating an existing processed product record."""

    pass


class ProcessedProductInDB(ProcessedProductBase):
    """Schema for processed product as stored in database."""

    id: int
    product_detail_id: int
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProcessedProductResponse(ProcessedProductInDB):
    """Schema for processed product API response."""

    pass


class ProcessedProductListResponse(BaseModel):
    """Schema for paginated list of processed products."""

    items: list[ProcessedProductResponse]
    total: int
    page: int
    page_size: int

    model_config = ConfigDict(from_attributes=True)
