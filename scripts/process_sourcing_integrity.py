#!/usr/bin/env python3
"""
Sourcing Integrity Processing Script

This script processes product_details records and classifies them into
sourcing integrity categories, updating the processed_products table.

Usage:
    # Process all unprocessed products
    python scripts/process_sourcing_integrity.py

    # Process all products (including already processed)
    python scripts/process_sourcing_integrity.py --reprocess

    # Process with limit
    python scripts/process_sourcing_integrity.py --limit 100

    # Process specific category
    python scripts/process_sourcing_integrity.py --reprocess-category "Human Grade"

    # Show statistics only
    python scripts/process_sourcing_integrity.py --stats-only

    # Test mode (no database changes)
    python scripts/process_sourcing_integrity.py --test
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import SessionLocal
from app.processors.sourcing_integrity_classifier import SourcingIntegrityClassifier
from app.processors.sourcing_integrity_processor import SourcingIntegrityProcessor


def run_test_mode():
    """Run test mode with sample data."""
    print("=" * 70)
    print("SOURCING INTEGRITY CLASSIFIER - TEST MODE")
    print("=" * 70)

    classifier = SourcingIntegrityClassifier()

    test_cases = [
        {
            "name": "Human Grade Organic",
            "product_category": "Premium Organic Dog Food",
            "product_name": "Organic Human Grade Chicken Recipe",
            "specifications": "USDA organic certified, made in human food facility",
            "ingredient_list": "Organic chicken, organic vegetables, certified organic",
        },
        {
            "name": "Human Grade",
            "product_category": "Premium Dog Food",
            "product_name": "Human Grade Beef Formula",
            "specifications": "Human grade ingredients, USDA inspected facility",
            "ingredient_list": "Human edible beef, restaurant quality vegetables",
        },
        {
            "name": "Feed Grade",
            "product_category": "Dog Food",
            "product_name": "Complete Dog Food",
            "specifications": "Feed grade formula, meat meal",
            "ingredient_list": "Meat by-product meal, rendered meat, animal feed quality",
        },
        {
            "name": "Organic Only",
            "product_category": "Organic Dog Food",
            "product_name": "Organic Chicken Meal",
            "specifications": "USDA organic certified",
            "ingredient_list": "Organic chicken meal, organic vegetables",
        },
        {
            "name": "Standard Quality",
            "product_category": "Dog Food",
            "product_name": "Premium Recipe",
            "specifications": "High quality ingredients",
            "ingredient_list": "Chicken, rice, vegetables",
        },
    ]

    print("\nRunning test classifications:")
    print("-" * 70)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Product: {test['product_name']}")
        print(f"   Specs: {test['specifications'][:50]}...")

        result = classifier.classify(
            product_category=test["product_category"],
            product_name=test["product_name"],
            specifications=test["specifications"],
            ingredient_list=test["ingredient_list"],
        )

        print(f"   → Sourcing: {result.sourcing_integrity.value}")
        print(f"   → Confidence: {result.confidence:.2f}")
        if result.matched_keywords:
            keywords_preview = ", ".join(result.matched_keywords[:2])
            if len(result.matched_keywords) > 2:
                keywords_preview += f" (+{len(result.matched_keywords) - 2} more)"
            print(f"   → Keywords: {keywords_preview}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


def run_processing(
    limit: int = None,
    reprocess: bool = False,
    reprocess_category: str = None,
    stats_only: bool = False,
):
    """Run the actual processing with database."""
    print("=" * 70)
    print("SOURCING INTEGRITY PROCESSOR")
    print("=" * 70)

    # Create database session
    db = SessionLocal()

    try:
        processor = SourcingIntegrityProcessor(db)

        # Show statistics only
        if stats_only:
            print("\nCurrent Statistics:")
            processor.print_statistics()
            return

        # Reprocess specific category
        if reprocess_category:
            print(f"\nReprocessing category: {reprocess_category}")
            if limit:
                print(f"Limit: {limit} products")
            print("-" * 70)

            results = processor.reprocess_category(reprocess_category, limit=limit)

            print(f"\n✓ Reprocessing complete!")
            print(f"  Total: {results['total']}")
            print(f"  Success: {results['success']}")
            print(f"  Failed: {results['failed']}")

            if results["failed"] > 0 and "failed_ids" in results:
                print(f"  Failed IDs: {results['failed_ids'][:10]}")

            # Show updated statistics
            print("\nUpdated Statistics:")
            processor.print_statistics()
            return

        # Process products
        skip_existing = not reprocess

        print(f"\nProcessing Configuration:")
        print(f"  Mode: {'Reprocess All' if reprocess else 'New Only'}")
        print(f"  Limit: {limit if limit else 'None (all)'}")
        print("-" * 70)

        results = processor.process_all(limit=limit, skip_existing=skip_existing)

        print(f"\n✓ Processing complete!")
        print(f"  Total: {results['total']}")
        print(f"  Success: {results['success']}")
        print(f"  Failed: {results['failed']}")

        if results["failed"] > 0 and "failed_ids" in results:
            print(f"  Failed IDs: {results['failed_ids'][:10]}")

        # Show statistics
        if results["success"] > 0:
            print("\nFinal Statistics:")
            processor.print_statistics()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process sourcing integrity for dog food products",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all unprocessed products
  python scripts/process_sourcing_integrity.py

  # Process all products including already processed
  python scripts/process_sourcing_integrity.py --reprocess

  # Process up to 100 products
  python scripts/process_sourcing_integrity.py --limit 100

  # Reprocess all "Human Grade" products
  python scripts/process_sourcing_integrity.py --reprocess-category "Human Grade"

  # Show statistics only
  python scripts/process_sourcing_integrity.py --stats-only

  # Run test mode (no database)
  python scripts/process_sourcing_integrity.py --test
        """,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of products to process",
    )

    parser.add_argument(
        "--reprocess",
        action="store_true",
        help="Reprocess all products (including already processed)",
    )

    parser.add_argument(
        "--reprocess-category",
        type=str,
        default=None,
        help="Reprocess specific sourcing integrity category",
    )

    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Show statistics only, don't process",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (no database changes)",
    )

    args = parser.parse_args()

    # Run test mode
    if args.test:
        run_test_mode()
        return

    # Run processing
    run_processing(
        limit=args.limit,
        reprocess=args.reprocess,
        reprocess_category=args.reprocess_category,
        stats_only=args.stats_only,
    )


if __name__ == "__main__":
    main()
