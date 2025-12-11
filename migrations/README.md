# Database Migrations

This directory contains SQL migration scripts for the Dog Food Scoring API database.

## Overview

Migrations are database schema changes that are version-controlled and can be applied systematically to keep your database schema in sync with your application models.

## Available Migrations

### 001_add_processed_products_table.sql
Creates the `processed_products` table with comprehensive dog food assessment fields including:
- Food category and sourcing integrity
- Processing methods (3 fields for detailed tracking)
- Guaranteed analysis (protein, fat, fiber, moisture, ash, carbs)
- Ingredient quality breakdowns (protein, fat, carb, fiber)
- Quality classifications
- Additive tracking (dirty dozen, synthetic nutrition, longevity additives)
- Storage and shelf life information
- Processing metadata (timestamp, version)

## Migration Methods

You have two options to apply migrations:

### Option 1: Using Alembic (Recommended)

Alembic provides version control and automated migration management.

```bash
# Navigate to the api directory
cd api

# Activate virtual environment
source .venv/bin/activate

# Check current migration status
alembic current

# Upgrade to the latest migration
alembic upgrade head

# Downgrade one migration
alembic downgrade -1

# View migration history
alembic history
```

**Configuration:**
- Alembic config: `api/alembic.ini`
- Migration scripts: `api/alembic/versions/`
- Environment setup: `api/alembic/env.py`

Update the database URL in `alembic.ini` if needed:
```ini
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/dogfood_db
```

### Option 2: Direct SQL Execution

For manual control or if Alembic is not available:

```bash
# Using psql
psql -U postgres -d dogfood_db -f migrations/001_add_processed_products_table.sql

# Using psql with connection string
psql postgresql://postgres:postgres@localhost:5432/dogfood_db -f migrations/001_add_processed_products_table.sql
```

Or from within a PostgreSQL session:
```sql
\i migrations/001_add_processed_products_table.sql
```

## Rollback

### Using Alembic
```bash
alembic downgrade -1
```

### Using SQL
Uncomment the rollback section at the bottom of the SQL file and execute it:
```sql
-- Uncomment and run the rollback section in the migration file
```

## Verifying the Migration

After applying the migration, verify the table was created:

```sql
-- Check if table exists
SELECT * FROM information_schema.tables 
WHERE table_name = 'processed_products';

-- View table structure
\d processed_products

-- Check enum types
\dT

-- Verify foreign key constraint
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'processed_products';
```

## Database Schema

After this migration, your database will have the following structure:

```
products_list (existing)
├── id (PK)
├── product_url
├── page_num
├── scraped
├── skipped
└── product_image_url

product_details (existing)
├── id (PK)
├── product_id (FK -> products_list.id)
├── product_category
├── product_name
├── ingredients
├── guaranteed_analysis
└── ... (other fields)

processed_products (NEW)
├── id (PK)
├── product_detail_id (FK -> product_details.id)
├── flavor
├── food_category (ENUM)
├── sourcing_integrity (ENUM)
├── processing_method_1 (ENUM)
├── processing_method_2 (ENUM)
├── processing_adulteration_method (ENUM)
├── guaranteed_analysis_* (NUMERIC fields)
├── protein_* (quality metrics)
├── fat_* (quality metrics)
├── carb_* (quality metrics)
├── fiber_* (quality metrics)
├── dirty_dozen_ingredients
├── synthetic_nutrition_addition
├── longevity_additives
├── food_storage (ENUM)
├── packaging_size (ENUM)
├── shelf_life_thawed (ENUM)
├── processed_at (TIMESTAMP)
└── processor_version (VARCHAR)
```

## Workflow Integration

The `processed_products` table fits into your data pipeline:

1. **Scraping** → Populates `products_list` and `product_details`
2. **Processing** → Reads from `product_details`, analyzes, writes to `processed_products`
3. **Scoring** → Reads from `processed_products`, calculates scores
4. **API** → Serves data from all tables

## Development Guidelines

### Creating New Migrations

When you need to modify the schema:

1. **Using Alembic:**
   ```bash
   alembic revision -m "description_of_change"
   # Edit the generated file in alembic/versions/
   alembic upgrade head
   ```

2. **Using SQL:**
   - Create a new file: `00X_description.sql`
   - Follow the existing format
   - Include rollback script
   - Test on a development database first

### Migration Best Practices

- ✅ **Always backup** your database before running migrations
- ✅ **Test migrations** on a development database first
- ✅ **Include rollback** scripts for all migrations
- ✅ **Document** what each migration does
- ✅ **Version control** all migration files
- ✅ **Keep migrations small** and focused on one change
- ✅ **Don't modify** existing migration files after they've been applied
- ❌ **Never** delete migration files that have been applied to production

## Troubleshooting

### "relation already exists" error
The table might already exist. Check with:
```sql
\dt processed_products
```

### "type already exists" error
The enum types might already exist. Check with:
```sql
\dT
```

To force recreation:
```sql
DROP TABLE IF EXISTS processed_products CASCADE;
DROP TYPE IF EXISTS foodcategoryenum CASCADE;
-- ... (drop all enum types)
```

### Foreign key constraint fails
Ensure `product_details` table exists:
```sql
SELECT * FROM information_schema.tables WHERE table_name = 'product_details';
```

### Connection issues
Verify your database connection string in `alembic.ini` or your connection command.

## Support

For issues or questions about migrations:
1. Check the Alembic documentation: https://alembic.sqlalchemy.org/
2. Review the SQLAlchemy models in `api/app/models/product.py`
3. Consult the project's main README