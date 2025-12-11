#!/usr/bin/env python3
"""
Process Products Script

This script runs data processors on scraped products to normalize and
enhance the data before scoring.

Processors include:
- Ingredient normalization
- Category normalization
- Processing method detection
- Package size estimation

Usage:
    python scripts/process_products.py [options]

Examples:
    # Process all unprocessed products
    python scripts/process_products.py

    # Process specific number of products
    python scripts/process_products.py --limit 100

    # Start from offset
    python scripts/process_products.py --offset 500 --limit 100

    # Force reprocess already processed products
    python scripts/process_products.py --force --limit 50

    # Process single product by ID
    python scripts/process_products.py --product-id 123
"""

import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import SessionLocal, init_db
from app.models.product import ProductList
from app.processors.base_processor import BaseProcessor

# TODO: Import specific processors when implemented
# from app.processors.ingredient_normalizer import IngredientNormalizer
# from app.processors.category_normalizer import CategoryNormalizer
# from app.processors.processing_detector import ProcessingDetector
# from app.processors.packaging_estimator import PackagingEstimator


def parse_arguments():
    """Parse command line arguments"""
    args = {
        "limit": None,
        "offset": 0,
        "force": False,
        "product_id": None,
    }

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg in ["--limit", "-l"] and i + 1 < len(sys.argv):
            try:
                args["limit"] = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"❌ Invalid limit value: {sys.argv[i + 1]}")
                sys.exit(1)

        elif arg in ["--offset", "-o"] and i + 1 < len(sys.argv):
            try:
                args["offset"] = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"❌ Invalid offset value: {sys.argv[i + 1]}")
                sys.exit(1)

        elif arg in ["--force", "-f"]:
            args["force"] = True
            i += 1

        elif arg in ["--product-id", "-p"] and i + 1 < len(sys.argv):
            try:
                args["product_id"] = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print(f"❌ Invalid product ID: {sys.argv[i + 1]}")
                sys.exit(1)

        elif arg in ["--help", "-h"]:
            print(__doc__)
            sys.exit(0)

        else:
            print(f"❌ Unknown argument: {arg}")
            print("Use --help for usage information")
            sys.exit(1)

    return args


