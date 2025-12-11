#!/usr/bin/env python3
"""
Data Import/Merge Script

Imports product data from a JSON export file into the database.
Handles duplicates and maintains referential integrity.

Usage:
    python import_data.py export_file.json
    python import_data.py export_file.json --dry-run  # Preview without importing
"""

import json
import sys
from database import SessionLocal, ProductList, ProductDetails
from sqlalchemy.exc import IntegrityError

def import_products(json_file: str, dry_run: bool = False):
    """Import products from JSON file"""
    # Read JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON file: {e}")
        return False
    
    print(f"📦 Importing data from: {json_file}")
    print(f"📅 Export date: {export_data.get('export_date', 'Unknown')}")
    print(f"📊 Total products: {export_data.get('total_products', 0)}")
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")
    
    db = SessionLocal()
    
    stats = {
        'products_added': 0,
        'products_skipped': 0,
        'details_added': 0,
        'details_updated': 0,
        'details_skipped': 0,
        'errors': 0
    }
    
    try:
        for idx, product_data in enumerate(export_data.get('products', []), 1):
            pl_data = product_data.get('product_list', {})
            pd_data = product_data.get('product_details')
            
            # Import ProductList
            product_url = pl_data.get('product_url')
            if not product_url:
                print(f"⚠️  Skipping product {idx}: missing product_url")
                stats['errors'] += 1
                continue
            
            # Check if product exists
            existing_product = db.query(ProductList).filter_by(product_url=product_url).first()
            
            if existing_product:
                # Product exists - update scraped flag if needed
                if not existing_product.scraped and pl_data.get('scraped'):
                    if not dry_run:
                        existing_product.scraped = True
                    stats['products_skipped'] += 1
                    print(f"[{idx}/{len(export_data['products'])}] Product exists: {product_url[:60]}...")
                else:
                    stats['products_skipped'] += 1
                    print(f"[{idx}/{len(export_data['products'])}] Product already exists: {product_url[:60]}...")
                
                product = existing_product
            else:
                # Create new product
                if not dry_run:
                    product = ProductList(
                        product_url=product_url,
                        page_num=pl_data.get('page_num', 0),
                        scraped=pl_data.get('scraped', False),
                        product_image_url=pl_data.get('product_image_url')
                    )
                    db.add(product)
                    db.flush()  # Get the ID
                else:
                    # Create a mock product for dry run
                    class MockProduct:
                        id = 999999
                    product = MockProduct()
                
                stats['products_added'] += 1
                print(f"[{idx}/{len(export_data['products'])}] ✅ Adding product: {product_url[:60]}...")
            
            # Import ProductDetails if exists
            if pd_data:
                if not dry_run:
                    # Check if details exist
                    existing_details = db.query(ProductDetails).filter_by(product_id=product.id).first()
                    
                    if existing_details:
                        # Update existing details
                        for key, value in pd_data.items():
                            if key != 'product_id' and hasattr(existing_details, key):
                                setattr(existing_details, key, value)
                        stats['details_updated'] += 1
                    else:
                        # Create new details
                        details = ProductDetails(
                            product_id=product.id,
                            product_category=pd_data.get('product_category'),
                            product_name=pd_data.get('product_name'),
                            img_link=pd_data.get('img_link'),
                            product_url=pd_data.get('product_url'),
                            price=pd_data.get('price'),
                            size=pd_data.get('size'),
                            details=pd_data.get('details'),
                            more_details=pd_data.get('more_details'),
                            specifications=pd_data.get('specifications'),
                            ingredients=pd_data.get('ingredients'),
                            caloric_content=pd_data.get('caloric_content'),
                            guaranteed_analysis=pd_data.get('guaranteed_analysis'),
                            feeding_instructions=pd_data.get('feeding_instructions'),
                            transition_instructions=pd_data.get('transition_instructions'),
                        )
                        db.add(details)
                        stats['details_added'] += 1
                else:
                    stats['details_added'] += 1
            
            # Commit periodically (every 100 products)
            if not dry_run and idx % 100 == 0:
                try:
                    db.commit()
                    print(f"💾 Committed {idx} products...")
                except IntegrityError as e:
                    db.rollback()
                    print(f"⚠️  Error committing batch: {e}")
                    stats['errors'] += 1
        
        # Final commit
        if not dry_run:
            try:
                db.commit()
                print("\n💾 Final commit completed")
            except IntegrityError as e:
                db.rollback()
                print(f"❌ Error in final commit: {e}")
                stats['errors'] += 1
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 Import Summary:")
        print("=" * 70)
        print(f"✅ Products added: {stats['products_added']}")
        print(f"⏭️  Products skipped (duplicates): {stats['products_skipped']}")
        print(f"✅ Details added: {stats['details_added']}")
        print(f"🔄 Details updated: {stats['details_updated']}")
        print(f"❌ Errors: {stats['errors']}")
        
        if dry_run:
            print("\n🔍 This was a DRY RUN - no changes were made")
        else:
            print("\n✅ Import completed successfully!")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error importing data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <export_file.json> [--dry-run]")
        print("Use --help for more information")
        sys.exit(1)
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\nOptions:")
        print("  --dry-run    Preview import without making changes")
        sys.exit(0)
    
    json_file = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    import_products(json_file, dry_run)

if __name__ == "__main__":
    main()

