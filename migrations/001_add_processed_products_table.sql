-- Migration: Add processed_products table
-- Description: Creates a comprehensive table for storing processed and analyzed dog food product data
-- Author: System
-- Date: 2025-12-10

-- ============================================================================
-- Create ENUM Types
-- ============================================================================

CREATE TYPE foodcategoryenum AS ENUM (
    'Raw',
    'Fresh',
    'Dry',
    'Wet',
    'Soft',
    'Other'
);

CREATE TYPE sourcingintegrityenum AS ENUM (
    'Human Grade (organic)',
    'Human Grade',
    'Feed Grade',
    'Other'
);

CREATE TYPE processingmethodenum AS ENUM (
    'Uncooked (Not Frozen)',
    'Uncooked (Flash Frozen)',
    'Uncooked (Frozen)',
    'Lightly Cooked (Not Frozen)',
    'Lightly Cooked + Frozen',
    'Freeze Dried',
    'Air Dried',
    'Dehydrated',
    'Baked',
    'Extruded',
    'Retorted',
    'Other'
);

CREATE TYPE nutritionallyadequateenum AS ENUM (
    'Yes',
    'No'
);

CREATE TYPE qualityclassenum AS ENUM (
    'High',
    'Good',
    'Moderate',
    'Low'
);

CREATE TYPE foodstorageenum AS ENUM (
    'Freezer',
    'Refrigerator',
    'Cool Dry Space (Away from moisture)',
    'Cool Dry Space (Not away from moisture)'
);

CREATE TYPE packagingsizeenum AS ENUM (
    'a month',
    '2 month',
    '3+ month'
);

CREATE TYPE shelflifeenum AS ENUM (
    '7Day',
    '8-14 Day',
    '15+Day',
    'Other'
);

-- ============================================================================
-- Create processed_products Table
-- ============================================================================

CREATE TABLE processed_products (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Foreign Key to product_details
    product_detail_id INTEGER NOT NULL UNIQUE,

    -- Basic Information
    flavor TEXT,

    -- Food Category
    food_category foodcategoryenum,
    category_reason TEXT,

    -- Sourcing Integrity
    sourcing_integrity sourcingintegrityenum,
    sourcing_integrity_reason TEXT,

    -- Processing Methods
    processing_method_1 processingmethodenum,
    processing_method_2 processingmethodenum,
    processing_adulteration_method processingmethodenum,
    processing_adulteration_method_reason TEXT,

    -- Guaranteed Analysis (using NUMERIC for precise decimal values)
    guaranteed_analysis_crude_protein_pct NUMERIC(5, 2),
    guaranteed_analysis_crude_fat_pct NUMERIC(5, 2),
    guaranteed_analysis_crude_fiber_pct NUMERIC(5, 2),
    guaranteed_analysis_crude_moisture_pct NUMERIC(5, 2),
    guaranteed_analysis_crude_ash_pct NUMERIC(5, 2),
    starchy_carb_pct NUMERIC(5, 2),

    -- Nutritional Adequacy
    nutritionally_adequate nutritionallyadequateenum,
    nutritionally_adequate_reason TEXT,

    -- Ingredients - All
    ingredients_all TEXT,

    -- Protein Ingredients
    protein_ingredients_all TEXT,
    protein_ingredients_high INTEGER,
    protein_ingredients_good INTEGER,
    protein_ingredients_moderate INTEGER,
    protein_ingredients_low INTEGER,
    protein_quality_class qualityclassenum,

    -- Fat Ingredients
    fat_ingredients_all TEXT,
    fat_ingredients_high INTEGER,
    fat_ingredients_good INTEGER,
    fat_ingredients_low INTEGER,
    fat_quality_class qualityclassenum,

    -- Carb Ingredients
    carb_ingredients_all TEXT,
    carb_ingredients_high INTEGER,
    carb_ingredients_good INTEGER,
    carb_ingredients_moderate INTEGER,
    carb_ingredients_low INTEGER,
    carb_quality_class qualityclassenum,

    -- Fiber Ingredients
    fiber_ingredients_all TEXT,
    fiber_ingredients_high INTEGER,
    fiber_ingredients_good INTEGER,
    fiber_ingredients_moderate INTEGER,
    fiber_ingredients_low INTEGER,
    fiber_quality_class qualityclassenum,

    -- Dirty Dozen and Additives
    dirty_dozen_ingredients TEXT,
    dirty_dozen_ingredients_count INTEGER,
    synthetic_nutrition_addition TEXT,
    synthetic_nutrition_addition_count INTEGER,
    longevity_additives TEXT,
    longevity_additives_count INTEGER,

    -- Storage and Shelf Life
    food_storage foodstorageenum,
    food_storage_reason TEXT,
    packaging_size packagingsizeenum,
    shelf_life_thawed shelflifeenum,

    -- Metadata
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processor_version VARCHAR(50),

    -- Foreign Key Constraint
    CONSTRAINT fk_product_detail
        FOREIGN KEY (product_detail_id)
        REFERENCES product_details(id)
        ON DELETE CASCADE
);

