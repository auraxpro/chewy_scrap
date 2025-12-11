#!/usr/bin/env python3
"""
Food Category Processing CLI

Process product_details records and classify them into food categories
(Raw, Fresh, Dry, Wet, Other) using keyword-based classification.

Usage:
    # Process single product
    python scripts/process_food_categories.py --single 123

    # Process all unprocessed products
    python scripts/process_food_categories.py --all

    # Process with limit
    python scripts/process_food_categories.py --all --limit 100

    # Process all (including already processed)
    python scripts/process_food_categories.py --all --reprocess

    # Reprocess specific category
    python scripts/process_food_categories.py --reprocess-category Dry

    # Show statistics only
    python scripts/process_food_categories.py --stats

    # Test classifier with sample text
    python scripts/process_food_categories.py --test
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
from datetime import datetime

from app.models.database import SessionLocal
from app.processors.food_category_processor import FoodCategoryProcessor


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Food Category Classification Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process single product:
    python scripts/process_food_categories.py --single 123

  Process all unprocessed:
    python scripts/process_food_categories.py --all

  Process 50 products:
    python scripts/process_food_categories.py --all --limit 50

  Reprocess all (force update):
    python scripts/process_food_categories.py --all --reprocess

  Reprocess specific category:
    python scripts/process_food_categories.py --reprocess-category Dry

  Show statistics:
    python scripts/process_food_categories.py --stats

  Test mode:
    python scripts/process_food_categories.py --test
        """,
    )

    # Commands (mutually exclusive)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--single",
        type=int,
        metavar="ID",
        help="Process single product by product_detail ID",
    )
    group.add_argument(
        "--all", action="store_true", help="Process all unprocessed products"
    )
    group.add_argument(
        "--reprocess-category",
        type=str,
        metavar="CATEGORY",
        choices=["Raw", "Fresh", "Dry", "Wet", "Other"],
        help="Reprocess all products of a specific category",
    )
    group.add_argument(
        "--stats", action="store_true", help="Show category statistics only"
    )
    group.add_argument(
        "--test", action="store_true", help="Run test mode with sample data"
    )

    # Options
    parser.add_argument(
        "--limit", type=int, metavar="N", help="Limit number of products to process"
    )
    parser.add_argument(
        "--reprocess",
        action="store_true",
        help="Reprocess already processed products (force update)",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="v1.0.0",
        help="Processor version (default: v1.0.0)",
    )

    return parser.parse_args()


def process_single(processor: FoodCategoryProcessor, product_detail_id: int):
    """Process a single product."""
    print("=" * 70)
    print(f"Processing single product: detail_id={product_detail_id}")
    print("=" * 70)

    try:
        result = processor.process_single(product_detail_id)
        print(f"\n✓ Success!")
        print(f"  Product Detail ID: {result.product_detail_id}")
        print(f"  Food Category:     {result.food_category}")
        print(f"  Confidence:        {result.category_reason}")
        print(f"  Processed At:      {result.processed_at}")
        print(f"  Version:           {result.processor_version}")
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def process_all(
    processor: FoodCategoryProcessor, limit: int = None, skip_existing: bool = True
):
    """Process all products."""
    print("=" * 70)
    print("Processing Food Categories")
    print("=" * 70)
    print(f"Mode:           {'Skip existing' if skip_existing else 'Reprocess all'}")
    print(f"Limit:          {limit if limit else 'None (all records)'}")
    print(f"Version:        {processor.processor_version}")
    print("=" * 70)

    start_time = datetime.now()

    results = processor.process_all(limit=limit, skip_existing=skip_existing)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Total:          {results['total']:,}")
    print(f"Success:        {results['success']:,}")
    print(f"Failed:         {results['failed']:,}")
    print(f"Duration:       {duration:.2f} seconds")

    if results["success"] > 0:
        rate = results["success"] / duration
        print(f"Rate:           {rate:.2f} products/second")

    if results["failed"] > 0 and "failed_ids" in results:
        print(f"\nFailed IDs: {results['failed_ids']}")

    print("=" * 70)

    return results["success"] > 0


