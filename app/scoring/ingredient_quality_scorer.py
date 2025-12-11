"""
Ingredient Quality Scorer for Dog Food Products.

This module calculates ingredient quality scores based on weighted deduction formula
for four macro ingredient groups: Protein, Fat, Carbohydrates, and Fiber.

Scoring System:
- Each ingredient receives a Quality Tier (High, Good, Moderate, Low)
- Tier Point Values: High=0, Good=2, Moderate=3, Low=5
- Weighted Deduction = (Σ (Ingredient Count × Tier Point Value)) / Total Ingredients
- Final score starts at 100 and deductions are applied based on weighted average
"""

from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.models.product import ProcessedProduct, ProductList
from app.scoring.base_scorer import BaseScorer


class IngredientQualityScorer(BaseScorer):
    """
    Scorer for ingredient quality based on weighted deduction formula.
    
    Calculates scores for four macro groups:
    - Protein Quality
    - Fat Quality
    - Carbohydrate Quality
    - Fiber Quality
    
    Each group uses weighted deduction to determine final tier and deduction points.
    """

    # Tier Point Values
    TIER_POINT_HIGH = 0
    TIER_POINT_GOOD = 2
    TIER_POINT_MODERATE = 3
    TIER_POINT_LOW = 5

    # Tier Thresholds (for weighted average)
    TIER_THRESHOLD_HIGH_MAX = 1.00
    TIER_THRESHOLD_GOOD_MAX = 2.00
    TIER_THRESHOLD_MODERATE_MAX = 3.50

    # Final Deduction Points
    DEDUCTION_HIGH = 0
    DEDUCTION_GOOD = 2
    DEDUCTION_MODERATE = 3
    DEDUCTION_LOW = 5

    # Base Score (starting point)
    BASE_SCORE = 100.0

    def __init__(self, db: Session, weight: float = 0.35):
        """
        Initialize the ingredient quality scorer.

        Args:
            db: Database session
            weight: Weight of this scorer in overall score (default 0.35 = 35%)
        """
        super().__init__(db, weight)

    def get_component_name(self) -> str:
        """Get component name."""
        return "ingredient_quality"

    def can_score(self, product: ProductList) -> bool:
        """
        Check if product can be scored.

        Requires processed_products record with ingredient quality data.
        """
        if not super().can_score(product):
            return False

        # Check if processed data exists
        if not product.details:
            return False

        processed = (
            self.db.query(ProcessedProduct)
            .filter_by(product_detail_id=product.details.id)
            .first()
        )

        return processed is not None and processed.ingredients_all is not None

    def calculate_score(self, product: ProductList) -> float:
        """
        Calculate ingredient quality score.

        Args:
            product: ProductList instance

        Returns:
            Score between 0.0 and 100.0
        """
        if not self.can_score(product):
            return 0.0

        # Get processed product data
        processed = (
            self.db.query(ProcessedProduct)
            .filter_by(product_detail_id=product.details.id)
            .first()
        )

        if not processed:
            return 0.0

        # Calculate weighted deductions for each macro group
        protein_deduction = self._calculate_weighted_deduction(
            high_count=processed.protein_ingredients_high or 0,
            good_count=processed.protein_ingredients_good or 0,
            moderate_count=processed.protein_ingredients_moderate or 0,
            low_count=processed.protein_ingredients_low or 0,
        )

        fat_deduction = self._calculate_weighted_deduction(
            high_count=processed.fat_ingredients_high or 0,
            good_count=processed.fat_ingredients_good or 0,
            moderate_count=processed.fat_ingredients_moderate or 0,
            low_count=processed.fat_ingredients_low or 0,
        )

        carb_deduction = self._calculate_weighted_deduction(
            high_count=processed.carb_ingredients_high or 0,
            good_count=processed.carb_ingredients_good or 0,
            moderate_count=processed.carb_ingredients_moderate or 0,
            low_count=processed.carb_ingredients_low or 0,
        )

        fiber_deduction = self._calculate_weighted_deduction(
            high_count=processed.fiber_ingredients_high or 0,
            good_count=processed.fiber_ingredients_good or 0,
            moderate_count=processed.fiber_ingredients_moderate or 0,
            low_count=processed.fiber_ingredients_low or 0,
        )

        # Calculate total deduction (average of all four groups)
        total_deduction = (
            protein_deduction + fat_deduction + carb_deduction + fiber_deduction
        ) / 4.0

        # Calculate final score
        final_score = self.BASE_SCORE - total_deduction

        # Ensure score is within valid range
        return self.validate_score(final_score)

    def _calculate_weighted_deduction(
        self,
        high_count: int,
        good_count: int,
        moderate_count: int,
        low_count: int,
    ) -> float:
        """
        Calculate weighted deduction for a macro group.

        Formula: Weighted Deduction = (Σ (Ingredient Count × Tier Point Value)) / Total Ingredients

        Args:
            high_count: Number of high quality ingredients
            good_count: Number of good quality ingredients
            moderate_count: Number of moderate quality ingredients
            low_count: Number of low quality ingredients

        Returns:
            Final deduction points (0, 2, 3, or 5)
        """
        # Calculate total ingredients
        total_ingredients = high_count + good_count + moderate_count + low_count

        # If no ingredients, return moderate deduction (default)
        if total_ingredients == 0:
            return float(self.DEDUCTION_MODERATE)

        # Calculate weighted average
        weighted_sum = (
            (high_count * self.TIER_POINT_HIGH)
            + (good_count * self.TIER_POINT_GOOD)
            + (moderate_count * self.TIER_POINT_MODERATE)
            + (low_count * self.TIER_POINT_LOW)
        )

        weighted_avg = weighted_sum / total_ingredients

        # Determine final tier based on thresholds
        if weighted_avg <= self.TIER_THRESHOLD_HIGH_MAX:
            return float(self.DEDUCTION_HIGH)
        elif weighted_avg <= self.TIER_THRESHOLD_GOOD_MAX:
            return float(self.DEDUCTION_GOOD)
        elif weighted_avg <= self.TIER_THRESHOLD_MODERATE_MAX:
            return float(self.DEDUCTION_MODERATE)
        else:
            return float(self.DEDUCTION_LOW)

    def get_score_details(self, product: ProductList) -> Optional[Dict]:
        """
        Get detailed breakdown of ingredient quality score.

        Args:
            product: ProductList instance

        Returns:
            Dictionary with detailed scoring breakdown
        """
        if not self.can_score(product):
            return None

        processed = (
            self.db.query(ProcessedProduct)
            .filter_by(product_detail_id=product.details.id)
            .first()
        )

        if not processed:
            return None

        # Calculate deductions for each group
        protein_deduction = self._calculate_weighted_deduction(
            high_count=processed.protein_ingredients_high or 0,
            good_count=processed.protein_ingredients_good or 0,
            moderate_count=processed.protein_ingredients_moderate or 0,
            low_count=processed.protein_ingredients_low or 0,
        )

        fat_deduction = self._calculate_weighted_deduction(
            high_count=processed.fat_ingredients_high or 0,
            good_count=processed.fat_ingredients_good or 0,
            moderate_count=processed.fat_ingredients_moderate or 0,
            low_count=processed.fat_ingredients_low or 0,
        )

        carb_deduction = self._calculate_weighted_deduction(
            high_count=processed.carb_ingredients_high or 0,
            good_count=processed.carb_ingredients_good or 0,
            moderate_count=processed.carb_ingredients_moderate or 0,
            low_count=processed.carb_ingredients_low or 0,
        )

        fiber_deduction = self._calculate_weighted_deduction(
            high_count=processed.fiber_ingredients_high or 0,
            good_count=processed.fiber_ingredients_good or 0,
            moderate_count=processed.fiber_ingredients_moderate or 0,
            low_count=processed.fiber_ingredients_low or 0,
        )

        # Calculate weighted averages for display
        protein_weighted_avg = self._calculate_weighted_average(
            high_count=processed.protein_ingredients_high or 0,
            good_count=processed.protein_ingredients_good or 0,
            moderate_count=processed.protein_ingredients_moderate or 0,
            low_count=processed.protein_ingredients_low or 0,
        )

        fat_weighted_avg = self._calculate_weighted_average(
            high_count=processed.fat_ingredients_high or 0,
            good_count=processed.fat_ingredients_good or 0,
            moderate_count=processed.fat_ingredients_moderate or 0,
            low_count=processed.fat_ingredients_low or 0,
        )

        carb_weighted_avg = self._calculate_weighted_average(
            high_count=processed.carb_ingredients_high or 0,
            good_count=processed.carb_ingredients_good or 0,
            moderate_count=processed.carb_ingredients_moderate or 0,
            low_count=processed.carb_ingredients_low or 0,
        )

        fiber_weighted_avg = self._calculate_weighted_average(
            high_count=processed.fiber_ingredients_high or 0,
            good_count=processed.fiber_ingredients_good or 0,
            moderate_count=processed.fiber_ingredients_moderate or 0,
            low_count=processed.fiber_ingredients_low or 0,
        )

        total_deduction = (
            protein_deduction + fat_deduction + carb_deduction + fiber_deduction
        ) / 4.0

        return {
            "base_score": self.BASE_SCORE,
            "protein": {
                "high_count": processed.protein_ingredients_high or 0,
                "good_count": processed.protein_ingredients_good or 0,
                "moderate_count": processed.protein_ingredients_moderate or 0,
                "low_count": processed.protein_ingredients_low or 0,
                "weighted_average": protein_weighted_avg,
                "deduction": protein_deduction,
            },
            "fat": {
                "high_count": processed.fat_ingredients_high or 0,
                "good_count": processed.fat_ingredients_good or 0,
                "moderate_count": processed.fat_ingredients_moderate or 0,
                "low_count": processed.fat_ingredients_low or 0,
                "weighted_average": fat_weighted_avg,
                "deduction": fat_deduction,
            },
            "carb": {
                "high_count": processed.carb_ingredients_high or 0,
                "good_count": processed.carb_ingredients_good or 0,
                "moderate_count": processed.carb_ingredients_moderate or 0,
                "low_count": processed.carb_ingredients_low or 0,
                "weighted_average": carb_weighted_avg,
                "deduction": carb_deduction,
            },
            "fiber": {
                "high_count": processed.fiber_ingredients_high or 0,
                "good_count": processed.fiber_ingredients_good or 0,
                "moderate_count": processed.fiber_ingredients_moderate or 0,
                "low_count": processed.fiber_ingredients_low or 0,
                "weighted_average": fiber_weighted_avg,
                "deduction": fiber_deduction,
            },
            "total_deduction": total_deduction,
            "final_score": self.BASE_SCORE - total_deduction,
            "dirty_dozen_count": processed.dirty_dozen_ingredients_count or 0,
            "synthetic_nutrition_count": processed.synthetic_nutrition_addition_count or 0,
        }

    def _calculate_weighted_average(
        self,
        high_count: int,
        good_count: int,
        moderate_count: int,
        low_count: int,
    ) -> float:
        """
        Calculate weighted average for a macro group.

        Args:
            high_count: Number of high quality ingredients
            good_count: Number of good quality ingredients
            moderate_count: Number of moderate quality ingredients
            low_count: Number of low quality ingredients

        Returns:
            Weighted average value
        """
        total_ingredients = high_count + good_count + moderate_count + low_count

        if total_ingredients == 0:
            return 0.0

        weighted_sum = (
            (high_count * self.TIER_POINT_HIGH)
            + (good_count * self.TIER_POINT_GOOD)
            + (moderate_count * self.TIER_POINT_MODERATE)
            + (low_count * self.TIER_POINT_LOW)
        )

        return weighted_sum / total_ingredients

