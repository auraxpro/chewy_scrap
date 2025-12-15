#!/usr/bin/env python3
"""
Brand Processing Script

This script processes product_details records and detects brand names,
updating the processed_products table.

Usage:
    # Process all unprocessed products
    python scripts/process_brands.py

    # Process all products (including already processed)
    python scripts/process_brands.py --reprocess

    # Process with limit
    python scripts/process_brands.py --limit 100

    # Show statistics only
    python scripts/process_brands.py --stats-only

    # Test mode (no database changes)
    python scripts/process_brands.py --test
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import SessionLocal
from app.processors.brand_classifier import BrandClassifier
from app.processors.brand_processor import BrandProcessor


def run_test_mode():
    """Run test mode with sample data."""
    print("=" * 70)
    print("BRAND CLASSIFIER - TEST MODE")
    print("=" * 70)

    classifier = BrandClassifier()

    test_cases = [
        {
            "name": "Blue Buffalo Life Protection Formula Chicken & Rice Recipe",
            "expected": "Blue Buffalo",
        },
        {
            "name": "Hill's Science Diet Adult 7+ Chicken Meal",
            "expected": "Hill's Science Diet",
        },
        {
            "name": "Taste of the Wild Sierra Mountain Grain-Free",
            "expected": "Taste of the Wild",
        },
        {
            "name": "Purina ONE SmartBlend Chicken",
            "expected": "Purina ONE",
        },
        {
            "name": "Merrick Backcountry Raw Infused",
            "expected": "Merrick",
        },
        {
            "name": "Some Generic Product Name",
            "expected": None,
        },
    ]

    print("\nTesting brand detection:\n")
    for i, test in enumerate(test_cases, 1):
        result = classifier.classify(product_name=test["name"])
        status = "✅" if result.brand == test["expected"] else "❌"
        print(f"{status} Test {i}: {test['name']}")
        print(f"   Detected: {result.brand}")
        print(f"   Expected: {test['expected']}")
        print(f"   Method: {result.method}")
        print(f"   Confidence: {result.confidence}")
        if result.reason:
            print(f"   Reason: {result.reason}")
        print()

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Process brands for product_details records"
    )
    parser.add_argument(
        "--reprocess",
        action="store_true",
        help="Reprocess all products (including already processed)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of products to process",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Show statistics only (no processing)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test mode (no database changes)",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode()
        return

    db = SessionLocal()
    try:
        processor = BrandProcessor(db)

        if args.stats_only:
            processor.print_statistics()
            return

        # Process products
        skip_existing = not args.reprocess
        results = processor.process_all(limit=args.limit, skip_existing=skip_existing)

        print("\n" + "=" * 70)
        print("BRAND PROCESSING RESULTS")
        print("=" * 70)
        print(f"Total:     {results.get('total', 0)}")
        print(f"Success:   {results.get('success', 0)}")
        print(f"Failed:    {results.get('failed', 0)}")
        if results.get("failed_ids"):
            print(f"\nFailed IDs: {results['failed_ids'][:10]}...")
        print("=" * 70)

        # Show statistics
        processor.print_statistics()

    finally:
        db.close()


if __name__ == "__main__":
    main()

