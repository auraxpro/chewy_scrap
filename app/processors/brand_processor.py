"""
Brand Processor

This module processes product_details records and populates the brand
field in the processed_products table.

Usage:
    from app.processors.brand_processor import BrandProcessor

    processor = BrandProcessor(db_session)
    processor.process_single(product_detail_id)
    processor.process_all()
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import ProcessedProduct, ProductDetails
from app.processors.brand_classifier import BrandClassifier


class BrandProcessor:
    """
    Processor for detecting brands and updating processed_products table.
    """

    def __init__(self, db: Session, processor_version: str = "v1.0.0", brands: Optional[List[str]] = None):
        """
        Initialize the processor.

        Args:
            db: SQLAlchemy database session
            processor_version: Version string for tracking
            brands: Optional custom brand list. If None, uses default from brands.py
        """
        self.db = db
        self.processor_version = processor_version
        self.classifier = BrandClassifier(brands=brands)

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

        # Classify brand
        result = self.classifier.classify(
            product_name=detail.product_name,
            details=detail.details,
            specifications=detail.specifications,
            ingredients=detail.ingredients,
            more_details=detail.more_details,
        )

        # Update processed record
        processed.brand = result.brand
        processed.brand_detection_method = result.method
        processed.brand_detection_confidence = result.confidence
        processed.brand_detection_reason = result.reason
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
            skip_existing: If True, skip records that already have brand set

        Returns:
            Dict with processing statistics
        """
        # Build query
        query = self.db.query(ProductDetails)

        if skip_existing:
            # Only process records without processed_products or without brand
            query = query.outerjoin(
                ProcessedProduct,
                ProductDetails.id == ProcessedProduct.product_detail_id,
            ).filter(
                (ProcessedProduct.id.is_(None))
                | (ProcessedProduct.brand.is_(None))
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
        Get statistics about processed brands.

        Returns:
            Dict with statistics
        """
        from sqlalchemy import func

        stats = {}

        # Count by brand
        brand_results = (
            self.db.query(
                ProcessedProduct.brand,
                func.count(ProcessedProduct.id),
            )
            .group_by(ProcessedProduct.brand)
            .order_by(func.count(ProcessedProduct.id).desc())
            .all()
        )
        stats["brands"] = {
            brand if brand else "NULL": count for brand, count in brand_results
        }

        # Count by detection method
        method_results = (
            self.db.query(
                ProcessedProduct.brand_detection_method,
                func.count(ProcessedProduct.id),
            )
            .group_by(ProcessedProduct.brand_detection_method)
            .all()
        )
        stats["detection_methods"] = {
            method if method else "NULL": count for method, count in method_results
        }

        # Count by confidence
        confidence_results = (
            self.db.query(
                ProcessedProduct.brand_detection_confidence,
                func.count(ProcessedProduct.id),
            )
            .group_by(ProcessedProduct.brand_detection_confidence)
            .all()
        )
        stats["confidence"] = {
            conf if conf else "NULL": count for conf, count in confidence_results
        }

        # Total processed
        total_processed = (
            self.db.query(ProcessedProduct)
            .filter(ProcessedProduct.brand.isnot(None))
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
        """Print brand detection statistics in a readable format."""
        stats = self.get_statistics()

        print("\n" + "=" * 70)
        print("BRAND DETECTION STATISTICS")
        print("=" * 70)

        # Top brands
        print("\nTop Brands:")
        brand_items = list(stats["brands"].items())[:20]  # Top 20
        for brand, count in brand_items:
            print(f"  {brand[:40]:40} {count:6,} products")

        # Detection methods
        print("\nDetection Methods:")
        for method in ["starts_with", "contains", "fallback", "fuzzy", "none"]:
            count = stats["detection_methods"].get(method, 0)
            if count > 0:
                print(f"  {method:15} {count:6,} products")

        # Confidence levels
        print("\nConfidence Levels:")
        for conf in ["high", "medium", "low", "none"]:
            count = stats["confidence"].get(conf, 0)
            if count > 0:
                print(f"  {conf:15} {count:6,} products")

        # Totals
        print("\nOverall:")
        print(f"  Total Processed:   {stats['_total_processed']:6,}")
        print(f"  Total Details:     {stats['_total_details']:6,}")
        print(f"  Unprocessed:       {stats['_unprocessed']:6,}")

        if stats["_total_details"] > 0:
            pct = (stats["_total_processed"] / stats["_total_details"]) * 100
            print(f"  Progress:          {pct:6.1f}%")

        print("=" * 70)


# Convenience function
def process_brands(
    db: Session,
    product_detail_ids: Optional[List[int]] = None,
    limit: Optional[int] = None,
    skip_existing: bool = False,
    brands: Optional[List[str]] = None,
) -> dict:
    """
    Convenience function to process brands.

    Args:
        db: Database session
        product_detail_ids: Specific IDs to process (None = all)
        limit: Max records to process
        skip_existing: Skip records with existing brand
        brands: Optional custom brand list

    Returns:
        Processing statistics dict
    """
    processor = BrandProcessor(db, brands=brands)

    if product_detail_ids:
        return processor.process_batch(product_detail_ids)
    else:
        return processor.process_all(limit=limit, skip_existing=skip_existing)


if __name__ == "__main__":
    # Test/demo mode
    print("Brand Processor - Test Mode")
    print("=" * 70)
    print("This module processes product_details and detects brand names.")
    print("\nUsage:")
    print("  from app.processors.brand_processor import BrandProcessor")
    print("  from app.models.database import SessionLocal")
    print()
    print("  db = SessionLocal()")
    print("  processor = BrandProcessor(db)")
    print("  processor.process_all()")
    print("  processor.print_statistics()")
    print("=" * 70)

