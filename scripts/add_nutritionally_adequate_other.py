#!/usr/bin/env python3
"""
Script to add 'Other' value to nutritionallyadequateenum.

This script adds the 'Other' value to the PostgreSQL enum type.
Run this before using the nutritionally adequate processor.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import engine
from sqlalchemy import text


def add_other_enum_value():
    """Add 'Other' to nutritionallyadequateenum."""
    try:
        with engine.connect() as conn:
            # Use the DO block approach that works in transactions
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_enum 
                        WHERE enumlabel = 'Other' 
                        AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'nutritionallyadequateenum')
                    ) THEN
                        ALTER TYPE nutritionallyadequateenum ADD VALUE 'Other';
                    END IF;
                EXCEPTION
                    WHEN duplicate_object THEN
                        NULL;
                END $$;
            """))
            conn.commit()
            print("✅ Successfully added 'Other' to nutritionallyadequateenum")
            
            # Verify it was added
            result = conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'nutritionallyadequateenum')
                ORDER BY enumsortorder;
            """))
            values = [row[0] for row in result]
            print(f"✅ Current enum values: {', '.join(values)}")
            
    except Exception as e:
        print(f"❌ Error adding enum value: {e}")
        print("\n💡 Alternative: Run the SQL manually:")
        print("   psql -U chewy_user -d chewy_db -f add_nutritionally_adequate_other_enum.sql")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 70)
    print("Adding 'Other' to nutritionallyadequateenum")
    print("=" * 70)
    add_other_enum_value()
    print("=" * 70)