-- ============================================================================
-- Create Indexes
-- ============================================================================

-- Index on foreign key for faster joins
CREATE INDEX idx_processed_products_product_detail_id
    ON processed_products(product_detail_id);

-- Index on food category for filtering
CREATE INDEX idx_processed_products_food_category
    ON processed_products(food_category);

-- Index on quality classes for filtering by quality
CREATE INDEX idx_processed_products_protein_quality
    ON processed_products(protein_quality_class);

CREATE INDEX idx_processed_products_fat_quality
    ON processed_products(fat_quality_class);

CREATE INDEX idx_processed_products_carb_quality
    ON processed_products(carb_quality_class);

-- Index on processed_at for temporal queries
CREATE INDEX idx_processed_products_processed_at
    ON processed_products(processed_at);

-- ============================================================================
-- Comments (Documentation)
-- ============================================================================

COMMENT ON TABLE processed_products IS
    'Stores processed and analyzed dog food product data with comprehensive quality assessments';

COMMENT ON COLUMN processed_products.product_detail_id IS
    'Foreign key reference to product_details table';

COMMENT ON COLUMN processed_products.flavor IS
    'Comma-separated list of flavors (e.g., "Chicken, Beef")';

COMMENT ON COLUMN processed_products.processing_method_1 IS
    'Primary processing method used';

COMMENT ON COLUMN processed_products.processing_method_2 IS
    'Secondary processing method used (if applicable)';

COMMENT ON COLUMN processed_products.processing_adulteration_method IS
    'Assessment of processing/adulteration methods';

COMMENT ON COLUMN processed_products.starchy_carb_pct IS
    'Calculated starchy carbohydrate percentage';

COMMENT ON COLUMN processed_products.dirty_dozen_ingredients IS
    'List of ingredients from the "dirty dozen" list';

COMMENT ON COLUMN processed_products.synthetic_nutrition_addition IS
    'List of synthetic nutritional additives';

COMMENT ON COLUMN processed_products.longevity_additives IS
    'List of longevity-promoting additives';

COMMENT ON COLUMN processed_products.processed_at IS
    'Timestamp when this record was created/processed';

COMMENT ON COLUMN processed_products.processor_version IS
    'Version of the processing logic used (e.g., "v1.2.3")';

-- ============================================================================
-- Rollback Script (commented out, uncomment to rollback)
-- ============================================================================

/*
-- Drop indexes
DROP INDEX IF EXISTS idx_processed_products_processed_at;
DROP INDEX IF EXISTS idx_processed_products_carb_quality;
DROP INDEX IF EXISTS idx_processed_products_fat_quality;
DROP INDEX IF EXISTS idx_processed_products_protein_quality;
DROP INDEX IF EXISTS idx_processed_products_food_category;
DROP INDEX IF EXISTS idx_processed_products_product_detail_id;

-- Drop table
DROP TABLE IF EXISTS processed_products;

-- Drop ENUM types
DROP TYPE IF EXISTS shelflifeenum;
DROP TYPE IF EXISTS packagingsizeenum;
DROP TYPE IF EXISTS foodstorageenum;
DROP TYPE IF EXISTS qualityclassenum;
DROP TYPE IF EXISTS nutritionallyadequateenum;
DROP TYPE IF EXISTS processingmethodenum;
DROP TYPE IF EXISTS sourcingintegrityenum;
DROP TYPE IF EXISTS foodcategoryenum;
*/