def process_single_product(product_id: int, force: bool = False):
    """
    Process a single product by ID.

    Args:
        product_id: Product ID to process
        force: Force reprocess even if already processed
    """
    db = SessionLocal()
    try:
        product = db.query(ProductList).filter(ProductList.id == product_id).first()

        if not product:
            print(f"❌ Product with ID {product_id} not found")
            return False

        if product.processed and not force:
            print(
                f"⚠️  Product {product_id} already processed (use --force to reprocess)"
            )
            return False

        if not product.scraped or product.skipped:
            print(f"❌ Product {product_id} has not been scraped or was skipped")
            return False

        if not product.details:
            print(f"❌ Product {product_id} has no details")
            return False

        print(f"\n📦 Processing product {product_id}: {product.details.product_name}")

        # TODO: Initialize and run processors
        # processors = [
        #     IngredientNormalizer(db),
        #     CategoryNormalizer(db),
        #     ProcessingDetector(db),
        #     PackagingEstimator(db),
        # ]
        #
        # for processor in processors:
        #     try:
        #         result = processor.process(product)
        #         print(f"  ✅ {processor.get_name()}: {result}")
        #     except Exception as e:
        #         print(f"  ❌ {processor.get_name()}: {str(e)}")

        # Placeholder: Mark as processed
        print("  ⚠️  Note: Specific processors not yet implemented")
        print("  ⚠️  Marking as processed without actual processing")
        product.processed = True
        db.commit()

        print(f"✅ Product {product_id} processed successfully")
        return True

    except Exception as e:
        print(f"❌ Error processing product {product_id}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def process_batch(limit: int = None, offset: int = 0, force: bool = False):
    """
    Process multiple products in batch.

    Args:
        limit: Maximum number of products to process
        offset: Number of products to skip
        force: Force reprocess already processed products
    """
    db = SessionLocal()
    try:
        # Build query
        query = db.query(ProductList).filter(
            ProductList.scraped == True, ProductList.skipped == False
        )

        if not force:
            query = query.filter(ProductList.processed == False)

        query = query.order_by(ProductList.id).offset(offset)

        if limit:
            query = query.limit(limit)

        products = query.all()
        total = len(products)

        if total == 0:
            if force:
                print("✅ All products already processed!")
            else:
                print("✅ No unprocessed products found!")
                print("💡 Use --force to reprocess already processed products")
            return

        print(f"\n📊 Found {total} product(s) to process")
        if offset > 0:
            print(f"📍 Starting from offset: {offset}")
        if limit:
            print(f"📊 Limited to: {limit} products")

        print("\n" + "=" * 70)

        success_count = 0
        fail_count = 0
        start_time = datetime.now()

        # TODO: Initialize processors
        # processors = [
        #     IngredientNormalizer(db),
        #     CategoryNormalizer(db),
        #     ProcessingDetector(db),
        #     PackagingEstimator(db),
        # ]

        for idx, product in enumerate(products, 1):
            print(f"\n[{idx}/{total}] Processing product {product.id}")

            if not product.details:
                print("  ⚠️  No details found, skipping...")
                fail_count += 1
                continue

            print(f"  📦 {product.details.product_name[:60]}...")

            try:
                # TODO: Run each processor
                # for processor in processors:
                #     try:
                #         result = processor.process(product)
                #         print(f"    ✅ {processor.get_name()}")
                #     except Exception as e:
                #         print(f"    ❌ {processor.get_name()}: {str(e)}")

                # Placeholder: Mark as processed
                print("  ⚠️  Specific processors not yet implemented")
                product.processed = True
                db.commit()

                success_count += 1
                print(f"  ✅ Processed successfully")

            except Exception as e:
                fail_count += 1
                print(f"  ❌ Error: {str(e)}")
                continue

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print(f"✅ Processing completed in {duration:.2f} seconds!")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {fail_count}")
        print(f"   Total: {total}")

        if success_count > 0:
            avg_time = duration / success_count
            print(f"   Average: {avg_time:.2f}s per product")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


def show_statistics():
    """Show processing statistics"""
    db = SessionLocal()
    try:
        total = db.query(ProductList).count()
        scraped = db.query(ProductList).filter(ProductList.scraped == True).count()
        processed = db.query(ProductList).filter(ProductList.processed == True).count()
        unprocessed = (
            db.query(ProductList)
            .filter(
                ProductList.scraped == True,
                ProductList.processed == False,
                ProductList.skipped == False,
            )
            .count()
        )

        print("\n📊 Processing Statistics:")
        print(f"   Total products: {total}")
        print(f"   Scraped: {scraped}")
        print(f"   Processed: {processed}")
        print(f"   Unprocessed: {unprocessed}")

        if scraped > 0:
            processed_pct = (processed / scraped) * 100
            print(f"   Progress: {processed_pct:.1f}%")

    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    finally:
        db.close()


def main():
    """Main function"""
    print("=" * 70)
    print("🔧 Dog Food Scoring API - Product Data Processor")
    print("=" * 70)

    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        sys.exit(1)

    # Parse arguments
    args = parse_arguments()

    # Show statistics first
    show_statistics()

    # Process single product or batch
    if args["product_id"]:
        print("\n📍 Processing single product...")
        success = process_single_product(args["product_id"], force=args["force"])
        sys.exit(0 if success else 1)
    else:
        print("\n🚀 Starting batch processing...")
        process_batch(limit=args["limit"], offset=args["offset"], force=args["force"])

    # Show final statistics
    print("\n" + "=" * 70)
    show_statistics()
    print("=" * 70)

    print("\n💡 Next step: Calculate scores with:")
    print("   python scripts/calculate_scores.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
