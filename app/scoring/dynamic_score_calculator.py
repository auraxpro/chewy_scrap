"""
Dynamic Score Calculator for Dog Food Products (Phase 2).

This module implements Phase 2 of the scoring system - calculating the Final Score
by applying user-dependent handling deductions to the Base Score in real time.

Final Score Formula:
FinalScore = clamp(BaseScore - FoodStorageDeduction - PackagingSizeDeduction - ThawedShelfLifeDeduction, 0, 100)

These deductions are NEVER stored permanently and are calculated at runtime only.
"""

from typing import Optional

from app.models.product import (
    FoodStorageEnum,
    PackagingSizeEnum,
    ProcessedProduct,
    ShelfLifeEnum,
)


class DynamicScoreCalculator:
    """
    Calculator for Final Score (Phase 2) - applies user-dependent handling deductions.
    
    The Final Score adjusts the Base Score based on how the user stores and handles the food:
    - Food Storage Deduction (max 4)
    - Packaging Size Deduction (max 7)
    - Thawed Shelf Life Deduction (max 7)
    
    Dynamic field display rules determine which deductions apply based on:
    - Food Category (Raw, Fresh, Dry, Wet, Soft)
    - Processing Method (for Raw foods)
    """

    # Food Storage Deductions (MAX 4)
    FOOD_STORAGE_DEDUCTIONS = {
        FoodStorageEnum.FREEZER: 0,
        FoodStorageEnum.REFRIGERATOR: 0,
        FoodStorageEnum.COOL_DRY_AWAY: 1,
        FoodStorageEnum.COOL_DRY_NOT_AWAY: 3,
    }

    # Packaging Size Deductions (MAX 7)
    PACKAGING_SIZE_DEDUCTIONS = {
        PackagingSizeEnum.ONE_MONTH: 0,
        PackagingSizeEnum.TWO_MONTH: 3,
        PackagingSizeEnum.THREE_PLUS_MONTH: 4,
    }

    # Thawed Shelf Life Deductions (MAX 7)
    SHELF_LIFE_DEDUCTIONS = {
        ShelfLifeEnum.SEVEN_DAY: 0,
        ShelfLifeEnum.EIGHT_TO_FOURTEEN_DAY: 3,
        ShelfLifeEnum.FIFTEEN_PLUS_DAY: 4,
    }

    # Scoring Range Classifications (Display Only)
    SCORE_RANGES = {
        "Optimal": (85, 100),
        "Good": (70, 84),
        "Fair": (50, 69),
        "Poor": (30, 49),
        "At Risk": (0, 29),
    }

    def calculate_final_score(
        self,
        base_score: float,
        food_category: Optional[str],
        processing_method: Optional[str],
        food_storage: Optional[FoodStorageEnum] = None,
        packaging_size: Optional[PackagingSizeEnum] = None,
        shelf_life: Optional[ShelfLifeEnum] = None,
    ) -> dict:
        """
        Calculate final score with dynamic handling deductions.
        
        Args:
            base_score: Pre-calculated base score (0-100)
            food_category: Food category (Raw, Fresh, Dry, Wet, Soft)
            processing_method: Processing method (for Raw foods)
            food_storage: Food storage method (optional)
            packaging_size: Packaging size (optional)
            shelf_life: Thawed shelf life (optional)
            
        Returns:
            Dictionary containing:
            - final_score: Final score (0-100)
            - classification: Score classification (Optimal, Good, Fair, Poor, At Risk)
            - deductions: Dictionary of applied deductions
            - applicable_fields: List of fields that apply to this product
        """
        if base_score is None:
            return {
                "final_score": None,
                "classification": None,
                "deductions": {},
                "applicable_fields": [],
                "error": "Base score not available",
            }

        # Determine which fields apply based on food category and processing method
        applicable_fields = self._get_applicable_fields(food_category, processing_method)

        # Calculate deductions
        deductions = {}
        total_deduction = 0.0

        # Food Storage Deduction
        if "food_storage" in applicable_fields and food_storage:
            deduction = self._calculate_food_storage_deduction(food_storage)
            deductions["food_storage"] = deduction
            total_deduction += deduction

        # Packaging Size Deduction
        if "packaging_size" in applicable_fields and packaging_size:
            deduction = self._calculate_packaging_size_deduction(packaging_size)
            deductions["packaging_size"] = deduction
            total_deduction += deduction

        # Thawed Shelf Life Deduction
        if "thawed_shelf_life" in applicable_fields and shelf_life:
            deduction = self._calculate_shelf_life_deduction(shelf_life)
            deductions["thawed_shelf_life"] = deduction
            total_deduction += deduction

        # Calculate final score
        final_score = max(0.0, min(100.0, base_score - total_deduction))

        # Determine classification
        classification = self._get_score_classification(final_score)

        return {
            "final_score": final_score,
            "base_score": base_score,
            "classification": classification,
            "deductions": deductions,
            "total_deduction": total_deduction,
            "applicable_fields": applicable_fields,
        }

    def _get_applicable_fields(
        self, food_category: Optional[str], processing_method: Optional[str]
    ) -> list:
        """
        Determine which dynamic fields apply based on food category and processing method.
        
        Rules:
        - Wet Food: No dynamic fields
        - Soft Food: No dynamic fields
        - Dry Food: Food Storage and Packaging Size
        - Fresh Food: Thawed Shelf Life
        - Raw Food: Processing dependent
            - Uncooked (Not Frozen) → Thawed Shelf Life
            - Uncooked (Frozen) → Thawed Shelf Life
            - Uncooked (Flash Frozen) → Food Storage and Packaging Size
            - Freeze Dried → Food Storage and Packaging Size
            - Dehydrated → Food Storage and Packaging Size
        """
        if not food_category:
            return []

        food_category = food_category.strip()

        # Wet Food - No dynamic fields
        if food_category == "Wet":
            return []

        # Soft Food - No dynamic fields
        if food_category == "Soft":
            return []

        # Dry Food - Food Storage and Packaging Size
        if food_category == "Dry":
            return ["food_storage", "packaging_size"]

        # Fresh Food - Thawed Shelf Life
        if food_category == "Fresh":
            return ["thawed_shelf_life"]

        # Raw Food - Processing dependent
        if food_category == "Raw":
            if not processing_method:
                return []

            processing_method = processing_method.strip()

            # Uncooked (Not Frozen) → Thawed Shelf Life
            if processing_method == "Uncooked (Not Frozen)":
                return ["thawed_shelf_life"]

            # Uncooked (Frozen) → Thawed Shelf Life
            if processing_method == "Uncooked (Frozen)":
                return ["thawed_shelf_life"]

            # Uncooked (Flash Frozen) → Food Storage and Packaging Size
            if processing_method == "Uncooked (Flash Frozen)":
                return ["food_storage", "packaging_size"]

            # Freeze Dried → Food Storage and Packaging Size
            if processing_method == "Freeze Dried":
                return ["food_storage", "packaging_size"]

            # Dehydrated → Food Storage and Packaging Size
            if processing_method == "Dehydrated":
                return ["food_storage", "packaging_size"]

            # Default for other Raw processing methods
            return []

        # Other category - no dynamic fields
        return []

    def _calculate_food_storage_deduction(self, food_storage: FoodStorageEnum) -> float:
        """Calculate food storage deduction (MAX 4)."""
        return float(self.FOOD_STORAGE_DEDUCTIONS.get(food_storage, 0))

    def _calculate_packaging_size_deduction(self, packaging_size: PackagingSizeEnum) -> float:
        """Calculate packaging size deduction (MAX 7)."""
        return float(self.PACKAGING_SIZE_DEDUCTIONS.get(packaging_size, 0))

    def _calculate_shelf_life_deduction(self, shelf_life: ShelfLifeEnum) -> float:
        """Calculate thawed shelf life deduction (MAX 7)."""
        return float(self.SHELF_LIFE_DEDUCTIONS.get(shelf_life, 0))

    def _get_score_classification(self, score: float) -> str:
        """Get score classification based on score range."""
        for classification, (min_score, max_score) in self.SCORE_RANGES.items():
            if min_score <= score <= max_score:
                return classification
        return "At Risk"

    def get_score_range_info(self) -> dict:
        """Get information about score ranges for display."""
        return {
            "ranges": {
                classification: {
                    "min": min_score,
                    "max": max_score,
                    "description": self._get_range_description(classification),
                }
                for classification, (min_score, max_score) in self.SCORE_RANGES.items()
            }
        }

    def _get_range_description(self, classification: str) -> str:
        """Get description for score range."""
        descriptions = {
            "Optimal": "Excellent quality food",
            "Good": "Good quality food",
            "Fair": "Fair quality food",
            "Poor": "Poor quality food",
            "At Risk": "Food quality is at risk",
        }
        return descriptions.get(classification, "")

