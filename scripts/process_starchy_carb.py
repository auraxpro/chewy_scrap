#!/usr/bin/env python3
"""
Starchy Carb Processing CLI

Extract nutrition values from guaranteed_analysis and calculate starchy carb percentage.

Usage:
    # Process single product
    python scripts/process_starchy_carb.py --single 123

    # Process all unprocessed products
    python scripts/process_starchy_carb.py --all

    # Process with limit
    python scripts/process_starchy_carb.py --all --limit 100

    # Process all (including already processed)
    python scripts/process_starchy_carb.py --all --reprocess

    # Show statistics only
    python scripts/process_starchy_carb.py --stats
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
from datetime import datetime

from app.models.database import SessionLocal
from app.processors.starchy_carb_processor import StarchyCarbProcessor


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Starchy Carb Extraction Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process single product:
    python scripts/process_starchy_carb.py --single 123

  Process all unprocessed:
    python scripts/process_starchy_carb.py --all

  Process 50 products:
    python scripts/process_starchy_carb.py --all --limit 50

  Reprocess all (force update):
    python scripts/process_starchy_carb.py --all --reprocess

  Show statistics:
    python scripts/process_starchy_carb.py --stats
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
        "--stats", action="store_true", help="Show nutrition statistics only"
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


def process_single(processor: StarchyCarbProcessor, product_detail_id: int):
    """Process a single product."""
    print("=" * 70)
    print(f"Processing single product: detail_id={product_detail_id}")
    print("=" * 70)

    try:
        result = processor.process_single(product_detail_id)
        print(f"\n✓ Success!")
        print(f"  Product Detail ID: {result.product_detail_id}")
        print(
            f"  Protein:            {result.guaranteed_analysis_crude_protein_pct}%"
        )
        print(f"  Fat:                {result.guaranteed_analysis_crude_fat_pct}%")
        print(
            f"  Fiber:              {result.guaranteed_analysis_crude_fiber_pct}%"
        )
        print(
            f"  Moisture:           {result.guaranteed_analysis_crude_moisture_pct}%"
        )
        print(f"  Ash:                {result.guaranteed_analysis_crude_ash_pct}%")
        print(f"  Starchy Carbs:      {result.starchy_carb_pct}%")
        print(f"  Processed At:      {result.processed_at}")
        print(f"  Version:            {result.processor_version}")
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def process_all(
    processor: StarchyCarbProcessor, limit: int = None, skip_existing: bool = True
):
    """Process all products."""
    print("=" * 70)
    print("Processing Starchy Carb Extraction")
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


def show_statistics(processor: StarchyCarbProcessor):
    """Show nutrition statistics."""
    processor.print_statistics()


def main():
    """Main entry point."""
    args = parse_args()

    # Initialize database session
    db = SessionLocal()

    try:
        # Create processor
        processor = StarchyCarbProcessor(db, processor_version=args.version)

        # Execute command
        if args.single:
            success = process_single(processor, args.single)
        elif args.all:
            success = process_all(
                processor, limit=args.limit, skip_existing=not args.reprocess
            )
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
