"""
Starchy Carb Processor

This module extracts nutrition values from guaranteed_analysis and calculates
starchy carb percentage for dog food products.

Feature name: Starchy Carb Process Feature

Extracts:
- crude_protein_pct
- crude_fat_pct
- crude_fiber_pct
- crude_moisture_pct
- crude_ash_pct
- starchy_carb_pct (calculated)

Calculation Formulas:
- Dry Food: carbs = 100 - (protein + fat + fiber + moisture + ash)
- Wet/Raw Food:
  Step 1: Wet Matter = 100 - (protein + fat + fiber + moisture + ash)
  Step 2: Dry Matter = 100 - Moisture
  Step 3: Carb % = (Wet Matter / Dry Matter) * 100

Usage:
    from app.processors.starchy_carb_processor import StarchyCarbProcessor

    processor = StarchyCarbProcessor(db_session)
    processor.process_single(product_detail_id)
    processor.process_all()
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import ProcessedProduct, ProductDetails


class StarchyCarbProcessor:
    """
    Processor for extracting nutrition values and calculating starchy carb percentage.
    """

    def __init__(self, db: Session, processor_version: str = "v1.0.0"):
        """
        Initialize the processor.

        Args:
            db: SQLAlchemy database session
            processor_version: Version string for tracking
        """
        self.db = db
        self.processor_version = processor_version

    def extract_nutrition_value(
        self, text: str, patterns: List[str], default: Optional[float] = None
    ) -> Optional[float]:
        """
        Extract a nutrition value from text using regex patterns.

        Args:
            text: Text to search in
            patterns: List of regex patterns to try
            default: Default value if not found (None = no default)

        Returns:
            Extracted float value or None/default
        """
        if not text:
            return default

        text = str(text).strip()
        if not text:
            return default

        # Try each pattern
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_str = match.group(1)
                try:
                    # Strip any remaining symbols and convert to float
                    value_str = value_str.replace(",", "").strip()
                    value = float(value_str)
                    return value
                except (ValueError, AttributeError):
                    continue

        return default

    def extract_all_nutrition_values(self, detail: ProductDetails) -> dict:
        """
        Extract all nutrition values from product details.

        Uses guaranteed_analysis as primary source, with fallbacks to:
        - details
        - more_details
        - specifications
        - product_name (last fallback)

        Args:
            detail: ProductDetails instance

        Returns:
            Dict with extracted values:
            {
                'crude_protein_pct': float or None,
                'crude_fat_pct': float or None,
                'crude_fiber_pct': float or None,
                'crude_moisture_pct': float or None,
                'crude_ash_pct': float or None,
            }
        """
        # Define regex patterns for each nutrient
        # Patterns handle formats like:
        # - "Crude Protein | 4.1%min"
        # - "Crude Protein | 37.0% (min)"
        # - "Protein: 28%"
        # - "28% protein"
        # Use non-greedy matching to find the first number after the keyword
        protein_patterns = [
            r"crude\s+protein.*?([0-9]+\.?[0-9]*)\s*%",
            r"protein.*?([0-9]+\.?[0-9]*)\s*%",
        ]
        fat_patterns = [
            r"crude\s+fat.*?([0-9]+\.?[0-9]*)\s*%",
            r"fat.*?([0-9]+\.?[0-9]*)\s*%",
        ]
        fiber_patterns = [
            r"crude\s+fiber.*?([0-9]+\.?[0-9]*)\s*%",
            r"fiber.*?([0-9]+\.?[0-9]*)\s*%",
        ]
        moisture_patterns = [
            r"moisture.*?([0-9]+\.?[0-9]*)\s*%",
        ]
        ash_patterns = [
            r"crude\s+ash.*?([0-9]+\.?[0-9]*)\s*%",
            r"ash.*?([0-9]+\.?[0-9]*)\s*%",
        ]

        # Build search text from all fields (in priority order)
        search_fields = []
        if detail.guaranteed_analysis:
            search_fields.append(detail.guaranteed_analysis)
        if detail.details:
            search_fields.append(detail.details)
        if detail.more_details:
            search_fields.append(detail.more_details)
        if detail.specifications:
            search_fields.append(detail.specifications)
        if detail.product_name:
            search_fields.append(detail.product_name)

        # Combine all fields into one search text
        search_text = " ".join(str(field) for field in search_fields if field)

        # Extract values
        crude_protein_pct = self.extract_nutrition_value(
            search_text, protein_patterns
        )
        crude_fat_pct = self.extract_nutrition_value(search_text, fat_patterns)
        crude_fiber_pct = self.extract_nutrition_value(search_text, fiber_patterns)
        crude_moisture_pct = self.extract_nutrition_value(
            search_text, moisture_patterns
        )
        # Ash defaults to 6.0% if missing
        crude_ash_pct = self.extract_nutrition_value(
            search_text, ash_patterns, default=6.0
        )

        return {
            "crude_protein_pct": crude_protein_pct,
            "crude_fat_pct": crude_fat_pct,
            "crude_fiber_pct": crude_fiber_pct,
            "crude_moisture_pct": crude_moisture_pct,
            "crude_ash_pct": crude_ash_pct,
        }

    def calculate_starchy_carbs(
        self,
        protein: Optional[float],
        fat: Optional[float],
        fiber: Optional[float],
        moisture: Optional[float],
        ash: Optional[float],
        food_category: Optional[str] = None,
    ) -> Optional[float]:
        """
        Calculate starchy carb percentage.

        For Dry Food:
            Formula: carbs = 100 - (protein + fat + fiber + moisture + ash)

        For Wet Food & Raw Food:
            Step 1: Wet Matter = 100 - (protein + fat + fiber + moisture + ash)
            Step 2: Dry Matter = 100 - Moisture
            Step 3: Carb % = (Wet Matter / Dry Matter) * 100

        Rules:
        1. Use extracted numeric values
        2. For Dry: If moisture missing, exclude it (assume null)
        3. For Wet/Raw: Moisture is required for conversion
        4. If ash missing: use default 6.0%
        5. Minimum resulting carbs cannot be negative
        6. Round to one decimal place

        Args:
            protein: Crude protein percentage
            fat: Crude fat percentage
            fiber: Crude fiber percentage
            moisture: Moisture percentage (can be None)
            ash: Ash percentage (defaults to 6.0 if None)
            food_category: Food category (Dry, Wet, Raw, Fresh, Soft, Other)

        Returns:
            Calculated starchy carb percentage or None if insufficient data
        """
        # Need at least protein, fat, and fiber to calculate
        if protein is None or fat is None or fiber is None:
            return None

        # Use default ash if not provided
        ash_value = ash if ash is not None else 6.0

        # Determine if this is Dry or Wet/Raw food
        # If food_category is not set, infer from moisture content:
        # High moisture (>70%) suggests Wet/Raw food
        is_dry = False
        is_wet_or_raw = False

        if food_category:
            is_dry = food_category.lower() == "dry"
            is_wet_or_raw = food_category.lower() in ["wet", "raw", "fresh"]
        elif moisture is not None and moisture > 70.0:
            # High moisture suggests Wet/Raw food
            is_wet_or_raw = True
        else:
            # Default to Dry formula if category unknown and moisture is low/unknown
            is_dry = True

        if is_wet_or_raw:
            # Wet/Raw Food Conversion Formula
            # Step 1: Calculate wet matter carbs
            total = protein + fat + fiber + ash_value
            if moisture is not None:
                total += moisture
            else:
                # Moisture is required for Wet/Raw conversion
                return None

            wet_matter = 100.0 - total

            # Step 2: Calculate dry matter
            dry_matter = 100.0 - moisture

            # Step 3: Convert to dry matter basis
            if dry_matter <= 0:
                return None

            carbs = (wet_matter / dry_matter) * 100.0
        else:
            # Dry Food Formula (or default if category unknown)
            total = protein + fat + fiber + ash_value
            if moisture is not None:
                total += moisture

            carbs = 100.0 - total

        # Ensure non-negative
        carbs = max(0.0, carbs)

        # Round to one decimal place
        return round(carbs, 1)

    def validate_ingredients(self, ingredients_text: Optional[str]) -> bool:
        """
        Validate that ingredients contain starchy carb sources.

        This is confirmational only, not required for numeric output.

        Args:
            ingredients_text: Ingredients text to scan

        Returns:
            True if starchy carb ingredients found, False otherwise
        """
        if not ingredients_text:
            return False

        starchy_keywords = [
            "potato",
            "sweet potato",
            "rice",
            "brown rice",
            "millet",
            "barley",
            "oats",
            "quinoa",
            "chickpea",
            "lentil",
            "pea",
            "corn",
            "wheat",
        ]

        ingredients_lower = str(ingredients_text).lower()
        for keyword in starchy_keywords:
            if keyword in ingredients_lower:
                return True

        return False

    def process_single(self, product_detail_id: int) -> ProcessedProduct:
        """
        Process a single product detail and update/create processed_products record.

        Args:
            product_detail_id: ID of the product_details record

        Returns:
            ProcessedProduct instance

        Raises:
            ValueError: If product_detail_id not found
        """
        # Get product detail
        detail = self.db.query(ProductDetails).get(product_detail_id)
        if not detail:
            raise ValueError(
                f"ProductDetails with id={product_detail_id} not found"
            )

        # Check if processed record exists
        processed = (
            self.db.query(ProcessedProduct)
            .filter_by(product_detail_id=product_detail_id)
            .first()
        )

        if not processed:
            # Create new record
            processed = ProcessedProduct(product_detail_id=product_detail_id)
            self.db.add(processed)

        # Extract nutrition values
        nutrition_values = self.extract_all_nutrition_values(detail)

        # Get food category for calculation (may be None if not yet classified)
        food_category = processed.food_category

        # Calculate starchy carbs
        starchy_carb_pct = self.calculate_starchy_carbs(
            protein=nutrition_values["crude_protein_pct"],
            fat=nutrition_values["crude_fat_pct"],
            fiber=nutrition_values["crude_fiber_pct"],
            moisture=nutrition_values["crude_moisture_pct"],
            ash=nutrition_values["crude_ash_pct"],
            food_category=food_category,
        )

        # Update processed record
        processed.guaranteed_analysis_crude_protein_pct = (
            Decimal(str(nutrition_values["crude_protein_pct"]))
            if nutrition_values["crude_protein_pct"] is not None
            else None
        )
        processed.guaranteed_analysis_crude_fat_pct = (
            Decimal(str(nutrition_values["crude_fat_pct"]))
            if nutrition_values["crude_fat_pct"] is not None
            else None
        )
        processed.guaranteed_analysis_crude_fiber_pct = (
            Decimal(str(nutrition_values["crude_fiber_pct"]))
            if nutrition_values["crude_fiber_pct"] is not None
            else None
        )
        processed.guaranteed_analysis_crude_moisture_pct = (
            Decimal(str(nutrition_values["crude_moisture_pct"]))
            if nutrition_values["crude_moisture_pct"] is not None
            else None
        )
        processed.guaranteed_analysis_crude_ash_pct = (
            Decimal(str(nutrition_values["crude_ash_pct"]))
            if nutrition_values["crude_ash_pct"] is not None
            else None
        )
        processed.starchy_carb_pct = (
            Decimal(str(starchy_carb_pct)) if starchy_carb_pct is not None else None
        )
        processed.processed_at = datetime.utcnow()
        processed.processor_version = self.processor_version

        # Commit changes
        self.db.commit()
        self.db.refresh(processed)

        return processed

    def process_batch(
        self, product_detail_ids: List[int], skip_errors: bool = True
    ) -> dict:
        """
        Process multiple product details.

        Args:
            product_detail_ids: List of product_detail IDs to process
            skip_errors: If True, skip records that error; if False, raise exception

        Returns:
            Dict with keys: 'success', 'failed', 'total'
        """
        results = {"success": 0, "failed": 0, "total": len(product_detail_ids)}
        failed_ids = []

        for detail_id in product_detail_ids:
            try:
                self.process_single(detail_id)
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                failed_ids.append(detail_id)
                if not skip_errors:
                    raise
                else:
                    print(f"⚠️  Failed to process detail_id={detail_id}: {e}")

        if failed_ids:
            results["failed_ids"] = failed_ids

        return results

    def process_all(
        self, limit: Optional[int] = None, skip_existing: bool = False
    ) -> dict:
        """
        Process all product_details records.

        Args:
            limit: Maximum number of records to process (None = all)
            skip_existing: If True, skip records that already have nutrition values set

        Returns:
            Dict with processing statistics
        """
        # Build query
        query = self.db.query(ProductDetails)

        if skip_existing:
            # Only process records without processed_products or without nutrition values
            query = query.outerjoin(
                ProcessedProduct,
                ProductDetails.id == ProcessedProduct.product_detail_id,
            ).filter(
                (ProcessedProduct.id.is_(None))
                | (ProcessedProduct.guaranteed_analysis_crude_protein_pct.is_(None))
            )

        if limit:
            query = query.limit(limit)

        details = query.all()

        print(f"Found {len(details)} product_details to process")

        if not details:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "message": "No records to process",
            }

        # Process all records
        detail_ids = [d.id for d in details]
        results = self.process_batch(detail_ids, skip_errors=True)

        return results

    def get_statistics(self) -> dict:
        """
        Get statistics about processed nutrition values.

        Returns:
            Dict with statistics
        """
        from sqlalchemy import func

        stats = {}

        # Count records with nutrition values
        total_with_protein = (
            self.db.query(ProcessedProduct)
            .filter(
                ProcessedProduct.guaranteed_analysis_crude_protein_pct.isnot(None)
            )
            .count()
        )
        total_with_fat = (
            self.db.query(ProcessedProduct)
            .filter(ProcessedProduct.guaranteed_analysis_crude_fat_pct.isnot(None))
            .count()
        )
        total_with_fiber = (
            self.db.query(ProcessedProduct)
            .filter(
                ProcessedProduct.guaranteed_analysis_crude_fiber_pct.isnot(None)
            )
            .count()
        )
        total_with_moisture = (
            self.db.query(ProcessedProduct)
            .filter(
                ProcessedProduct.guaranteed_analysis_crude_moisture_pct.isnot(None)
            )
            .count()
        )
        total_with_ash = (
            self.db.query(ProcessedProduct)
            .filter(ProcessedProduct.guaranteed_analysis_crude_ash_pct.isnot(None))
            .count()
        )
        total_with_carbs = (
            self.db.query(ProcessedProduct)
            .filter(ProcessedProduct.starchy_carb_pct.isnot(None))
            .count()
        )

        stats["with_protein"] = total_with_protein
        stats["with_fat"] = total_with_fat
        stats["with_fiber"] = total_with_fiber
        stats["with_moisture"] = total_with_moisture
        stats["with_ash"] = total_with_ash
        stats["with_carbs"] = total_with_carbs

        # Total processed
        total_processed = self.db.query(ProcessedProduct).count()
        stats["_total_processed"] = total_processed

        # Total product_details
        total_details = self.db.query(ProductDetails).count()
        stats["_total_details"] = total_details

        # Unprocessed
        stats["_unprocessed"] = total_details - total_processed

        return stats

    def print_statistics(self):
        """Print nutrition statistics in a readable format."""
        stats = self.get_statistics()

        print("\n" + "=" * 70)
        print("STARCHY CARB PROCESSING STATISTICS")
        print("=" * 70)

        print("\nNutrition Values Extracted:")
        print(f"  Protein:   {stats['with_protein']:6,} products")
        print(f"  Fat:       {stats['with_fat']:6,} products")
        print(f"  Fiber:     {stats['with_fiber']:6,} products")
        print(f"  Moisture:  {stats['with_moisture']:6,} products")
        print(f"  Ash:       {stats['with_ash']:6,} products")
        print(f"  Carbs:     {stats['with_carbs']:6,} products")

        # Totals
        print("\nOverall:")
        print(f"  Total Processed:   {stats['_total_processed']:6,}")
        print(f"  Total Details:     {stats['_total_details']:6,}")
        print(f"  Unprocessed:       {stats['_unprocessed']:6,}")

        if stats["_total_details"] > 0:
            pct = (stats["_total_processed"] / stats["_total_details"]) * 100
            print(f"  Progress:          {pct:6.1f}%")

        print("=" * 70)


# Convenience functions
def process_starchy_carbs(
    db: Session,
    product_detail_ids: Optional[List[int]] = None,
    limit: Optional[int] = None,
    skip_existing: bool = False,
) -> dict:
    """
    Convenience function to process starchy carb extraction.

    Args:
        db: Database session
        product_detail_ids: Specific IDs to process (None = all)
        limit: Max records to process
        skip_existing: Skip records with existing nutrition values

    Returns:
        Processing statistics dict
    """
    processor = StarchyCarbProcessor(db)

    if product_detail_ids:
        return processor.process_batch(product_detail_ids)
    else:
        return processor.process_all(limit=limit, skip_existing=skip_existing)


if __name__ == "__main__":
    # Test/demo mode
    print("Starchy Carb Processor - Test Mode")
    print("=" * 70)
    print("This module extracts nutrition values and calculates starchy carbs.")
    print("\nUsage:")
    print(
        "  from app.processors.starchy_carb_processor import StarchyCarbProcessor"
    )
    print("  from app.models.database import SessionLocal")
    print()
    print("  db = SessionLocal()")
    print("  processor = StarchyCarbProcessor(db)")
    print("  processor.process_all()")
    print("  processor.print_statistics()")
    print("=" * 70)