def reprocess_category(
    processor: FoodCategoryProcessor, category: str, limit: int = None
):
    """Reprocess all products of a specific category."""
    print("=" * 70)
    print(f"Reprocessing Category: {category}")
    print("=" * 70)
    print(f"Limit:          {limit if limit else 'None (all records)'}")
    print("=" * 70)

    start_time = datetime.now()

    results = processor.reprocess_category(category, limit=limit)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 70)
    print("REPROCESSING COMPLETE")
    print("=" * 70)
    print(f"Total:          {results['total']:,}")
    print(f"Success:        {results['success']:,}")
    print(f"Failed:         {results['failed']:,}")
    print(f"Duration:       {duration:.2f} seconds")

    if results["success"] > 0:
        rate = results["success"] / duration
        print(f"Rate:           {rate:.2f} products/second")

    print("=" * 70)

    return results["success"] > 0


def show_statistics(processor: FoodCategoryProcessor):
    """Show category statistics."""
    processor.print_statistics()


def run_test():
    """Run test mode with sample data."""
    print("=" * 70)
    print("FOOD CATEGORY CLASSIFIER - TEST MODE")
    print("=" * 70)

    from app.processors.category_classifier import FoodCategoryClassifier

    classifier = FoodCategoryClassifier()

    test_cases = [
        {
            "name": "Dry Kibble",
            "product_category": "Dry Dog Food",
            "product_name": "Blue Buffalo Wilderness High Protein Kibble",
            "specifications": "Grain-free dry formula",
        },
        {
            "name": "Raw Frozen",
            "product_category": "Frozen Dog Food",
            "product_name": "Primal Raw Frozen Beef Formula",
            "specifications": "Raw frozen patties, uncooked",
        },
        {
            "name": "Fresh Refrigerated",
            "product_category": "Fresh Dog Food",
            "product_name": "The Farmer's Dog Fresh Meals",
            "specifications": "Gently cooked, refrigerated, human grade",
        },
        {
            "name": "Wet Canned",
            "product_category": "Canned Dog Food",
            "product_name": "Merrick Grain Free Wet Dog Food",
            "specifications": "Chunks in gravy, pate style",
        },
        {
            "name": "Unclear/Other",
            "product_category": "Dog Food",
            "product_name": "Generic Brand Dog Food",
            "specifications": None,
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'─' * 70}")
        print(f"Category:  {test['product_category']}")
        print(f"Name:      {test['product_name']}")
        print(f"Specs:     {test['specifications']}")

        result = classifier.classify(
            product_category=test["product_category"],
            product_name=test["product_name"],
            specifications=test["specifications"],
        )

        print(f"\n→ Result:     {result.category.value}")
        print(f"→ Confidence: {result.confidence:.2f}")
        print(
            f"→ Keywords:   {', '.join(result.matched_keywords[:3]) if result.matched_keywords else 'None'}"
        )
        print(f"→ Reason:     {result.reason}")

    print(f"\n{'=' * 70}")
    print("TEST COMPLETE")
    print("=" * 70)


def main():
    """Main entry point."""
    args = parse_args()

    # Test mode doesn't need DB
    if args.test:
        run_test()
        sys.exit(0)

    # Initialize database session
    db = SessionLocal()

    try:
        # Create processor
        processor = FoodCategoryProcessor(db, processor_version=args.version)

        # Execute command
        if args.single:
            success = process_single(processor, args.single)
        elif args.all:
            success = process_all(
                processor, limit=args.limit, skip_existing=not args.reprocess
            )
        elif args.reprocess_category:
            success = reprocess_category(processor, args.reprocess_category, args.limit)
        elif args.stats:
            show_statistics(processor)
            success = True
        else:
            print("No command specified. Use --help for usage information.")
            success = False

        # Exit code
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n{'=' * 70}")
        print("ERROR")
        print("=" * 70)
        print(f"{e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
