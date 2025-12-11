#!/usr/bin/env python3
"""
Data Export Script

Exports scraped product data from the database to a JSON file
for transfer to another computer or backup.

Usage:
    python export_data.py [--output filename.json] [--all]
    python export_data.py --scraped-only  # Only export scraped products (default)
    python export_data.py --all           # Export all products
"""

import json
import sys
from datetime import datetime
from database import SessionLocal, ProductList, ProductDetails
from sqlalchemy.orm import joinedload

def export_products(export_scraped_only: bool = True, output_file: str = None):
    """Export products to JSON file"""
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(ProductList)
        if export_scraped_only:
            query = query.filter_by(scraped=True)
        
        # Load with details
        products = query.options(joinedload(ProductList.details)).all()
        
        print(f"📦 Found {len(products)} products to export")
        
        # Prepare export data
        export_data = {
            'export_date': datetime.now().isoformat(),
            'export_scraped_only': export_scraped_only,
            'total_products': len(products),
            'products': []
        }
        
        for product in products:
            product_data = {
                'product_list': {
                    'id': product.id,
                    'product_url': product.product_url,
                    'page_num': product.page_num,
                    'scraped': product.scraped,
                    'product_image_url': product.product_image_url,
                }
            }
            
            # Add details if exists
            if product.details:
                product_data['product_details'] = {
                    'product_id': product.details.product_id,
                    'product_category': product.details.product_category,
                    'product_name': product.details.product_name,
                    'img_link': product.details.img_link,
                    'product_url': product.details.product_url,
                    'price': product.details.price,
                    'size': product.details.size,
                    'details': product.details.details,
                    'more_details': product.details.more_details,
                    'specifications': product.details.specifications,
                    'ingredients': product.details.ingredients,
                    'caloric_content': product.details.caloric_content,
                    'guaranteed_analysis': product.details.guaranteed_analysis,
                    'feeding_instructions': product.details.feeding_instructions,
                    'transition_instructions': product.details.transition_instructions,
                }
            
            export_data['products'].append(product_data)
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"export_{timestamp}.json"
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(products)} products to: {output_file}")
        print(f"📁 File size: {len(json.dumps(export_data)) / 1024:.2f} KB")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def main():
    """Main entry point"""
    export_scraped_only = True
    output_file = None
    
    if '--all' in sys.argv:
        export_scraped_only = False
    
    if '--output' in sys.argv or '-o' in sys.argv:
        idx = sys.argv.index('--output') if '--output' in sys.argv else sys.argv.index('-o')
        try:
            output_file = sys.argv[idx + 1]
        except IndexError:
            print("Error: --output requires a filename argument")
            sys.exit(1)
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\nOptions:")
        print("  --scraped-only      Export only scraped products (default)")
        print("  --all                Export all products")
        print("  --output FILE, -o FILE  Output filename (default: export_YYYYMMDD_HHMMSS.json)")
        sys.exit(0)
    
    export_products(export_scraped_only, output_file)

if __name__ == "__main__":
    main()

