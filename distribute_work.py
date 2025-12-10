#!/usr/bin/env python3
"""
Work Distribution Script

This script helps distribute scraping work across multiple computers
by assigning ID ranges or offsets to each computer.

Usage:
    python distribute_work.py --computers 3 --chunk-size 1200
    python distribute_work.py --computers 3 --chunk-size 1200 --show-assignments
"""

import sys
from database import SessionLocal, ProductList
from sqlalchemy import func

def get_unscraped_count():
    """Get total count of unscraped products"""
    db = SessionLocal()
    try:
        count = db.query(func.count(ProductList.id)).filter_by(scraped=False).scalar()
        return count
    finally:
        db.close()

def get_unscraped_id_range():
    """Get min and max IDs of unscraped products"""
    db = SessionLocal()
    try:
        result = db.query(
            func.min(ProductList.id).label('min_id'),
            func.max(ProductList.id).label('max_id')
        ).filter_by(scraped=False).first()
        return result.min_id, result.max_id
    finally:
        db.close()

def distribute_work(num_computers: int, chunk_size: int = None):
    """Distribute work across multiple computers"""
    total_unscraped = get_unscraped_count()
    
    if total_unscraped == 0:
        print("✅ No unscraped products found!")
        return []
    
    print(f"📊 Total unscraped products: {total_unscraped}")
    
    if chunk_size:
        # Use fixed chunk size
        assignments = []
        offset = 0
        for i in range(num_computers):
            assignments.append({
                'computer': i + 1,
                'offset': offset,
                'limit': chunk_size,
                'estimated_count': min(chunk_size, total_unscraped - offset)
            })
            offset += chunk_size
            if offset >= total_unscraped:
                break
    else:
        # Distribute evenly
        chunk_size = (total_unscraped + num_computers - 1) // num_computers
        assignments = []
        offset = 0
        for i in range(num_computers):
            remaining = total_unscraped - offset
            limit = min(chunk_size, remaining)
            if limit <= 0:
                break
            assignments.append({
                'computer': i + 1,
                'offset': offset,
                'limit': limit,
                'estimated_count': limit
            })
            offset += limit
    
    return assignments

def main():
    """Main entry point"""
    num_computers = 3
    chunk_size = None
    show_assignments = False
    
    # Parse arguments
    if '--computers' in sys.argv:
        idx = sys.argv.index('--computers')
        try:
            num_computers = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            print("Error: --computers requires an integer argument")
            sys.exit(1)
    
    if '--chunk-size' in sys.argv:
        idx = sys.argv.index('--chunk-size')
        try:
            chunk_size = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            print("Error: --chunk-size requires an integer argument")
            sys.exit(1)
    
    if '--show-assignments' in sys.argv or '-s' in sys.argv:
        show_assignments = True
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        print("\nOptions:")
        print("  --computers N        Number of computers (default: 3)")
        print("  --chunk-size N      Fixed chunk size per computer (default: auto-distribute)")
        print("  --show-assignments   Show detailed assignments")
        sys.exit(0)
    
    # Distribute work
    assignments = distribute_work(num_computers, chunk_size)
    
    if not assignments:
        print("No work to distribute!")
        return
    
    print(f"\n📋 Work Distribution ({len(assignments)} computers):")
    print("=" * 70)
    
    for assignment in assignments:
        print(f"\n🖥️  Computer {assignment['computer']}:")
        print(f"   Offset: {assignment['offset']}")
        print(f"   Limit: {assignment['limit']}")
        print(f"   Estimated products: {assignment['estimated_count']}")
        print(f"   Command: python main.py --details --offset {assignment['offset']} --limit {assignment['limit']}")
    
    print("\n" + "=" * 70)
    print("\n💡 To run on each computer:")
    print("   1. Copy the command for that computer")
    print("   2. Run it on that computer")
    print("   3. After scraping, export data using: python export_data.py")
    print("   4. Import into master database using: python import_data.py <export_file.json>")

if __name__ == "__main__":
    main()

