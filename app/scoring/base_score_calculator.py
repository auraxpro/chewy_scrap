"""
Base Score Calculator for Dog Food Products.

This module implements Phase 1 of the scoring system - calculating the Base Score
that reflects the intrinsic quality of the food. The Base Score is calculated once,
stored in the database, and never recalculated at runtime.

Base Score Formula:
BaseScore = clamp(100 - all base deductions + longevity additive bonus, 0, 100)

All deductions are additive and capped at their maximum values.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.product import ProcessedProduct


class BaseScoreCalculator:
    """
    Calculator for Base Score (Phase 1) - intrinsic food quality score.
    
    The Base Score includes ONLY food-intrinsic factors:
    - Food Category Deduction (max 20)
    - Sourcing Integrity Deduction (max 15)
    - Processing Method Deduction (max 17)
    - Nutritionally Adequate Deduction (max 14)
    - Starchy Carbohydrate Percent Deduction (max 14)
    - Ingredient Quality - Protein (max 9)
    - Ingredient Quality - Fats (max 9)
    - Ingredient Quality - Carbohydrates (max 9)
    - Ingredient Quality - Fiber (max 9)
    - Dirty Dozen Ingredients Deduction (max 12)
    - Synthetic Nutrition Addition Deduction (max 9)
    - Longevity Additives Bonus (max +4)
    """

    # Food Category Deductions (MAX 20)
    FOOD_CATEGORY_DEDUCTIONS = {
        "Raw": 0,
        "Fresh": 4,
        "Dry": 13,
        "Wet": 13,
        "Soft": 13,
    }

    # Sourcing Integrity Deductions (MAX 15)
    SOURCING_INTEGRITY_DEDUCTIONS = {
        "Human Grade (organic)": 0,
        "Human Grade": 3,
        "Feed Grade": 10,
    }

    # Processing Method Deductions (MAX 17) - Use highest applicable
    PROCESSING_METHOD_DEDUCTIONS = {
        "Uncooked (Not Frozen)": 0,
        "Uncooked (Flash Frozen)": 1,
        "Uncooked (Frozen)": 2,
        "Lightly Cooked (Not Frozen)": 3,
        "Lightly Cooked (Frozen)": 4,
        "Freeze Dried": 5,
        "Air Dried": 7,
        "Dehydrated": 8,
        "Baked": 11,
        "Extruded": 15,
        "Retorted": 15,
    }

    # Nutritionally Adequate Deductions (MAX 14)
    NUTRITIONALLY_ADEQUATE_DEDUCTIONS = {
        "Yes": 0,
        "No": 10,
    }

    # Starchy Carbohydrate Percent Deductions (MAX 14)
    STARCHY_CARB_DEDUCTIONS = [
        (None, 10, 0),      # < 10%
        (10, 15, 2),        # 10-15%
        (16, 20, 4),        # 16-20%
        (21, 25, 6),        # 21-25%
        (26, 30, 8),        # 26-30%
        (30, None, 10),     # >= 30%
    ]

    # Ingredient Quality Tier Weights
    TIER_WEIGHTS = {
        "High": 0,
        "Good": 2,
        "Moderate": 3,
        "Low": 5,
    }

    # Dirty Dozen Ingredients Deductions (MAX 12)
    DIRTY_DOZEN_DEDUCTIONS = [
        (0, 0, 0),      # 0 ingredients
        (1, 2, 2),      # 1-2 ingredients
        (3, 5, 5),      # 3-5 ingredients
        (6, 9, 8),      # 6-9 ingredients
        (10, None, 9),  # 10+ ingredients
    ]

    # Synthetic Nutrition Addition Deductions (MAX 9)
    SYNTHETIC_NUTRITION_DEDUCTIONS = [
        (0, 3, 0),      # 0-3 added synthetics
        (4, 6, 2),      # 4-6 added synthetics
        (7, 10, 3),     # 7-10 added synthetics
        (11, None, 5),  # 11+ added synthetics
    ]

    # Longevity Additives Bonus (MAX +4)
    LONGEVITY_ADDITIVES_BONUS = [
        (0, 0, 0),      # 0 additives
        (1, 3, 2),      # 1-3 additives
        (4, 7, 3),      # 4-7 additives
        (7, None, 4),   # 7+ additives
    ]

    def __init__(self, db: Session):
        """
        Initialize the base score calculator.
        
        Args:
            db: Database session
        """
        self.db = db

    def calculate_base_score(self, processed_product: ProcessedProduct) -> Optional[float]:
        """
        Calculate the base score for a processed product.
        
        Args:
            processed_product: ProcessedProduct instance
            
        Returns:
            Base score (0-100) or None if required data is missing
        """
        # Start with 100
        base_score = 100.0
        
        # Track missing data for QA
        missing_data = []
        
        # 1. Food Category Deduction (MAX 20)
        food_category_deduction = self._calculate_food_category_deduction(
            processed_product.food_category
        )
        if food_category_deduction is None:
            missing_data.append("food_category")
        else:
            base_score -= food_category_deduction
            print('food_category_deduction:')
            print(food_category_deduction)
        
        # 2. Sourcing Integrity Deduction (MAX 15)
        sourcing_deduction = self._calculate_sourcing_integrity_deduction(
            processed_product.sourcing_integrity
        )
        if sourcing_deduction is None:
            missing_data.append("sourcing_integrity")
        else:
            base_score -= sourcing_deduction
            print('sourcing_deduction:')
            print(sourcing_deduction)
        
        # 3. Processing Method Deduction (MAX 17) - Use highest applicable
        processing_deduction = self._calculate_processing_method_deduction(
            processed_product.processing_adulteration_method
        )
        if processing_deduction is None:
            missing_data.append("processing_adulteration_method")
        else:
            base_score -= processing_deduction
            print('processing_deduction:')
            print(processing_deduction)
        
        # 4. Nutritionally Adequate Deduction (MAX 14)
        nutritionally_adequate_deduction = self._calculate_nutritionally_adequate_deduction(
            processed_product.nutritionally_adequate
        )
        if nutritionally_adequate_deduction is None:
            missing_data.append("nutritionally_adequate")
        else:
            base_score -= nutritionally_adequate_deduction
            print('nutritionally_adequate_deduction:')
            print(nutritionally_adequate_deduction)
        
        # 5. Starchy Carbohydrate Percent Deduction (MAX 14)
        starchy_carb_deduction = self._calculate_starchy_carb_deduction(
            processed_product.starchy_carb_pct
        )
        if starchy_carb_deduction is None:
            missing_data.append("starchy_carb_pct")
        else:
            base_score -= starchy_carb_deduction
            print('starchy_carb_deduction:')
            print(starchy_carb_deduction)
        
        # 6. Ingredient Quality - Protein (MAX 9)
        protein_deduction = self._calculate_ingredient_quality_deduction(
            high_count=processed_product.protein_ingredients_high or 0,
            good_count=processed_product.protein_ingredients_good or 0,
            moderate_count=processed_product.protein_ingredients_moderate or 0,
            low_count=processed_product.protein_ingredients_low or 0,
            max_deduction=9,
        )
        base_score -= protein_deduction
        print('protein_deduction:')
        print(protein_deduction)
        
        # 7. Ingredient Quality - Fats (MAX 9)
        fat_deduction = self._calculate_ingredient_quality_deduction(
            high_count=processed_product.fat_ingredients_high or 0,
            good_count=processed_product.fat_ingredients_good or 0,
            moderate_count=0,  # Fats don't have moderate tier
            low_count=processed_product.fat_ingredients_low or 0,
            max_deduction=9,
        )
        base_score -= fat_deduction
        print('fat_deduction:')
        print(fat_deduction)
        
        # 8. Ingredient Quality - Carbohydrates (MAX 9)
        carb_deduction = self._calculate_ingredient_quality_deduction(
            high_count=processed_product.carb_ingredients_high or 0,
            good_count=processed_product.carb_ingredients_good or 0,
            moderate_count=processed_product.carb_ingredients_moderate or 0,
            low_count=processed_product.carb_ingredients_low or 0,
            max_deduction=9,
        )
        base_score -= carb_deduction
        print('carb_deduction:')
        print(carb_deduction)
        
        # 9. Ingredient Quality - Fiber (MAX 9)
        fiber_deduction = self._calculate_ingredient_quality_deduction(
            high_count=processed_product.fiber_ingredients_high or 0,
            good_count=processed_product.fiber_ingredients_good or 0,
            moderate_count=processed_product.fiber_ingredients_moderate or 0,
            low_count=processed_product.fiber_ingredients_low or 0,
            max_deduction=9,
        )
        base_score -= fiber_deduction
        print('fiber_deduction:')
        print(fiber_deduction)
        
        # 10. Dirty Dozen Ingredients Deduction (MAX 12)
        dirty_dozen_deduction = self._calculate_dirty_dozen_deduction(
            processed_product.dirty_dozen_ingredients_count or 0
        )
        base_score -= dirty_dozen_deduction
        print('dirty_dozen_deduction:')
        print(dirty_dozen_deduction)
        
        # 11. Synthetic Nutrition Addition Deduction (MAX 9)
        synthetic_deduction = self._calculate_synthetic_nutrition_deduction(
            processed_product.synthetic_nutrition_addition_count or 0
        )
        base_score -= synthetic_deduction
        print('synthetic_deduction:')
        print(synthetic_deduction)
        
        # 12. Longevity Additives Bonus (MAX +4) - ADDITIVE
        longevity_bonus = self._calculate_longevity_additives_bonus(
            processed_product.longevity_additives_count or 0
        )
        base_score += longevity_bonus
        print('longevity_bonus:')
        print(longevity_bonus)
        
        # If critical data is missing, return None (should go to QA)
        if missing_data:
            return None
        
        # Clamp to 0-100
        return max(0.0, min(100.0, base_score))

    def _calculate_food_category_deduction(self, food_category: Optional[str]) -> Optional[float]:
        """Calculate food category deduction (MAX 20)."""
        if not food_category:
            return None
        
        # Handle "Other" category - should be sent to QA
        if food_category == "Other":
            return None
        
        return float(self.FOOD_CATEGORY_DEDUCTIONS.get(food_category, 0))

    def _calculate_sourcing_integrity_deduction(self, sourcing_integrity: Optional[str]) -> Optional[float]:
        """Calculate sourcing integrity deduction (MAX 15)."""
        if not sourcing_integrity:
            return None
        
        # Handle "Other" category - should be sent to QA
        if sourcing_integrity == "Other":
            return None
        
        return float(self.SOURCING_INTEGRITY_DEDUCTIONS.get(sourcing_integrity, 0))

    def _calculate_processing_method_deduction(self, processing_method: Optional[str]) -> Optional[float]:
        """Calculate processing method deduction (MAX 17) - use highest applicable."""
        if not processing_method:
            return None
        
        # Handle "Other" category - should be sent to QA
        if processing_method == "Other":
            return None
        
        return float(self.PROCESSING_METHOD_DEDUCTIONS.get(processing_method, 0))

    def _calculate_nutritionally_adequate_deduction(self, nutritionally_adequate: Optional[str]) -> Optional[float]:
        """Calculate nutritionally adequate deduction (MAX 14)."""
        if not nutritionally_adequate:
            return None
        
        # Handle "Other" category - should be sent to QA
        if nutritionally_adequate == "Other":
            return None
        
        return float(self.NUTRITIONALLY_ADEQUATE_DEDUCTIONS.get(nutritionally_adequate, 0))

    def _calculate_starchy_carb_deduction(self, starchy_carb_pct: Optional[float]) -> Optional[float]:
        """Calculate starchy carbohydrate percent deduction (MAX 14)."""
        if starchy_carb_pct is None:
            return None
        
        for min_val, max_val, deduction in self.STARCHY_CARB_DEDUCTIONS:
            if min_val is None:
                # < 10%
                if starchy_carb_pct < max_val:
                    return float(deduction)
            elif max_val is None:
                # >= 30%
                if starchy_carb_pct >= min_val:
                    return float(deduction)
            else:
                # Range check
                if min_val <= starchy_carb_pct <= max_val:
                    return float(deduction)
        
        return 0.0

    def _calculate_ingredient_quality_deduction(
        self,
        high_count: int,
        good_count: int,
        moderate_count: int,
        low_count: int,
        max_deduction: int = 9,
    ) -> float:
        """
        Calculate ingredient quality deduction.
        
        Formula: (High*0 + Good*2 + Moderate*3 + Low*5) / TotalIngredients
        Cap result at max_deduction.
        
        Args:
            high_count: Number of high quality ingredients
            good_count: Number of good quality ingredients
            moderate_count: Number of moderate quality ingredients
            low_count: Number of low quality ingredients
            max_deduction: Maximum deduction (default 9)
            
        Returns:
            Deduction value (0 to max_deduction)
        """
        total_ingredients = high_count + good_count + moderate_count + low_count
        
        if total_ingredients == 0:
            return 0.0
        
        weighted_sum = (
            (high_count * self.TIER_WEIGHTS["High"]) +
            (good_count * self.TIER_WEIGHTS["Good"]) +
            (moderate_count * self.TIER_WEIGHTS["Moderate"]) +
            (low_count * self.TIER_WEIGHTS["Low"])
        )
        
        deduction = weighted_sum / total_ingredients
        
        # Cap at max_deduction
        return min(float(max_deduction), deduction)

    def _calculate_dirty_dozen_deduction(self, count: int) -> float:
        """Calculate dirty dozen ingredients deduction (MAX 12)."""
        for min_val, max_val, deduction in self.DIRTY_DOZEN_DEDUCTIONS:
            if max_val is None:
                # 10+ ingredients
                if count >= min_val:
                    return float(deduction)
            elif min_val == max_val == 0:
                # Exact match (0 ingredients)
                if count == 0:
                    return float(deduction)
            else:
                # Range check
                if min_val <= count <= max_val:
                    return float(deduction)
        
        return 0.0

    def _calculate_synthetic_nutrition_deduction(self, count: int) -> float:
        """Calculate synthetic nutrition addition deduction (MAX 9)."""
        for min_val, max_val, deduction in self.SYNTHETIC_NUTRITION_DEDUCTIONS:
            if max_val is None:
                # 11+ added synthetics
                if count >= min_val:
                    return float(deduction)
            else:
                # Range check
                if min_val <= count <= max_val:
                    return float(deduction)
        
        return 0.0

    def _calculate_longevity_additives_bonus(self, count: int) -> float:
        """Calculate longevity additives bonus (MAX +4)."""
        for min_val, max_val, bonus in self.LONGEVITY_ADDITIVES_BONUS:
            if max_val is None:
                # 7+ additives
                if count >= min_val:
                    return float(bonus)
            elif min_val == max_val == 0:
                # Exact match (0 additives)
                if count == 0:
                    return float(bonus)
            else:
                # Range check
                if min_val <= count <= max_val:
                    return float(bonus)
        
        return 0.0

    def calculate_and_save_base_score(self, processed_product: ProcessedProduct) -> Optional[float]:
        """
        Calculate and save base score to database.
        
        Args:
            processed_product: ProcessedProduct instance
            
        Returns:
            Base score (0-100) or None if calculation failed
        """
        base_score = self.calculate_base_score(processed_product)
        
        if base_score is not None:
            processed_product.base_score = base_score
            self.db.commit()
        
        return base_score

