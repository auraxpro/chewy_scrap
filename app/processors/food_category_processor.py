"""
Food Category Processor

This module processes product_details records and populates the food_category
and category_reason fields in the processed_products table.

Usage:
    from app.processors.food_category_processor import FoodCategoryProcessor

    processor = FoodCategoryProcessor(db_session)
    processor.process_single(product_detail_id)
    processor.process_all()
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import ProcessedProduct, ProductDetails
from app.processors.category_classifier import FoodCategoryClassifier


class FoodCategoryProcessor:
    """
    Processor for classifying food categories and updating processed_products table.
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
        self.classifier = FoodCategoryClassifier()

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

        # Classify food category
        result = self.classifier.classify(
            product_category=detail.product_category,
            product_name=detail.product_name,
            specifications=detail.specifications,
        )

        # Update processed record
        processed.food_category = result.category.value
        processed.category_reason = result.reason
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
            skip_existing: If True, skip records that already have food_category set

        Returns:
            Dict with processing statistics
        """
        # Build query
        query = self.db.query(ProductDetails)

        if skip_existing:
            # Only process records without processed_products or without food_category
            query = query.outerjoin(
                ProcessedProduct,
                ProductDetails.id == ProcessedProduct.product_detail_id,
            ).filter(
                (ProcessedProduct.id.is_(None))
                | (ProcessedProduct.food_category.is_(None))
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

    def reprocess_category(self, category: str, limit: Optional[int] = None) -> dict:
        """
        Reprocess all records of a specific category.

        Useful for testing or when classification logic changes.

        Args:
            category: Food category to reprocess (Raw, Fresh, Dry, Wet, Other)
            limit: Maximum number to reprocess

        Returns:
            Dict with processing statistics
        """
        query = self.db.query(ProcessedProduct).filter(
            ProcessedProduct.food_category == category
        )

        if limit:
            query = query.limit(limit)

        processed_records = query.all()
        detail_ids = [p.product_detail_id for p in processed_records]

        print(f"Reprocessing {len(detail_ids)} records with category '{category}'")

        if not detail_ids:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "message": f"No records found with category '{category}'",
            }

        return self.process_batch(detail_ids, skip_errors=True)

    def get_statistics(self) -> dict:
        """
        Get statistics about processed food categories.

        Returns:
            Dict with category counts
        """
        from sqlalchemy import func

        stats = {}

        # Count by category
        results = (
            self.db.query(
                ProcessedProduct.food_category, func.count(ProcessedProduct.id)
            )
            .group_by(ProcessedProduct.food_category)
            .all()
        )

        for category, count in results:
            stats[category if category else "NULL"] = count

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
        """Print category statistics in a readable format."""
        stats = self.get_statistics()

        print("\n" + "=" * 70)
        print("FOOD CATEGORY STATISTICS")
        print("=" * 70)

        # Categories
        print("\nBy Category:")
        categories = ["Raw", "Fresh", "Dry", "Wet", "Other", "NULL"]
        for cat in categories:
            count = stats.get(cat, 0)
            if count > 0:
                print(f"  {cat:15} {count:6,} products")

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
def process_food_categories(
    db: Session,
    product_detail_ids: Optional[List[int]] = None,
    limit: Optional[int] = None,
    skip_existing: bool = False,
) -> dict:
    """
    Convenience function to process food categories.

    Args:
        db: Database session
        product_detail_ids: Specific IDs to process (None = all)
        limit: Max records to process
        skip_existing: Skip records with existing food_category

    Returns:
        Processing statistics dict
    """
    processor = FoodCategoryProcessor(db)

    if product_detail_ids:
        return processor.process_batch(product_detail_ids)
    else:
        return processor.process_all(limit=limit, skip_existing=skip_existing)


if __name__ == "__main__":
    # Test/demo mode
    print("Food Category Processor - Test Mode")
    print("=" * 70)
    print("This module processes product_details and classifies food categories.")
    print("\nUsage:")
    print("  from app.processors.food_category_processor import FoodCategoryProcessor")
    print("  from app.models.database import SessionLocal")
    print()
    print("  db = SessionLocal()")
    print("  processor = FoodCategoryProcessor(db)")
    print("  processor.process_all()")
    print("  processor.print_statistics()")
    print("=" * 70)
