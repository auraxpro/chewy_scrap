"""
Ingredient Quality Processor

This module processes product_details records and populates ingredient quality
fields in the processed_products table.

Usage:
    from app.processors.ingredient_quality_processor import IngredientQualityProcessor

    processor = IngredientQualityProcessor(db_session)
    processor.process_single(product_detail_id)
    processor.process_all()
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import ProcessedProduct, ProductDetails
from app.processors.ingredient_quality_classifier import IngredientQualityClassifier


class IngredientQualityProcessor:
    """
    Processor for classifying ingredient quality and updating processed_products table.
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
        self.classifier = IngredientQualityClassifier()

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
            raise ValueError(f"ProductDetails with id={product_detail_id} not found")

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

        # Classify ingredient quality
        result = self.classifier.classify(detail.ingredients)

        # Update processed record
        processed.ingredients_all = result.ingredients_all

        # Protein
        processed.protein_ingredients_all = result.protein_ingredients_all
        processed.protein_ingredients_high = len(result.protein_ingredients_high)
        processed.protein_ingredients_good = len(result.protein_ingredients_good)
        processed.protein_ingredients_moderate = len(result.protein_ingredients_moderate)
        processed.protein_ingredients_low = len(result.protein_ingredients_low)
        processed.protein_ingredients_other = ", ".join(result.protein_ingredients_other) if result.protein_ingredients_other else None
        processed.protein_quality_class = result.protein_quality_class.value

        # Fat
        processed.fat_ingredients_all = result.fat_ingredients_all
        processed.fat_ingredients_high = len(result.fat_ingredients_high)
        processed.fat_ingredients_good = len(result.fat_ingredients_good)
        processed.fat_ingredients_low = len(result.fat_ingredients_low)
        processed.fat_ingredients_other = ", ".join(result.fat_ingredients_other) if result.fat_ingredients_other else None
        processed.fat_quality_class = result.fat_quality_class.value

        # Carb
        processed.carb_ingredients_all = result.carb_ingredients_all
        processed.carb_ingredients_high = len(result.carb_ingredients_high)
        processed.carb_ingredients_good = len(result.carb_ingredients_good)
        processed.carb_ingredients_moderate = len(result.carb_ingredients_moderate)
        processed.carb_ingredients_low = len(result.carb_ingredients_low)
        processed.carb_ingredients_other = ", ".join(result.carb_ingredients_other) if result.carb_ingredients_other else None
        processed.carb_quality_class = result.carb_quality_class.value

        # Fiber
        processed.fiber_ingredients_all = result.fiber_ingredients_all
        processed.fiber_ingredients_high = len(result.fiber_ingredients_high)
        processed.fiber_ingredients_good = len(result.fiber_ingredients_good)
        processed.fiber_ingredients_moderate = len(result.fiber_ingredients_moderate)
        processed.fiber_ingredients_low = len(result.fiber_ingredients_low)
        processed.fiber_ingredients_other = ", ".join(result.fiber_ingredients_other) if result.fiber_ingredients_other else None
        processed.fiber_quality_class = result.fiber_quality_class.value

        # Dirty Dozen
        processed.dirty_dozen_ingredients = ", ".join(result.dirty_dozen_ingredients) if result.dirty_dozen_ingredients else None
        processed.dirty_dozen_ingredients_count = result.dirty_dozen_ingredients_count

        # Synthetic Nutrition
        processed.synthetic_nutrition_addition = ", ".join(result.synthetic_nutrition_addition) if result.synthetic_nutrition_addition else None
        processed.synthetic_nutrition_addition_count = result.synthetic_nutrition_addition_count

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
            skip_existing: If True, skip records that already have ingredient quality set

        Returns:
            Dict with processing statistics
        """
        # Build query
        query = self.db.query(ProductDetails)

        if skip_existing:
            # Only process records without processed_products or without ingredients_all
            query = query.outerjoin(
                ProcessedProduct,
                ProductDetails.id == ProcessedProduct.product_detail_id,
            ).filter(
                (ProcessedProduct.id.is_(None))
                | (ProcessedProduct.ingredients_all.is_(None))
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

    def reprocess_quality_class(
        self, quality_class: str, limit: Optional[int] = None
    ) -> dict:
        """
        Reprocess all records with a specific quality class.

        Useful for testing or when classification logic changes.

        Args:
            quality_class: Quality class to reprocess (High, Good, Moderate, Low)
            limit: Maximum number to reprocess

        Returns:
            Dict with processing statistics
        """
        # Find records with this quality class in any category
        query = self.db.query(ProcessedProduct).filter(
            (
                (ProcessedProduct.protein_quality_class == quality_class)
                | (ProcessedProduct.fat_quality_class == quality_class)
                | (ProcessedProduct.carb_quality_class == quality_class)
                | (ProcessedProduct.fiber_quality_class == quality_class)
            )
        )

        if limit:
            query = query.limit(limit)

        processed_records = query.all()
        detail_ids = [p.product_detail_id for p in processed_records]

        print(
            f"Reprocessing {len(detail_ids)} records with quality class '{quality_class}'"
        )

        if not detail_ids:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "message": f"No records found with quality class '{quality_class}'",
            }

        return self.process_batch(detail_ids, skip_errors=True)

    def get_statistics(self) -> dict:
        """
        Get statistics about processed ingredient quality.

        Returns:
            Dict with statistics
        """
        from sqlalchemy import func

        stats = {}

        # Count by protein quality class
        protein_results = (
            self.db.query(
                ProcessedProduct.protein_quality_class,
                func.count(ProcessedProduct.id),
            )
            .group_by(ProcessedProduct.protein_quality_class)
            .all()
        )
        stats["protein_quality"] = {
            quality if quality else "NULL": count
            for quality, count in protein_results
        }

        # Count by fat quality class
        fat_results = (
            self.db.query(
                ProcessedProduct.fat_quality_class,
                func.count(ProcessedProduct.id),
            )
            .group_by(ProcessedProduct.fat_quality_class)
            .all()
        )
        stats["fat_quality"] = {
            quality if quality else "NULL": count for quality, count in fat_results
        }

        # Count by carb quality class
        carb_results = (
            self.db.query(
                ProcessedProduct.carb_quality_class,
                func.count(ProcessedProduct.id),
            )
            .group_by(ProcessedProduct.carb_quality_class)
            .all()
        )
        stats["carb_quality"] = {
            quality if quality else "NULL": count for quality, count in carb_results
        }

        # Count by fiber quality class
        fiber_results = (
            self.db.query(
                ProcessedProduct.fiber_quality_class,
                func.count(ProcessedProduct.id),
            )
            .group_by(ProcessedProduct.fiber_quality_class)
            .all()
        )
        stats["fiber_quality"] = {
            quality if quality else "NULL": count for quality, count in fiber_results
        }

        # Total processed
        total_processed = (
            self.db.query(ProcessedProduct)
            .filter(ProcessedProduct.ingredients_all.isnot(None))
            .count()
        )
        stats["_total_processed"] = total_processed

        # Total product_details
        total_details = self.db.query(ProductDetails).count()
        stats["_total_details"] = total_details

        # Unprocessed
        stats["_unprocessed"] = total_details - total_processed

        return stats

    def print_statistics(self):
        """Print ingredient quality statistics in a readable format."""
        stats = self.get_statistics()

        print("\n" + "=" * 70)
        print("INGREDIENT QUALITY STATISTICS")
        print("=" * 70)

        # Protein Quality
        print("\nProtein Quality:")
        for quality in ["High", "Good", "Moderate", "Low", "NULL"]:
            count = stats["protein_quality"].get(quality, 0)
            if count > 0:
                print(f"  {quality:15} {count:6,} products")

        # Fat Quality
        print("\nFat Quality:")
        for quality in ["High", "Good", "Moderate", "Low", "NULL"]:
            count = stats["fat_quality"].get(quality, 0)
            if count > 0:
                print(f"  {quality:15} {count:6,} products")

        # Carb Quality
        print("\nCarb Quality:")
        for quality in ["High", "Good", "Moderate", "Low", "NULL"]:
            count = stats["carb_quality"].get(quality, 0)
            if count > 0:
                print(f"  {quality:15} {count:6,} products")

        # Fiber Quality
        print("\nFiber Quality:")
        for quality in ["High", "Good", "Moderate", "Low", "NULL"]:
            count = stats["fiber_quality"].get(quality, 0)
            if count > 0:
                print(f"  {quality:15} {count:6,} products")

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
def process_ingredient_quality(
    db: Session,
    product_detail_ids: Optional[List[int]] = None,
    limit: Optional[int] = None,
    skip_existing: bool = False,
) -> dict:
    """
    Convenience function to process ingredient quality.

    Args:
        db: Database session
        product_detail_ids: Specific IDs to process (None = all)
        limit: Max records to process
        skip_existing: Skip records with existing ingredient quality

    Returns:
        Processing statistics dict
    """
    processor = IngredientQualityProcessor(db)

    if product_detail_ids:
        return processor.process_batch(product_detail_ids)
    else:
        return processor.process_all(limit=limit, skip_existing=skip_existing)


if __name__ == "__main__":
    # Test/demo mode
    print("Ingredient Quality Processor - Test Mode")
    print("=" * 70)
    print("This module processes product_details and classifies ingredient quality.")
    print("\nUsage:")
    print(
        "  from app.processors.ingredient_quality_processor import IngredientQualityProcessor"
    )
    print("  from app.models.database import SessionLocal")
    print()
    print("  db = SessionLocal()")
    print("  processor = IngredientQualityProcessor(db)")
    print("  processor.process_all()")
    print("  processor.print_statistics()")
    print("=" * 70)

