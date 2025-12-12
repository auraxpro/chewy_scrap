"""
Products View schemas for the Dog Food Scoring API.

This module contains Pydantic schemas for the final products view
that combines data from multiple tables.
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ProductListItemResponse(BaseModel):
    """Simplified schema for product list response with only id and name."""

    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product Name")

    class Config:
        populate_by_name = True
        from_attributes = True


class ProductViewResponse(BaseModel):
    """Schema for product view response matching the final products view."""

    product_id: Optional[int] = Field(None, description="Product ID")
    brand_website: Optional[str] = Field(None, description="Brand Website")
    product_detail_page: Optional[str] = Field(None, description="Product Detail Page")
    product_name: Optional[str] = Field(None, description="Product Name")
    flavors_recipe: Optional[str] = Field(None, description="Flavors/Recipe")
    food_category: Optional[str] = Field(None, description="Food Category")
    sourcing_integrity: Optional[str] = Field(None, description="Sourcing Integrity")
    processing_method_1: Optional[str] = Field(None, description="Processing Method 1")
    processing_method_2: Optional[str] = Field(None, description="Processing Method 2")
    processing_adulteration_method: Optional[str] = Field(None, description="Processing/Adulteration Method")
    guaranteed_analysis_crude_protein_pct: Optional[Decimal] = Field(None, description="Guaranteed Analysis - Crude Protein %")
    guaranteed_analysis_crude_fat_pct: Optional[Decimal] = Field(None, description="Guaranteed Analysis - Crude Fat %")
    guaranteed_analysis_crude_fiber_pct: Optional[Decimal] = Field(None, description="Guaranteed Analysis - Crude Fiber %")
    guaranteed_analysis_crude_moisture_pct: Optional[Decimal] = Field(None, description="Guaranteed Analysis - Crude Moisture %")
    guaranteed_analysis_crude_ash_pct: Optional[Decimal] = Field(None, description="Guaranteed Analysis - Crude Ash %")
    starchy_carb_pct: Optional[Decimal] = Field(None, description="Starchy Carb %")
    nutritionally_adequate: Optional[str] = Field(None, description="Nutritionally Adequate")
    ingredients_all: Optional[str] = Field(None, description="Ingredients (All)")
    protein_ingredients_all: Optional[str] = Field(None, description="Protein Ingredients (All)")
    protein_ingredients_high: Optional[int] = Field(None, description="Protein Ingredients (High)")
    protein_ingredients_good: Optional[int] = Field(None, description="Protein Ingredients (Good)")
    protein_ingredients_moderate: Optional[int] = Field(None, description="Protein Ingredients (Moderate)")
    protein_ingredients_low: Optional[int] = Field(None, description="Protein Ingredients (Low)")
    protein_quality_class: Optional[str] = Field(None, description="Protein Quality Class")
    fat_ingredients_all: Optional[str] = Field(None, description="Fat Ingredients (All)")
    fat_ingredients_high: Optional[int] = Field(None, description="Fat Ingredients (High)")
    fat_ingredients_good: Optional[int] = Field(None, description="Fat Ingredients (Good)")
    fat_ingredients_low: Optional[int] = Field(None, description="Fat Ingredients (Low)")
    fat_quality_class: Optional[str] = Field(None, description="Fat Quality Class")
    carb_ingredients_all: Optional[str] = Field(None, description="Carb Ingredients (All)")
    carb_ingredients_high: Optional[int] = Field(None, description="Carb Ingredients (High)")
    carb_ingredients_good: Optional[int] = Field(None, description="Carb Ingredients (Good)")
    carb_ingredients_moderate: Optional[int] = Field(None, description="Carb Ingredients (Moderate)")
    carb_ingredients_low: Optional[int] = Field(None, description="Carb Ingredients (Low)")
    carb_quality_class: Optional[str] = Field(None, description="Carb Quality Class")
    fiber_ingredients_all: Optional[str] = Field(None, description="Fiber Ingredients (All)")
    fiber_ingredients_high: Optional[int] = Field(None, description="Fiber Ingredients (High)")
    fiber_ingredients_good: Optional[int] = Field(None, description="Fiber Ingredients (Good)")
    fiber_ingredients_moderate: Optional[int] = Field(None, description="Fiber Ingredients (Moderate)")
    fiber_ingredients_low: Optional[int] = Field(None, description="Fiber Ingredients (Low)")
    fiber_quality_class: Optional[str] = Field(None, description="Fiber Quality Class")
    dirty_dozen_ingredients: Optional[str] = Field(None, description="Dirty Dozen Ingredients")
    dirty_dozen_ingredients_count: Optional[int] = Field(None, description="Dirty Dozen Ingredients Count")
    synthetic_nutrition_addition: Optional[str] = Field(None, description="Synthetic Nutrition Addition")
    synthetic_nutrition_addition_count: Optional[int] = Field(None, description="Synthetic Nutrition Addition Count")
    longevity_additives: Optional[str] = Field(None, description="Longevity Additives")
    longevity_additives_count: Optional[int] = Field(None, description="Longevity Additives Count")
    food_storage: Optional[str] = Field(None, description="Food Storage")
    packaging_size: Optional[str] = Field(None, description="Packaging Size")
    shelf_life: Optional[str] = Field(None, description="Shelf Life (Thawed)")

    class Config:
        populate_by_name = True
        from_attributes = True

    @classmethod
    def from_dict(cls, data: dict):
        """Create instance from dictionary with column name mapping."""
        # Map database column names (with spaces) to schema field names
        mapping = {
            "Product ID": "product_id",
            "Brand Website": "brand_website",
            "Product Detail Page": "product_detail_page",
            "Product Name": "product_name",
            "Flavors/Recipe": "flavors_recipe",
            "Food Category": "food_category",
            "Sourcing Integrity": "sourcing_integrity",
            "Processing Method 1": "processing_method_1",
            "Processing Method 2": "processing_method_2",
            "Processing/Adulteration Method": "processing_adulteration_method",
            "Guaranteed Analysis - Crude Protein %": "guaranteed_analysis_crude_protein_pct",
            "Guaranteed Analysis - Crude Fat %": "guaranteed_analysis_crude_fat_pct",
            "Guaranteed Analysis - Crude Fiber %": "guaranteed_analysis_crude_fiber_pct",
            "Guaranteed Analysis - Crude Moisture %": "guaranteed_analysis_crude_moisture_pct",
            "Guaranteed Analysis - Crude Ash %": "guaranteed_analysis_crude_ash_pct",
            "Starchy Carb %": "starchy_carb_pct",
            "Nutritionally Adequate": "nutritionally_adequate",
            "Ingredients (All)": "ingredients_all",
            "Protein Ingredients (All)": "protein_ingredients_all",
            "Protein Ingredients (High)": "protein_ingredients_high",
            "Protein Ingredients (Good)": "protein_ingredients_good",
            "Protein Ingredients (Moderate)": "protein_ingredients_moderate",
            "Protein Ingredients (Low)": "protein_ingredients_low",
            "Protein Quality Class": "protein_quality_class",
            "Fat Ingredients (All)": "fat_ingredients_all",
            "Fat Ingredients (High)": "fat_ingredients_high",
            "Fat Ingredients (Good)": "fat_ingredients_good",
            "Fat Ingredients (Low)": "fat_ingredients_low",
            "Fat Quality Class": "fat_quality_class",
            "Carb Ingredients (All)": "carb_ingredients_all",
            "Carb Ingredients (High)": "carb_ingredients_high",
            "Carb Ingredients (Good)": "carb_ingredients_good",
            "Carb Ingredients (Moderate)": "carb_ingredients_moderate",
            "Carb Ingredients (Low)": "carb_ingredients_low",
            "Carb Quality Class": "carb_quality_class",
            "Fiber Ingredients (All)": "fiber_ingredients_all",
            "Fiber Ingredients (High)": "fiber_ingredients_high",
            "Fiber Ingredients (Good)": "fiber_ingredients_good",
            "Fiber Ingredients (Moderate)": "fiber_ingredients_moderate",
            "Fiber Ingredients (Low)": "fiber_ingredients_low",
            "Fiber Quality Class": "fiber_quality_class",
            "Dirty Dozen Ingredients": "dirty_dozen_ingredients",
            "Dirty Dozen Ingredients Count": "dirty_dozen_ingredients_count",
            "Synthetic Nutrition Addition": "synthetic_nutrition_addition",
            "Synthetic Nutrition Addition Count": "synthetic_nutrition_addition_count",
            "Longevity Additives": "longevity_additives",
            "Longevity Additives Count": "longevity_additives_count",
            "Food Storage": "food_storage",
            "Packaging Size": "packaging_size",
            "Shelf Life (Thawed)": "shelf_life",
        }
        
        mapped_data = {}
        for key, value in data.items():
            mapped_key = mapping.get(key, key.lower().replace(" ", "_").replace("/", "_").replace("-", "_").replace("(", "").replace(")", "").replace("%", "pct"))
            mapped_data[mapped_key] = value
        
        return cls(**mapped_data)
