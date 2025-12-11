#!/usr/bin/env python3
"""
Longevity Additives Processing Script

This script processes product_details records and identifies longevity additives,
updating the processed_products table.

Usage:
    # Process all unprocessed products
    python scripts/process_longevity_additives.py

    # Process all products (including already processed)
    python scripts/process_longevity_additives.py --reprocess

    # Process with limit
    python scripts/process_longevity_additives.py --limit 100

    # Show statistics only
    python scripts/process_longevity_additives.py --stats-only

    # Test mode (no database changes)
    python scripts/process_longevity_additives.py --test
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import SessionLocal
from app.processors.longevity_additives_classifier import (
    LongevityAdditivesClassifier,
)
from app.processors.longevity_additives_processor import (
    LongevityAdditivesProcessor,
)


def run_test_mode():
    """Run test mode with sample data."""
    print("=" * 70)
    print("LONGEVITY ADDITIVES CLASSIFIER - TEST MODE")
    print("=" * 70)

    classifier = LongevityAdditivesClassifier()

    test_cases = [
        {
            "name": "Herbs and Botanicals",
            "ingredients": "Chicken, brown rice, rosemary extract, turmeric, blueberry extract, cranberry, spinach, fish oil",
        },
        {
            "name": "Probiotics and Mushrooms",
            "ingredients": "Beef, sweet potato, probiotics, lactobacillus acidophilus, reishi mushroom, shiitake mushroom, omega-3 fish oil",
        },
        {
            "name": "Multiple Longevity Additives",
            "ingredients": "Salmon, quinoa, spirulina, chlorella, green tea extract, aloe vera, goji berry, elderberry, bee pollen, royal jelly, glucosamine, chondroitin sulfate, astaxanthin, resveratrol, CoQ10, taurine",
        },
        {
            "name": "No Longevity Additives",
            "ingredients": "Chicken meal, brown rice, chicken fat, corn gluten meal, wheat flour, BHA, artificial colors",
        },
        {
            "name": "Herbs Only",
            "ingredients": "Organic chicken, organic beef, parsley, oregano, basil, thyme, sage, ginger",
        },
    ]

    print("\nRunning test classifications:")
    print("-" * 70)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Ingredients: {test['ingredients'][:70]}...")

        result = classifier.classify(test["ingredients"])

        print(f"   → Found {result.longevity_additives_count} longevity additive(s)")
        if result.longevity_additives:
            print(f"   → Additives: {', '.join(result.longevity_additives[:5])}")
            if len(result.longevity_additives) > 5:
                print(f"     ... and {len(result.longevity_additives) - 5} more")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


def run_processing(
    limit: int = None,
    reprocess: bool = False,
    stats_only: bool = False,
):
    """Run the actual processing with database."""
    print("=" * 70)
    print("LONGEVITY ADDITIVES PROCESSOR")
    print("=" * 70)

    # Create database session
    db = SessionLocal()

    try:
        processor = LongevityAdditivesProcessor(db)

        # Show statistics only
        if stats_only:
            print("\nCurrent Statistics:")
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
        description="Process longevity additives for dog food products",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all unprocessed products
  python scripts/process_longevity_additives.py

  # Process all products including already processed
  python scripts/process_longevity_additives.py --reprocess

  # Process up to 100 products
  python scripts/process_longevity_additives.py --limit 100

  # Show statistics only
  python scripts/process_longevity_additives.py --stats-only

  # Run test mode (no database)
  python scripts/process_longevity_additives.py --test
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
        stats_only=args.stats_only,
    )


if __name__ == "__main__":
    main()
