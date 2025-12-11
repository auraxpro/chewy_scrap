#!/usr/bin/env python3
"""
Calculate Scores Script

This script calculates quality scores for processed dog food products
using the multi-criteria scoring system.

Scoring Components:
- Ingredient Quality (35%)
- Nutritional Value (30%)
- Processing Method (20%)
- Price-Value Ratio (15%)

Usage:
    python scripts/calculate_scores.py [options]

Examples:
    # Calculate scores for all unscored products
    python scripts/calculate_scores.py

    # Calculate scores for specific number of products
    python scripts/calculate_scores.py --limit 100

    # Start from offset
    python scripts/calculate_scores.py --offset 500 --limit 100

    # Force recalculate already scored products
    python scripts/calculate_scores.py --force --limit 50

    # Calculate score for single product by ID
    python scripts/calculate_scores.py --product-id 123
"""

import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path so we can import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import (
    SCORE_WEIGHT_INGREDIENTS,
    SCORE_WEIGHT_NUTRITION,
    SCORE_WEIGHT_PRICE_VALUE,
    SCORE_WEIGHT_PROCESSING,
    SCORING_VERSION,
)
from app.models.database import SessionLocal, init_db
from app.models.product import ProductList
from app.services.scoring_service import ScoringService


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


def show_scoring_config():
    """Display current scoring configuration"""
    print("\n⚖️  Scoring Configuration:")
    print(f"   Version: {SCORING_VERSION}")
    print(f"   Ingredient Quality: {SCORE_WEIGHT_INGREDIENTS * 100:.0f}%")
    print(f"   Nutritional Value: {SCORE_WEIGHT_NUTRITION * 100:.0f}%")
    print(f"   Processing Method: {SCORE_WEIGHT_PROCESSING * 100:.0f}%")
    print(f"   Price-Value Ratio: {SCORE_WEIGHT_PRICE_VALUE * 100:.0f}%")

    total_weight = (
        SCORE_WEIGHT_INGREDIENTS
        + SCORE_WEIGHT_NUTRITION
        + SCORE_WEIGHT_PROCESSING
        + SCORE_WEIGHT_PRICE_VALUE
    )
    print(f"   Total Weight: {total_weight * 100:.0f}%")

    if abs(total_weight - 1.0) > 0.01:
        print("   ⚠️  WARNING: Weights do not sum to 100%!")


