#!/usr/bin/env python3
"""
Dog Food Scoring API - Unified CLI Tool

This is the main command-line interface for all manual operations including
scraping, processing, and scoring.

Usage:
    python scripts/main.py [command] [options]

Commands:
    --scrape, -s           Scrape product URLs from Chewy.com
    --scrape --details     Scrape detailed product information
    --process, -p          Process and normalize product data
    --category             Process food categories (use with --process)
    --sourcing             Process sourcing integrity (use with --process)
    --processing           Process processing methods (use with --process)
    --ingredient-quality   Process ingredient quality (use with --process)
    --longevity-additives   Process longevity additives (use with --process)
    --nutritionally-adequate Process nutritionally adequate status (use with --process)
    --starchy-carb         Process starchy carb extraction (use with --process)
    --score, -sc           Calculate quality scores for products
    --all, -a              Run complete pipeline (scrape → process → score)
    --stats                Show statistics for all stages

Options:
    --limit, -l N          Limit number of items to process
    --offset, -o N         Start from offset N
    --force, -f            Force re-processing/re-scoring
    --test, -t             Test mode (limited scope)
    --product-id, -pid N   Process/score single product by ID
    --test-url, -tu URL    Test scrape single product by URL
    --product-url, --product_url, -pu URL Scrape single product by URL (must exist in DB)
    --reprocess-category C Reprocess specific category (Raw/Fresh/Dry/Wet/Other)
    --reprocess-sourcing S Reprocess sourcing integrity (Human Grade (organic)/Human Grade/Feed Grade/Other)
    --reprocess-processing P Reprocess processing method (Freeze Dried/Extruded/Baked/etc.)
    --reprocess-quality Q Reprocess ingredient quality class (High/Good/Moderate/Low)
    --help, -h             Show this help message

Examples:
    # Scrape product list (pages 1-138)
    python scripts/main.py --scrape

    # Scrape product details (all unscraped)
    python scripts/main.py --scrape --details

    # Scrape with limit
    python scripts/main.py --scrape --details --limit 100

    # Test scrape first page only
    python scripts/main.py --scrape --test

    # Scrape single product by URL (must exist in product_list)
    python scripts/main.py --scrape --details --product-url https://www.chewy.com/...
    python cli.py --scrape --details --product_url https://www.chewy.com/...

    # Process all unprocessed products
    python scripts/main.py --process

    # Process food categories
    python scripts/main.py --process --category
    python scripts/main.py --process --category --limit 100

    # Process single product category
    python scripts/main.py --process --category --product-id 123

    # Reprocess specific category
    python scripts/main.py --process --category --reprocess-category Dry

    # Process sourcing integrity
    python scripts/main.py --process --sourcing
    python scripts/main.py --process --sourcing --limit 100

    # Reprocess specific sourcing integrity
    python scripts/main.py --process --sourcing --reprocess-sourcing "Human Grade"

    # Process processing methods
    python scripts/main.py --process --processing
    python scripts/main.py --process --processing --limit 100

    # Reprocess specific processing method
    python scripts/main.py --process --processing --reprocess-processing "Freeze Dried"

    # Process ingredient quality
    python scripts/main.py --process --ingredient-quality
    python scripts/main.py --process --ingredient-quality --limit 100

    # Reprocess specific quality class
    python scripts/main.py --process --ingredient-quality --reprocess-quality "High"

    # Process longevity additives
    python scripts/main.py --process --longevity-additives
    python scripts/main.py --process --longevity-additives --limit 100

    # Process nutritionally adequate status
    python scripts/main.py --process --nutritionally-adequate
    python scripts/main.py --process --nutritionally-adequate --limit 100

    # Process starchy carb extraction
    python scripts/main.py --process --starchy-carb
    python scripts/main.py --process --starchy-carb --limit 100

    # Calculate scores for all unscored products
    python scripts/main.py --score

    # Run complete pipeline
    python scripts/main.py --all

    # Process single product
    python scripts/main.py --process --product-id 123

    # Show statistics
    python scripts/main.py --stats

    # Force recalculate all scores (limited)
    python scripts/main.py --score --force --limit 50
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

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
from app.scraper.chewy_scraper import ChewyScraperUCD
from app.services.scoring_service import ScoringService


class UnifiedCLI:
    """Unified command-line interface for all operations"""

    def __init__(self):
        self.args = self.parse_arguments()
        self.db = None
        self.scraper = None

    def parse_arguments(self):
        """Parse command line arguments"""
        args = {
            # Commands
            "scrape": False,
            "details": False,
            "process": False,
            "category": False,
            "sourcing": False,
            "processing": False,
            "ingredient_quality": False,
            "longevity_additives": False,
            "nutritionally_adequate": False,
            "starchy_carb": False,
            "score": False,
            "all": False,
            "stats": False,
            # Options
            "limit": None,
            "offset": 0,
            "force": False,
            "test": False,
            "product_id": None,
            "test_url": None,
            "product_url": None,
            "reprocess_category": None,
            "reprocess_sourcing": None,
            "reprocess_processing": None,
            "reprocess_quality": None,
            "help": False,
        }

        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]

            # Commands
            if arg in ["--scrape", "-s"]:
                args["scrape"] = True
                i += 1
            elif arg in ["--details", "-d"]:
                args["details"] = True
                i += 1
            elif arg in ["--process", "-p"]:
                args["process"] = True
                i += 1
            elif arg in ["--category"]:
                args["category"] = True
                i += 1
            elif arg in ["--sourcing"]:
                args["sourcing"] = True
                i += 1
            elif arg in ["--processing"]:
                args["processing"] = True
                i += 1
            elif arg in ["--ingredient-quality"]:
                args["ingredient_quality"] = True
                i += 1
            elif arg in ["--longevity-additives"]:
                args["longevity_additives"] = True
                i += 1
            elif arg in ["--nutritionally-adequate"]:
                args["nutritionally_adequate"] = True
                i += 1
            elif arg in ["--starchy-carb"]:
                args["starchy_carb"] = True
                i += 1
            elif arg in ["--score", "-sc"]:
                args["score"] = True
                i += 1
            elif arg in ["--all", "-a"]:
                args["all"] = True
                i += 1
            elif arg in ["--stats"]:
                args["stats"] = True
                i += 1

            # Options
            elif arg in ["--limit", "-l"] and i + 1 < len(sys.argv):
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

            elif arg in ["--test", "-t"]:
                args["test"] = True
                i += 1

            elif arg in ["--product-id", "-pid"] and i + 1 < len(sys.argv):
                try:
                    args["product_id"] = int(sys.argv[i + 1])
                    i += 2
                except ValueError:
                    print(f"❌ Invalid product ID: {sys.argv[i + 1]}")
                    sys.exit(1)

            elif arg in ["--test-url", "-tu"] and i + 1 < len(sys.argv):
                args["test_url"] = sys.argv[i + 1]
                i += 2

            elif arg in ["--product-url", "--product_url", "-pu"] and i + 1 < len(sys.argv):
                args["product_url"] = sys.argv[i + 1]
                i += 2

            elif arg in ["--reprocess-category"] and i + 1 < len(sys.argv):
                category = sys.argv[i + 1]
                if category in ["Raw", "Fresh", "Dry", "Wet", "Other"]:
                    args["reprocess_category"] = category
                    i += 2
                else:
                    print(f"❌ Invalid category: {category}")
                    print("Valid categories: Raw, Fresh, Dry, Wet, Other")
                    sys.exit(1)

            elif arg in ["--reprocess-sourcing"] and i + 1 < len(sys.argv):
                sourcing = sys.argv[i + 1]
                if sourcing in [
                    "Human Grade (organic)",
                    "Human Grade",
                    "Feed Grade",
                    "Other",
                ]:
                    args["reprocess_sourcing"] = sourcing
                    i += 2
                else:
                    print(f"❌ Invalid sourcing integrity: {sourcing}")
                    print(
                        "Valid values: 'Human Grade (organic)', 'Human Grade', 'Feed Grade', 'Other'"
                    )
                    sys.exit(1)

            elif arg in ["--reprocess-processing"] and i + 1 < len(sys.argv):
                processing = sys.argv[i + 1]
                valid_methods = [
                    "Uncooked (Not Frozen)",
                    "Uncooked (Flash Frozen)",
                    "Uncooked (Frozen)",
                    "Lightly Cooked (Not Frozen)",
                    "Lightly Cooked (Frozen)",
                    "Freeze Dried",
                    "Air Dried",
                    "Dehydrated",
                    "Baked",
                    "Extruded",
                    "Retorted",
                    "Other",
                ]
                if processing in valid_methods:
                    args["reprocess_processing"] = processing
                    i += 2
                else:
                    print(f"❌ Invalid processing method: {processing}")
                    print(
                        "Valid methods: 'Uncooked (Not Frozen)', 'Uncooked (Flash Frozen)', 'Uncooked (Frozen)', "
                        "'Lightly Cooked (Not Frozen)', 'Lightly Cooked (Frozen)', 'Freeze Dried', 'Air Dried', "
                        "'Dehydrated', 'Baked', 'Extruded', 'Retorted', 'Other'"
                    )
                    sys.exit(1)

            elif arg in ["--reprocess-quality"] and i + 1 < len(sys.argv):
                quality = sys.argv[i + 1]
                valid_qualities = ["High", "Good", "Moderate", "Low"]
                if quality in valid_qualities:
                    args["reprocess_quality"] = quality
                    i += 2
                else:
                    print(f"❌ Invalid quality class: {quality}")
                    print(f"Valid qualities: {', '.join(valid_qualities)}")
                    sys.exit(1)

            elif arg in ["--help", "-h"]:
                args["help"] = True
                i += 1
            else:
                print(f"❌ Unknown argument: {arg}")
                print("Use --help for usage information")
                sys.exit(1)

        return args

    def show_help(self):
        """Display help message"""
        print(__doc__)

    def show_header(self):
        """Display application header"""
        print("=" * 70)
        print("🐕 Dog Food Scoring API - Unified CLI Tool")
        print("=" * 70)
        print()

    def show_statistics(self):
        """Show comprehensive statistics"""
        self.db = SessionLocal()
        try:
            from app.models.product import ProductDetails

            total = self.db.query(ProductList).count()
            scraped = (
                self.db.query(ProductList).filter(ProductList.scraped == True).count()
            )

            # Count products with details (considered "processed")
            processed = (
                self.db.query(ProductList)
                .join(ProductDetails)
                .filter(ProductList.scraped == True)
                .count()
            )

            # Count products with scores
            try:
                from app.models.score import ProductScore

                scored = self.db.query(ProductList).join(ProductScore).count()
            except:
                scored = 0

            unscraped = (
                self.db.query(ProductList)
                .filter(ProductList.scraped == False, ProductList.skipped == False)
                .count()
            )

            # Products scraped but without details
            unprocessed = (
                self.db.query(ProductList)
                .outerjoin(ProductDetails)
                .filter(
                    ProductList.scraped == True,
                    ProductDetails.id == None,
                    ProductList.skipped == False,
                )
                .count()
            )

            # Products with details but no scores
            try:
                from app.models.score import ProductScore

                unscored = (
                    self.db.query(ProductList)
                    .join(ProductDetails)
                    .outerjoin(ProductScore)
                    .filter(
                        ProductList.scraped == True,
                        ProductScore.id == None,
                        ProductList.skipped == False,
                    )
                    .count()
                )
            except:
                unscored = processed  # All processed products are unscored if table doesn't exist
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
        finally:
            self.db.close()

    def _progress_bar(self, percentage: float, width: int = 20) -> str:
        """Generate a progress bar string"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return bar

    def run_scrape(self):
        """Run scraping operation"""
        print("\n" + "=" * 70)
        print("🕷️  SCRAPING")
        print("=" * 70)

        try:
            self.scraper = ChewyScraperUCD()

            if self.args["product_url"]:
                # Scrape single product by URL (must exist in DB)
                from app.models.database import SessionLocal
                from app.models.product import ProductList

                product_url = self.args["product_url"]
                print(f"\n📦 Scraping product by URL")
                print(f"   URL: {product_url}")

                db = SessionLocal()
                try:
                    # Check if URL exists in product_list
                    product = (
                        db.query(ProductList)
                        .filter_by(product_url=product_url)
                        .first()
                    )

                    if not product:
                        print(f"\n⚠️  Product URL not found in database")
                        print(f"   URL: {product_url}")
                        print(f"   Skipping...")
                        return

                    print(f"   Found product ID: {product.id}")
                    print(f"   Product already scraped: {product.scraped}")

                    # Scrape product details
                    details = self.scraper.scrape_product_details(
                        product.product_url, product.product_image_url
                    )

                    if details:
                        # Save to database
                        if self.scraper.save_product_details(product.id, details):
                            print(f"\n✅ Successfully scraped and saved product details")
                        else:
                            print(f"\n❌ Failed to save product details")
                    else:
                        print(f"\n⚠️  No details extracted - marking as skipped")
                        self.scraper.mark_product_as_skipped(product.id)

                finally:
                    db.close()

            elif self.args["test_url"]:
                # Test single product by URL
                print(f"\n🧪 Test mode: Scraping single product")
                print(f"   URL: {self.args['test_url']}")
                self.scraper.scrape_product_by_url(self.args["test_url"])

            elif self.args["details"]:
                # Scrape product details
                print("\n📦 Scraping product details...")

                if self.args["test"]:
                    print("🧪 Test mode: Scraping first 5 unscraped products")
                    self.scraper.scrape_all_product_details(limit=5)
                else:
                    self.scraper.scrape_all_product_details(
                        limit=self.args["limit"], offset=self.args["offset"]
                    )

            else:
                # Scrape product list
                print("\n📋 Scraping product list...")

                if self.args["test"]:
                    print("🧪 Test mode: Scraping page 1 only")
                    self.scraper.scrape_all(start=1, end=1)
                else:
                    print("📄 Scraping pages 1-138...")
                    self.scraper.scrape_all(start=1, end=138)

            print("\n✅ Scraping completed!")

        except Exception as e:
            print(f"\n❌ Scraping error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.scraper:
                self.scraper.close()

    def run_process(self):
        """Run processing operation"""
        # Check if category processing requested
        if self.args["category"]:
            self.run_category_processing()
            return

        print("\n" + "=" * 70)
        print("🔧 PROCESSING")
        print("=" * 70)

        self.db = SessionLocal()
        try:
            # Handle single product
            if self.args["product_id"]:
                self._process_single_product(self.args["product_id"])
                return

            # Handle batch processing
            from app.models.product import ProductDetails

            if not self.args["force"]:
                # Get products that are scraped but don't have details yet
                query = (
                    self.db.query(ProductList)
                    .outerjoin(ProductDetails)
                    .filter(
                        ProductList.scraped == True,
                        ProductList.skipped == False,
                        ProductDetails.id == None,
                    )
                    .order_by(ProductList.id)
                    .offset(self.args["offset"])
                )
            else:
                # Force mode: get all scraped products
                query = (
                    self.db.query(ProductList)
                    .filter(ProductList.scraped == True, ProductList.skipped == False)
                    .order_by(ProductList.id)
                    .offset(self.args["offset"])
                )

            if self.args["limit"]:
                query = query.limit(self.args["limit"])

            products = query.all()
            total = len(products)

            if total == 0:
                print("\n✅ No products to process!")
                return

            print(f"\n📊 Found {total} product(s) to process")
            print("\n⚠️  Note: Specific processors not yet fully implemented")
            print("⚠️  This will verify products have details")

            success = 0
            failed = 0

            for idx, product in enumerate(products, 1):
                print(f"\n[{idx}/{total}] Checking product {product.id}")
                if product.details:
                    print(f"  📦 {product.details.product_name[:60]}...")
                    print("  ✅ Product has details (considered processed)")
                    success += 1
                else:
                    print("  ⚠️  No details found, needs scraping")
                    failed += 1

            print(f"\n✅ Processing completed!")
            print(f"   Success: {success}")
            print(f"   Failed: {failed}")

        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def run_category_processing(self):
        """Run food category classification"""
        from app.processors.food_category_processor import FoodCategoryProcessor

        print("\n" + "=" * 70)
        print("🔧 FOOD CATEGORY PROCESSING")
        print("=" * 70)

        self.db = SessionLocal()
        try:
            processor = FoodCategoryProcessor(self.db, processor_version="v1.0.0")

            # Handle single product
            if self.args["product_id"]:
                from app.models.product import ProductDetails

                pid = self.args["product_id"]
                print(f"\nProcessing single product (ID={pid})")
                # Try treating as ProductDetails.id first
                detail = (
                    self.db.query(ProductDetails)
                    .filter(ProductDetails.id == pid)
                    .first()
                )
                if not detail:
                    # Fallback: treat as ProductList.id (ProductDetails.product_id)
                    detail = (
                        self.db.query(ProductDetails)
                        .filter(ProductDetails.product_id == pid)
                        .first()
                    )
                if not detail:
                    print(f"\n❌ Could not find ProductDetails for ID={pid}")
                    print(
                        "   Provide a ProductDetails.id or a ProductList.id that has details."
                    )
                    return
                try:
                    result = processor.process_single(detail.id)
                    print(f"\n✅ Success!")
                    print(f"  Product Detail ID: {result.product_detail_id}")
                    print(f"  Food Category:     {result.food_category}")
                    print(f"  Reason:            {result.category_reason}")
                    print(f"  Processed At:      {result.processed_at}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                return

            # Handle reprocess category
            if self.args["reprocess_category"]:
                category = self.args["reprocess_category"]
                print(f"\nReprocessing category: {category}")
                if self.args["limit"]:
                    print(f"Limit: {self.args['limit']}")

                results = processor.reprocess_category(
                    category, limit=self.args["limit"]
                )

                print(f"\n✅ Reprocessing completed!")
                print(f"   Total:   {results['total']}")
                print(f"   Success: {results['success']}")
                print(f"   Failed:  {results['failed']}")
                return

            # Handle batch processing
            print(f"\nProcessing all products")
            if self.args["limit"]:
                print(f"Limit: {self.args['limit']}")
            print(f"Mode: {'Reprocess all' if self.args['force'] else 'Skip existing'}")

            results = processor.process_all(
                limit=self.args["limit"], skip_existing=not self.args["force"]
            )

            print(f"\n✅ Processing completed!")
            print(f"   Total:   {results['total']}")
            print(f"   Success: {results['success']}")
            print(f"   Failed:  {results['failed']}")

            # Show statistics
            print()
            processor.print_statistics()

        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def run_sourcing_processing(self):
        """Run sourcing integrity classification"""
        from app.processors.sourcing_integrity_processor import (
            SourcingIntegrityProcessor,
        )

        print("\n" + "=" * 70)
        print("🔧 SOURCING INTEGRITY PROCESSING")
        print("=" * 70)

        self.db = SessionLocal()
        try:
            processor = SourcingIntegrityProcessor(self.db, processor_version="v1.0.0")

            # Handle single product
            if self.args["product_id"]:
                from app.models.product import ProductDetails

                pid = self.args["product_id"]
                print(f"\nProcessing single product (ID={pid})")
                # Try treating as ProductDetails.id first
                detail = (
                    self.db.query(ProductDetails)
                    .filter(ProductDetails.id == pid)
                    .first()
                )
                if not detail:
                    # Fallback: treat as ProductList.id (ProductDetails.product_id)
                    detail = (
                        self.db.query(ProductDetails)
                        .filter(ProductDetails.product_id == pid)
                        .first()
                    )
                if not detail:
                    print(f"\n❌ Could not find ProductDetails for ID={pid}")
                    print(
                        "   Provide a ProductDetails.id or a ProductList.id that has details."
                    )
                    return
                try:
                    result = processor.process_single(detail.id)
                    print(f"\n✅ Success!")
                    print(f"  Product Detail ID:     {result.product_detail_id}")
                    print(f"  Sourcing Integrity:    {result.sourcing_integrity}")
                    print(
                        f"  Reason:                {result.sourcing_integrity_reason}"
                    )
                    print(f"  Processed At:          {result.processed_at}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                return

            # Handle reprocess sourcing
            if self.args["reprocess_sourcing"]:
                sourcing = self.args["reprocess_sourcing"]
                print(f"\nReprocessing sourcing integrity: {sourcing}")
                if self.args["limit"]:
                    print(f"Limit: {self.args['limit']}")

                results = processor.reprocess_category(
                    sourcing, limit=self.args["limit"]
                )

                print(f"\n✅ Reprocessing completed!")
                print(f"   Total:   {results['total']}")
                print(f"   Success: {results['success']}")
                print(f"   Failed:  {results['failed']}")
                return

            # Handle batch processing
            print(f"\nProcessing all products")
            if self.args["limit"]:
                print(f"Limit: {self.args['limit']}")
            print(f"Mode: {'Reprocess all' if self.args['force'] else 'Skip existing'}")

            results = processor.process_all(
                limit=self.args["limit"], skip_existing=not self.args["force"]
            )

            print(f"\n✅ Processing completed!")
            print(f"   Total:   {results['total']}")
            print(f"   Success: {results['success']}")
            print(f"   Failed:  {results['failed']}")

            # Show statistics
            print()
            processor.print_statistics()

        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def run_processing_method_processing(self):
        """Run processing method classification"""
        from app.processors.processing_method_processor import (
            ProcessingMethodProcessor,
        )

        print("\n" + "=" * 70)
        print("🔧 PROCESSING METHOD CLASSIFICATION")
        print("=" * 70)

        self.db = SessionLocal()
        try:
            processor = ProcessingMethodProcessor(self.db, processor_version="v1.0.0")

            # Handle single product
            if self.args["product_id"]:
                from app.models.product import ProductDetails

                pid = self.args["product_id"]
                print(f"\nProcessing single product (ID={pid})")
                # Try treating as ProductDetails.id first
                detail = (
                    self.db.query(ProductDetails)
                    .filter(ProductDetails.id == pid)
                    .first()
                )
                if not detail:
                    # Fallback: treat as ProductList.id (ProductDetails.product_id)
                    detail = (
                        self.db.query(ProductDetails)
                        .filter(ProductDetails.product_id == pid)
                        .first()
                    )
                if not detail:
                    print(f"\n❌ Could not find ProductDetails for ID={pid}")
                    print(
                        "   Provide a ProductDetails.id or a ProductList.id that has details."
                    )
                    return
                try:
                    result = processor.process_single(detail.id)
                    print(f"\n✅ Success!")
                    print(f"  Product Detail ID:     {result.product_detail_id}")
                    print(f"  Processing Method 1:   {result.processing_method_1}")
                    print(f"  Processing Method 2:   {result.processing_method_2}")
                    print(
                        f"  Reason:                {result.processing_adulteration_method_reason}"
                    )
                    print(f"  Processed At:          {result.processed_at}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                return

            # Handle reprocess processing method
            if self.args["reprocess_processing"]:
                processing = self.args["reprocess_processing"]
                print(f"\nReprocessing processing method: {processing}")
                if self.args["limit"]:
                    print(f"Limit: {self.args['limit']}")

                results = processor.reprocess_method(
                    processing, limit=self.args["limit"]
                )

                print(f"\n✅ Reprocessing completed!")
                print(f"   Total:   {results['total']}")
                print(f"   Success: {results['success']}")
                print(f"   Failed:  {results['failed']}")
                return

            # Handle batch processing
            print(f"\nProcessing all products")
            if self.args["limit"]:
                print(f"Limit: {self.args['limit']}")
            print(f"Mode: {'Reprocess all' if self.args['force'] else 'Skip existing'}")

            results = processor.process_all(
                limit=self.args["limit"], skip_existing=not self.args["force"]
            )

            print(f"\n✅ Processing completed!")
            print(f"   Total:   {results['total']}")
            print(f"   Success: {results['success']}")
            print(f"   Failed:  {results['failed']}")

            # Show statistics
            print()
            processor.print_statistics()

        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def run_ingredient_quality_processing(self):
        """Run ingredient quality classification"""
        from app.processors.ingredient_quality_processor import (
            IngredientQualityProcessor,
        )

        print("\n" + "=" * 70)
        print("🔧 INGREDIENT QUALITY PROCESSING")
        print("=" * 70)

        self.db = SessionLocal()
        try:
            processor = IngredientQualityProcessor(self.db, processor_version="v1.0.0")

            # Handle single product
            if self.args["product_id"]:
                from app.models.product import ProductDetails

                pid = self.args["product_id"]
                print(f"\nProcessing single product (ID={pid})")
                # Try treating as ProductDetails.id first
                detail = (
                    self.db.query(ProductDetails)
                    .filter(ProductDetails.id == pid)
                    .first()
                )
                if not detail:
                    # Fallback: treat as ProductList.id (ProductDetails.product_id)
                    detail = (
                        self.db.query(ProductDetails)
                        .filter(ProductDetails.product_id == pid)
                        .first()
                    )
                if not detail:
                    print(f"\n❌ Could not find ProductDetails for ID={pid}")
                    print(
                        "   Provide a ProductDetails.id or a ProductList.id that has details."
                    )
                    return
                try:
                    result = processor.process_single(detail.id)
                    print(f"\n✅ Success!")
                    print(f"  Product Detail ID:     {result.product_detail_id}")
                    print(f"  Protein Quality:       {result.protein_quality_class}")
                    print(f"  Fat Quality:           {result.fat_quality_class}")
                    print(f"  Carb Quality:          {result.carb_quality_class}")
                    print(f"  Fiber Quality:         {result.fiber_quality_class}")
                    print(f"  Dirty Dozen Count:     {result.dirty_dozen_ingredients_count}")
                    print(f"  Synthetic Nutrition:   {result.synthetic_nutrition_addition_count}")
                    print(f"  Processed At:          {result.processed_at}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                return

            # Handle reprocess quality class
            if self.args["reprocess_quality"]:
                quality = self.args["reprocess_quality"]
                print(f"\nReprocessing quality class: {quality}")
                if self.args["limit"]:
                    print(f"Limit: {self.args['limit']}")

                results = processor.reprocess_quality_class(
                    quality, limit=self.args["limit"]
                )

                print(f"\n✅ Reprocessing completed!")
                print(f"   Total:   {results['total']}")
                print(f"   Success: {results['success']}")
                print(f"   Failed:  {results['failed']}")
                return

            # Handle batch processing
            print(f"\nProcessing all products")
            if self.args["limit"]:
                print(f"Limit: {self.args['limit']}")
            print(f"Mode: {'Reprocess all' if self.args['force'] else 'Skip existing'}")

            results = processor.process_all(
                limit=self.args["limit"], skip_existing=not self.args["force"]
            )

            print(f"\n✅ Processing completed!")
            print(f"   Total:   {results['total']}")
            print(f"   Success: {results['success']}")
            print(f"   Failed:  {results['failed']}")

            # Show statistics
            print()
            processor.print_statistics()

        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def run_longevity_additives_processing(self):
        """Run longevity additives identification"""
        from app.processors.longevity_additives_processor import (
            LongevityAdditivesProcessor,
        )

        print("\n" + "=" * 70)
        print("🔧 LONGEVITY ADDITIVES PROCESSING")
        print("=" * 70)

        self.db = SessionLocal()
        try:
            processor = LongevityAdditivesProcessor(
                self.db, processor_version="v1.0.0"
            )

            # Handle single product
            if self.args["product_id"]:
                from app.models.product import ProductDetails

                pid = self.args["product_id"]
                print(f"\nProcessing single product (ID={pid})")
                # Try treating as ProductDetails.id first
                detail = (
                    self.db.query(ProductDetails)
                    .filter(ProductDetails.id == pid)
                    .first()
                )
                if not detail:
                    # Fallback: treat as ProductList.id (ProductDetails.product_id)
                    detail = (
                        self.db.query(ProductDetails)
                        .filter(ProductDetails.product_id == pid)
                        .first()
                    )
                if not detail:
                    print(f"\n❌ Could not find ProductDetails for ID={pid}")
                    print(
                        "   Provide a ProductDetails.id or a ProductList.id that has details."
                    )
                    return
                try:
                    result = processor.process_single(detail.id)
                    print(f"\n✅ Success!")
                    print(f"  Product Detail ID:     {result.product_detail_id}")
                    print(f"  Longevity Additives:    {result.longevity_additives}")
                    print(f"  Additives Count:        {result.longevity_additives_count}")
                    print(f"  Processed At:          {result.processed_at}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                return

            # Handle batch processing
            print(f"\nProcessing all products")
            if self.args["limit"]:
                print(f"Limit: {self.args['limit']}")
            print(f"Mode: {'Reprocess all' if self.args['force'] else 'Skip existing'}")

            results = processor.process_all(
                limit=self.args["limit"], skip_existing=not self.args["force"]
            )

            print(f"\n✅ Processing completed!")
            print(f"   Total:   {results['total']}")
            print(f"   Success: {results['success']}")
            print(f"   Failed:  {results['failed']}")

            # Show statistics
            print()
            processor.print_statistics()

        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def run_nutritionally_adequate_processing(self):
        """Run nutritionally adequate status classification"""
        from app.processors.nutritionally_adequate_processor import (
            NutritionallyAdequateProcessor,
        )

        print("\n" + "=" * 70)
        print("🔧 NUTRITIONALLY ADEQUATE PROCESSING")
        print("=" * 70)

        self.db = SessionLocal()
        try:
            processor = NutritionallyAdequateProcessor(
                self.db, processor_version="v1.0.0"
            )

            # Handle single product
            if self.args["product_id"]:
                from app.models.product import ProductDetails

                pid = self.args["product_id"]
                print(f"\nProcessing single product (ID={pid})")
                # Try treating as ProductDetails.id first
                detail = (
                    self.db.query(ProductDetails)
                    .filter(ProductDetails.id == pid)
                    .first()
                )
                if not detail:
                    # Fallback: treat as ProductList.id (ProductDetails.product_id)
                    detail = (
                        self.db.query(ProductDetails)
                        .filter(ProductDetails.product_id == pid)
                        .first()
                    )
                if not detail:
                    print(f"\n❌ Could not find ProductDetails for ID={pid}")
                    print(
                        "   Provide a ProductDetails.id or a ProductList.id that has details."
                    )
                    return
                try:
                    result = processor.process_single(detail.id)
                    print(f"\n✅ Success!")
                    print(f"  Product Detail ID:     {result.product_detail_id}")
                    print(f"  Nutritionally Adequate: {result.nutritionally_adequate}")
                    print(f"  Reason:                {result.nutritionally_adequate_reason}")
                    print(f"  Processed At:          {result.processed_at}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                return

            # Handle batch processing
            print(f"\nProcessing all products")
            if self.args["limit"]:
                print(f"Limit: {self.args['limit']}")
            print(f"Mode: {'Reprocess all' if self.args['force'] else 'Skip existing'}")

            results = processor.process_all(
                limit=self.args["limit"], skip_existing=not self.args["force"]
            )

            print(f"\n✅ Processing completed!")
            print(f"   Total:   {results['total']}")
            print(f"   Success: {results['success']}")
            print(f"   Failed:  {results['failed']}")

            # Show statistics
            print()
            processor.print_statistics()

        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def run_starchy_carb_processing(self):
        """Run starchy carb extraction"""
        from app.processors.starchy_carb_processor import StarchyCarbProcessor

        print("\n" + "=" * 70)
        print("🔧 STARCHY CARB PROCESSING")
        print("=" * 70)

        self.db = SessionLocal()
        try:
            processor = StarchyCarbProcessor(self.db, processor_version="v1.0.0")

            # Handle single product
            if self.args["product_id"]:
                from app.models.product import ProductDetails

                pid = self.args["product_id"]
                print(f"\nProcessing single product (ID={pid})")
                # Try treating as ProductDetails.id first
                detail = (
                    self.db.query(ProductDetails)
                    .filter(ProductDetails.id == pid)
                    .first()
                )
                if not detail:
                    # Fallback: treat as ProductList.id (ProductDetails.product_id)
                    detail = (
                        self.db.query(ProductDetails)
                        .filter(ProductDetails.product_id == pid)
                        .first()
                    )
                if not detail:
                    print(f"\n❌ Could not find ProductDetails for ID={pid}")
                    print(
                        "   Provide a ProductDetails.id or a ProductList.id that has details."
                    )
                    return
                try:
                    result = processor.process_single(detail.id)
                    print(f"\n✅ Success!")
                    print(f"  Product Detail ID:     {result.product_detail_id}")
                    print(f"  Protein:               {result.guaranteed_analysis_crude_protein_pct}%")
                    print(f"  Fat:                   {result.guaranteed_analysis_crude_fat_pct}%")
                    print(f"  Fiber:                 {result.guaranteed_analysis_crude_fiber_pct}%")
                    print(f"  Moisture:              {result.guaranteed_analysis_crude_moisture_pct}%")
                    print(f"  Ash:                   {result.guaranteed_analysis_crude_ash_pct}%")
                    print(f"  Starchy Carbs:         {result.starchy_carb_pct}%")
                    print(f"  Processed At:          {result.processed_at}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                return

            # Handle batch processing
            print(f"\nProcessing all products")
            if self.args["limit"]:
                print(f"Limit: {self.args['limit']}")
            print(f"Mode: {'Reprocess all' if self.args['force'] else 'Skip existing'}")

            results = processor.process_all(
                limit=self.args["limit"], skip_existing=not self.args["force"]
            )

            print(f"\n✅ Processing completed!")
            print(f"   Total:   {results['total']}")
            print(f"   Success: {results['success']}")
            print(f"   Failed:  {results['failed']}")

            # Show statistics
            print()
            processor.print_statistics()

        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def _process_single_product(self, pid: int):
        """Process a single product"""
        product = (
            self.db.query(ProductList).filter(ProductList.id == pid).first()
        )

        if not product:
            print(f"\n❌ Product {pid} not found")
            return

        if not product.details:
            print(f"\n❌ Product {pid} has no details")
            return

        print(f"\n📦 Checking product {pid}")
        print(f"   {product.details.product_name}")
        print("\n⚠️  Note: Specific processors not yet fully implemented")
        print("\n✅ Product has details (considered processed)")

    def run_score(self):
        """Run scoring operation"""
        print("\n" + "=" * 70)
        print("📊 SCORING")
        print("=" * 70)

        # Show configuration
        print(f"\n⚖️  Scoring Configuration:")
        print(f"   Version: {SCORING_VERSION}")
        print(f"   Ingredient Quality: {SCORE_WEIGHT_INGREDIENTS * 100:.0f}%")
        print(f"   Nutritional Value: {SCORE_WEIGHT_NUTRITION * 100:.0f}%")
        print(f"   Processing Method: {SCORE_WEIGHT_PROCESSING * 100:.0f}%")
        print(f"   Price-Value Ratio: {SCORE_WEIGHT_PRICE_VALUE * 100:.0f}%")

        self.db = SessionLocal()
        try:
            scoring_service = ScoringService(self.db)

            # Handle single product
            if self.args["product_id"]:
                self._score_single_product(scoring_service, self.args["product_id"])
                return

            # Handle batch scoring
            from app.models.product import ProductDetails

            try:
                from app.models.score import ProductScore

                if not self.args["force"]:
                    # Get products with details but no scores
                    query = (
                        self.db.query(ProductList)
                        .join(ProductDetails)
                        .outerjoin(ProductScore)
                        .filter(
                            ProductList.scraped == True,
                            ProductList.skipped == False,
                            ProductScore.id == None,
                        )
                        .order_by(ProductList.id)
                        .offset(self.args["offset"])
                    )
                else:
                    # Force mode: get all products with details
                    query = (
                        self.db.query(ProductList)
                        .join(ProductDetails)
                        .filter(
                            ProductList.scraped == True,
                            ProductList.skipped == False,
                        )
                        .order_by(ProductList.id)
                        .offset(self.args["offset"])
                    )
            except:
                # If score tables don't exist, get all products with details
                query = (
                    self.db.query(ProductList)
                    .join(ProductDetails)
                    .filter(
                        ProductList.scraped == True,
                        ProductList.skipped == False,
                    )
                    .order_by(ProductList.id)
                    .offset(self.args["offset"])
                )

            if self.args["limit"]:
                query = query.limit(self.args["limit"])

            products = query.all()
            total = len(products)

            if total == 0:
                print("\n✅ No products to score!")
                return

            print(f"\n📊 Found {total} product(s) to score")
            print("\n⚠️  Note: Using placeholder scoring logic")
            print("⚠️  Implement specific scorers for real scores")

            success = 0
            failed = 0
            total_score = 0.0

            for idx, product in enumerate(products, 1):
                print(f"\n[{idx}/{total}] Scoring product {product.id}")
                if product.details:
                    print(f"  📦 {product.details.product_name[:60]}...")

                    try:
                        score = scoring_service.calculate_product_score(
                            product.id, force_recalculate=self.args["force"]
                        )
                        if score:
                            success += 1
                            total_score += score.total_score
                            print(f"  ✅ Score: {score.total_score:.2f}/100")
                        else:
                            failed += 1
                            print("  ❌ Failed to calculate score")
                    except Exception as e:
                        failed += 1
                        print(f"  ❌ Error: {str(e)}")
                else:
                    failed += 1
                    print("  ⚠️  No details found, skipping")

            print(f"\n✅ Scoring completed!")
            print(f"   Success: {success}")
            print(f"   Failed: {failed}")
            if success > 0:
                print(f"   Average Score: {total_score / success:.2f}/100")

        except Exception as e:
            print(f"\n❌ Scoring error: {e}")
            import traceback

            traceback.print_exc()
            raise
        finally:
            if self.db:
                self.db.close()

    def _score_single_product(self, scoring_service, product_id: int):
        """Score a single product"""
        product = (
            self.db.query(ProductList).filter(ProductList.id == product_id).first()
        )

        if not product:
            print(f"\n❌ Product {product_id} not found")
            return

        if not product.details:
            print(f"\n❌ Product {product_id} has no details")
            return

        if not product.details:
            print(f"\n❌ Product {product_id} does not have details")
            print(f"💡 Run: python cli.py --scrape --details --product-id {product_id}")
            return

        print(f"\n📊 Calculating score for product {product_id}")
        print(f"   {product.details.product_name}")

        score = scoring_service.calculate_product_score(
            product_id, force_recalculate=self.args["force"]
        )

        if score:
            print(f"\n✅ Score: {score.total_score:.2f}/100")
            print(f"\n   Component Breakdown:")
            for component in score.components:
                print(
                    f"     {component.component_name:20s}: "
                    f"{component.component_score:.2f} "
                    f"(weighted: {component.weighted_score:.2f})"
                )
        else:
            print("\n❌ Failed to calculate score")

    def run_all(self):
        """Run complete pipeline"""
        print("\n" + "=" * 70)
        print("🚀 RUNNING COMPLETE PIPELINE")
        print("=" * 70)
        print("\nThis will run: Scrape → Process → Score")
        print()

        start_time = datetime.now()

        # Step 1: Scrape
        if not self.args["test"]:
            print("\n⏩ Skipping product list scraping (already done)")
            print("💡 Use --scrape separately if you need to update product list")

        self.args["details"] = True
        if self.args["test"]:
            self.args["limit"] = 5
        self.run_scrape()

        # Step 2: Process
        self.run_process()

        # Step 3: Score
        self.run_score()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print(f"✅ COMPLETE PIPELINE FINISHED!")
        print(f"   Duration: {duration:.2f} seconds ({duration / 60:.1f} minutes)")
        print("=" * 70)

    def run(self):
        """Main run method"""
        # Show help if requested or no commands given
        if self.args["help"] or len(sys.argv) == 1:
            self.show_help()
            return

        # Initialize database
        self.show_header()
        print("🔧 Initializing database...")
        init_db()
        print("✅ Database ready")

        # Show statistics if requested
        if self.args["stats"]:
            self.show_statistics()
            return

        # Execute commands
        try:
            if self.args["all"]:
                self.run_all()
            else:
                if self.args["scrape"]:
                    self.run_scrape()

                if self.args["process"]:
                    if self.args["category"]:
                        self.run_category_processing()
                    elif self.args["sourcing"]:
                        self.run_sourcing_processing()
                    elif self.args["processing"]:
                        self.run_processing_method_processing()
                    elif self.args["ingredient_quality"]:
                        self.run_ingredient_quality_processing()
                    elif self.args["longevity_additives"]:
                        self.run_longevity_additives_processing()
                    elif self.args["nutritionally_adequate"]:
                        self.run_nutritionally_adequate_processing()
                    elif self.args["starchy_carb"]:
                        self.run_starchy_carb_processing()
                    else:
                        self.run_process()

                if self.args["score"]:
                    self.run_score()

            # Show final statistics
            print("\n" + "=" * 70)
            self.show_statistics()
            print("=" * 70)

            print("\n💡 Next Steps:")
            if not self.args["scrape"] and not self.args["all"]:
                print("   • Run scraping: python scripts/main.py --scrape --details")
            if not self.args["process"] and not self.args["all"]:
                print("   • Process data: python scripts/main.py --process")
            if not self.args["score"] and not self.args["all"]:
                print("   • Calculate scores: python scripts/main.py --score")
            print("   • Start API: uvicorn app.main:app --reload")
            print("   • View stats: python scripts/main.py --stats")

        except KeyboardInterrupt:
            print("\n\n⚠️  Operation interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Fatal error: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


def main():
    """Entry point"""
    cli = UnifiedCLI()
    cli.run()


if __name__ == "__main__":
    main()
