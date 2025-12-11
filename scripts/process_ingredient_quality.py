#!/usr/bin/env python3
"""
Ingredient Quality Processing Script

This script processes product_details records and classifies ingredient quality,
updating the processed_products table.

Usage:
    # Process all unprocessed products
    python scripts/process_ingredient_quality.py

    # Process all products (including already processed)
    python scripts/process_ingredient_quality.py --reprocess

    # Process with limit
    python scripts/process_ingredient_quality.py --limit 100

    # Reprocess specific quality class
    python scripts/process_ingredient_quality.py --reprocess-quality "High"

    # Show statistics only
    python scripts/process_ingredient_quality.py --stats-only

    # Test mode (no database changes)
    python scripts/process_ingredient_quality.py --test
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import SessionLocal
from app.processors.ingredient_quality_classifier import IngredientQualityClassifier
from app.processors.ingredient_quality_processor import IngredientQualityProcessor


def run_test_mode():
    """Run test mode with sample data."""
    print("=" * 70)
    print("INGREDIENT QUALITY CLASSIFIER - TEST MODE")
    print("=" * 70)

    classifier = IngredientQualityClassifier()

    test_cases = [
        {
            "name": "High Quality Protein",
            "ingredients": "Organic chicken, organic beef, wild-caught salmon, organic sweet potatoes, organic carrots, flaxseed oil",
        },
        {
            "name": "Mixed Quality",
            "ingredients": "Chicken meal, brown rice, chicken fat, corn gluten meal, wheat flour, BHA, artificial colors",
        },
        {
            "name": "Low Quality",
            "ingredients": "Meat by-products, corn, wheat, soybean meal, animal digest, rendered fat, BHT, propylene glycol",
        },
        {
            "name": "Good Quality with Synthetic Nutrition",
            "ingredients": "Chicken breast, brown rice, salmon oil, sweet potatoes, Vitamin A Supplement, Zinc Oxide, Calcium Carbonate",
        },
        {
            "name": "High Quality Organic",
            "ingredients": "Organic whole chicken, organic beef liver, organic sweet potatoes, organic pumpkin, fish oil, organic carrots",
        },
    ]

    print("\nRunning test classifications:")
    print("-" * 70)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Ingredients: {test['ingredients'][:60]}...")

        result = classifier.classify(test["ingredients"])

        print(f"   → Protein: {result.protein_quality_class.value} ({len(result.protein_ingredients_high)} high, {len(result.protein_ingredients_good)} good)")
        print(f"   → Fat: {result.fat_quality_class.value} ({len(result.fat_ingredients_high)} high, {len(result.fat_ingredients_good)} good)")
        print(f"   → Carb: {result.carb_quality_class.value} ({len(result.carb_ingredients_high)} high, {len(result.carb_ingredients_good)} good)")
        print(f"   → Fiber: {result.fiber_quality_class.value} ({len(result.fiber_ingredients_high)} high, {len(result.fiber_ingredients_good)} good)")
        print(f"   → Dirty Dozen: {result.dirty_dozen_ingredients_count} found")
        print(f"   → Synthetic Nutrition: {result.synthetic_nutrition_addition_count} found")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


def run_processing(
    limit: int = None,
    reprocess: bool = False,
    reprocess_quality: str = None,
    stats_only: bool = False,
):
    """Run the actual processing with database."""
    print("=" * 70)
    print("INGREDIENT QUALITY PROCESSOR")
    print("=" * 70)

    # Create database session
    db = SessionLocal()

    try:
        processor = IngredientQualityProcessor(db)

        # Show statistics only
        if stats_only:
            print("\nCurrent Statistics:")
            processor.print_statistics()
            return

        # Reprocess specific quality class
        if reprocess_quality:
            print(f"\nReprocessing quality class: {reprocess_quality}")
            if limit:
                print(f"Limit: {limit} products")
            print("-" * 70)

            results = processor.reprocess_quality_class(reprocess_quality, limit=limit)

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
        description="Process ingredient quality for dog food products",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all unprocessed products
  python scripts/process_ingredient_quality.py

  # Process all products including already processed
  python scripts/process_ingredient_quality.py --reprocess

  # Process up to 100 products
  python scripts/process_ingredient_quality.py --limit 100

  # Reprocess all "High" quality products
  python scripts/process_ingredient_quality.py --reprocess-quality "High"

  # Show statistics only
  python scripts/process_ingredient_quality.py --stats-only

  # Run test mode (no database)
  python scripts/process_ingredient_quality.py --test
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
        "--reprocess-quality",
        type=str,
        default=None,
        help="Reprocess specific quality class (High, Good, Moderate, Low)",
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
        reprocess_quality=args.reprocess_quality,
        stats_only=args.stats_only,
    )


if __name__ == "__main__":
    main()