def calculate_single_score(product_id: int, force: bool = False):
    """
    Calculate score for a single product by ID.

    Args:
        product_id: Product ID to score
        force: Force recalculate even if already scored
    """
    db = SessionLocal()
    try:
        scoring_service = ScoringService(db)

        product = db.query(ProductList).filter(ProductList.id == product_id).first()

        if not product:
            print(f"❌ Product with ID {product_id} not found")
            return False

        if product.scored and not force:
            print(
                f"⚠️  Product {product_id} already scored (use --force to recalculate)"
            )
            # Show existing score
            existing_score = scoring_service.get_score_by_product_id(product_id)
            if existing_score:
                print(f"   Current score: {existing_score.total_score:.2f}/100")
            return False

        if not product.scraped or product.skipped:
            print(f"❌ Product {product_id} has not been scraped or was skipped")
            return False

        if not product.processed:
            print(f"❌ Product {product_id} has not been processed yet")
            print(
                "💡 Run: python scripts/process_products.py --product-id {product_id}"
            )
            return False

        if not product.details:
            print(f"❌ Product {product_id} has no details")
            return False

        print(f"\n📊 Calculating score for product {product_id}")
        print(f"   {product.details.product_name}")

        # Calculate score
        score = scoring_service.calculate_product_score(
            product_id=product_id, force_recalculate=force
        )

        if score:
            print(f"\n✅ Score calculated successfully!")
            print(f"   Total Score: {score.total_score:.2f}/100")
            print(f"\n   Component Breakdown:")
            for component in score.components:
                print(
                    f"     {component.component_name:20s}: "
                    f"{component.component_score:.2f} "
                    f"(weighted: {component.weighted_score:.2f})"
                )
            return True
        else:
            print(f"❌ Failed to calculate score for product {product_id}")
            return False

    except Exception as e:
        print(f"❌ Error calculating score for product {product_id}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        db.close()


def calculate_batch_scores(limit: int = None, offset: int = 0, force: bool = False):
    """
    Calculate scores for multiple products in batch.

    Args:
        limit: Maximum number of products to score
        offset: Number of products to skip
        force: Force recalculate already scored products
    """
    db = SessionLocal()
    try:
        scoring_service = ScoringService(db)

        # Build query
        query = db.query(ProductList).filter(
            ProductList.scraped == True,
            ProductList.processed == True,
            ProductList.skipped == False,
        )

        if not force:
            query = query.filter(ProductList.scored == False)

        query = query.order_by(ProductList.id).offset(offset)

        if limit:
            query = query.limit(limit)

        products = query.all()
        total = len(products)

        if total == 0:
            if force:
                print("✅ All products already scored!")
            else:
                print("✅ No unscored products found!")
                print("💡 Use --force to recalculate already scored products")
            return

        print(f"\n📊 Found {total} product(s) to score")
        if offset > 0:
            print(f"📍 Starting from offset: {offset}")
        if limit:
            print(f"📊 Limited to: {limit} products")

        print("\n" + "=" * 70)

        success_count = 0
        fail_count = 0
        start_time = datetime.now()
        total_score_sum = 0.0

        for idx, product in enumerate(products, 1):
            print(f"\n[{idx}/{total}] Scoring product {product.id}")

            if not product.details:
                print("  ⚠️  No details found, skipping...")
                fail_count += 1
                continue

            print(f"  📦 {product.details.product_name[:60]}...")

            try:
                score = scoring_service.calculate_product_score(
                    product_id=product.id, force_recalculate=force
                )

                if score:
                    success_count += 1
                    total_score_sum += score.total_score
                    print(f"  ✅ Score: {score.total_score:.2f}/100")

                    # Show component breakdown
                    for component in score.components:
                        print(
                            f"     - {component.component_name}: "
                            f"{component.component_score:.2f}"
                        )
                else:
                    fail_count += 1
                    print(f"  ❌ Failed to calculate score")

            except Exception as e:
                fail_count += 1
                print(f"  ❌ Error: {str(e)}")
                continue

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print(f"✅ Scoring completed in {duration:.2f} seconds!")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {fail_count}")
        print(f"   Total: {total}")

        if success_count > 0:
            avg_score = total_score_sum / success_count
            avg_time = duration / success_count
            print(f"   Average Score: {avg_score:.2f}/100")
            print(f"   Average Time: {avg_time:.2f}s per product")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


def show_statistics():
    """Show scoring statistics"""
    db = SessionLocal()
    try:
        total = db.query(ProductList).count()
        scraped = db.query(ProductList).filter(ProductList.scraped == True).count()
        processed = db.query(ProductList).filter(ProductList.processed == True).count()
        scored = db.query(ProductList).filter(ProductList.scored == True).count()
        unscored = (
            db.query(ProductList)
            .filter(
                ProductList.scraped == True,
                ProductList.processed == True,
                ProductList.scored == False,
                ProductList.skipped == False,
            )
            .count()
        )

        print("\n📊 Scoring Statistics:")
        print(f"   Total products: {total}")
        print(f"   Scraped: {scraped}")
        print(f"   Processed: {processed}")
        print(f"   Scored: {scored}")
        print(f"   Unscored: {unscored}")

        if processed > 0:
            scored_pct = (scored / processed) * 100
            print(f"   Progress: {scored_pct:.1f}%")

        # Get average score if any exist
        if scored > 0:
            scoring_service = ScoringService(db)
            stats = scoring_service.get_score_statistics()
            print(f"   Average Score: {stats['average_score']:.2f}/100")
            print(f"   Min Score: {stats['min_score']:.2f}/100")
            print(f"   Max Score: {stats['max_score']:.2f}/100")

    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    finally:
        db.close()


def main():
    """Main function"""
    print("=" * 70)
    print("📊 Dog Food Scoring API - Score Calculator")
    print("=" * 70)

    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        sys.exit(1)

    # Show scoring configuration
    show_scoring_config()

    # Parse arguments
    args = parse_arguments()

    # Show statistics first
    show_statistics()

    # Calculate single score or batch
    if args["product_id"]:
        print("\n📍 Calculating score for single product...")
        success = calculate_single_score(args["product_id"], force=args["force"])
        sys.exit(0 if success else 1)
    else:
        print("\n🚀 Starting batch score calculation...")
        calculate_batch_scores(
            limit=args["limit"], offset=args["offset"], force=args["force"]
        )

    # Show final statistics
    print("\n" + "=" * 70)
    show_statistics()
    print("=" * 70)

    print("\n💡 Scores calculated! Access via API:")
    print("   http://localhost:8000/api/v1/scores/top")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
