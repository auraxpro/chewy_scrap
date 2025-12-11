# Processed Products Table - Quick Start Guide

## TL;DR

You now have a `processed_products` table to store analyzed dog food data. Raw scrapes stay in `product_details`, processed analysis goes here.

## Quick Setup

### 1. Apply the Migration

**Option A - Alembic (Recommended):**
```bash
cd api
source .venv/bin/activate
alembic upgrade head
```

**Option B - Direct SQL:**
```bash
psql -U postgres -d dogfood_db -f migrations/001_add_processed_products_table.sql
```

### 2. Verify It Works

```bash
psql -U postgres -d dogfood_db
```

```sql
-- Check the table exists
\d processed_products

-- Should show 60+ columns including:
-- id, product_detail_id, flavor, food_category, etc.
```

## Basic Usage

### Import the Model

```python
from app.models import ProcessedProduct, ProductDetails
from app.schemas import ProcessedProductCreate
```

### Create a Processed Record

```python
from sqlalchemy.orm import Session

def process_product(detail_id: int, db: Session):
    # Get raw data
    detail = db.query(ProductDetails).get(detail_id)
    
    # Create processed record
    processed = ProcessedProduct(
        product_detail_id=detail.id,
        flavor="Chicken, Beef",
        food_category="Dry",
        guaranteed_analysis_crude_protein_pct=28.0,
        guaranteed_analysis_crude_fat_pct=15.0,
        protein_quality_class="High",
        processor_version="v1.0.0"
    )
    
    db.add(processed)
    db.commit()
    return processed
```

### Query Processed Products

```python
# Get all high-protein foods
high_protein = db.query(ProcessedProduct).filter(
    ProcessedProduct.guaranteed_analysis_crude_protein_pct >= 30.0
).all()

# Get by food category
dry_foods = db.query(ProcessedProduct).filter(
    ProcessedProduct.food_category == "Dry"
).all()

# Join with product details
from sqlalchemy.orm import joinedload

result = db.query(ProcessedProduct).options(
    joinedload(ProcessedProduct.product_detail)
).first()

print(result.product_detail.product_name)
print(result.guaranteed_analysis_crude_protein_pct)
```

## Key Fields You'll Use Most

### Essential Fields
- `product_detail_id` - Links to raw data (REQUIRED)
- `flavor` - e.g., "Chicken, Beef, Lamb"
- `food_category` - Dry, Wet, Raw, Fresh, Soft, Other
- `processor_version` - Track your processing logic version

### Nutrition (Guaranteed Analysis)
- `guaranteed_analysis_crude_protein_pct`
- `guaranteed_analysis_crude_fat_pct`
- `guaranteed_analysis_crude_fiber_pct`
- `guaranteed_analysis_crude_moisture_pct`
- `guaranteed_analysis_crude_ash_pct`
- `starchy_carb_pct` - Calculate this yourself

### Quality Metrics
Each has `_all` (text list) and `_high/_good/_moderate/_low` (counts):
- Protein ingredients
- Fat ingredients
- Carb ingredients
- Fiber ingredients

Each also has a `_quality_class` (High, Good, Moderate, Low).

### Flags & Counts
- `dirty_dozen_ingredients` + `dirty_dozen_ingredients_count`
- `synthetic_nutrition_addition` + `synthetic_nutrition_addition_count`
- `longevity_additives` + `longevity_additives_count`

## Data Flow

```
1. SCRAPE
   Chewy.com → products_list → product_details
   
2. PROCESS (you build this)
   product_details → YOUR CODE → processed_products
   
3. SCORE (future)
   processed_products → scoring logic → scores
```

## Enum Values Reference

### FoodCategoryEnum
- `Raw`, `Fresh`, `Dry`, `Wet`, `Soft`, `Other`

### SourcingIntegrityEnum
- `Human Grade (organic)`
- `Human Grade`
- `Feed Grade`
- `Other`

### ProcessingMethodEnum
- `Uncooked (Not Frozen)`
- `Uncooked (Flash Frozen)`
- `Uncooked (Frozen)`
- `Lightly Cooked (Not Frozen)`
- `Lightly Cooked + Frozen`
- `Freeze Dried`
- `Air Dried`
- `Dehydrated`
- `Baked`
- `Extruded`
- `Retorted`
- `Other`

### QualityClassEnum
- `High`, `Good`, `Moderate`, `Low`

### NutritionallyAdequateEnum
- `Yes`, `No`

### FoodStorageEnum
- `Freezer`
- `Refrigerator`
- `Cool Dry Space (Away from moisture)`
- `Cool Dry Space (Not away from moisture)`

### PackagingSizeEnum
- `a month`, `2 month`, `3+ month`

### ShelfLifeEnum
- `7Day`, `8-14 Day`, `15+Day`, `Other`

## Example: Complete Processing Function

```python
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import ProcessedProduct, ProductDetails

PROCESSOR_VERSION = "v1.0.0"

def process_single_product(detail_id: int, db: Session) -> ProcessedProduct:
    """
    Process a single product detail record.
    Returns ProcessedProduct instance.
    """
    # Get raw data
    detail = db.query(ProductDetails).get(detail_id)
    if not detail:
        raise ValueError(f"ProductDetails {detail_id} not found")
    
    # Check if already processed
    existing = db.query(ProcessedProduct).filter_by(
        product_detail_id=detail_id
    ).first()
    
    if existing:
        processed = existing
        print(f"Updating existing processed record {existing.id}")
    else:
        processed = ProcessedProduct(product_detail_id=detail_id)
        print(f"Creating new processed record for detail {detail_id}")
    
    # TODO: Implement your analysis logic
    # For now, just extract basic info
    
    # Extract flavor from product name (simple example)
    name_lower = (detail.product_name or "").lower()
    flavors = []
    if "chicken" in name_lower:
        flavors.append("Chicken")
    if "beef" in name_lower:
        flavors.append("Beef")
    if "salmon" in name_lower:
        flavors.append("Salmon")
    if "lamb" in name_lower:
        flavors.append("Lamb")
    
    processed.flavor = ", ".join(flavors) if flavors else None
    
    # Classify food category (simple heuristic)
    category_lower = (detail.product_category or "").lower()
    if "dry" in category_lower or "kibble" in category_lower:
        processed.food_category = "Dry"
        processed.category_reason = "Contains 'dry' or 'kibble' in category"
    elif "wet" in category_lower or "canned" in category_lower:
        processed.food_category = "Wet"
        processed.category_reason = "Contains 'wet' or 'canned' in category"
    elif "raw" in category_lower:
        processed.food_category = "Raw"
        processed.category_reason = "Contains 'raw' in category"
    else:
        processed.food_category = "Other"
        processed.category_reason = "Could not determine from category"
    
    # TODO: Parse guaranteed analysis from detail.guaranteed_analysis
    # TODO: Analyze ingredients from detail.ingredients
    # TODO: Assess quality metrics
    # TODO: Identify dirty dozen ingredients
    # TODO: Classify processing methods
    
    # Set metadata
    processed.processed_at = datetime.utcnow()
    processed.processor_version = PROCESSOR_VERSION
    
    db.add(processed)
    db.commit()
    db.refresh(processed)
    
    return processed


def batch_process_all(db: Session, batch_size: int = 50):
    """
    Process all unprocessed product details.
    """
    # Find product_details without processed_products
    unprocessed = db.query(ProductDetails).outerjoin(
        ProcessedProduct,
        ProductDetails.id == ProcessedProduct.product_detail_id
    ).filter(
        ProcessedProduct.id.is_(None)
    ).limit(batch_size).all()
    
    print(f"Found {len(unprocessed)} unprocessed products")
    
    results = []
    for detail in unprocessed:
        try:
            processed = process_single_product(detail.id, db)
            results.append(processed)
            print(f"✓ Processed detail {detail.id} → processed {processed.id}")
        except Exception as e:
            print(f"✗ Error processing detail {detail.id}: {e}")
    
    return results
```

## CLI Integration Example

Add to your `scripts/main.py`:

```python
@click.command()
@click.option("--all", is_flag=True, help="Process all unprocessed products")
@click.option("--detail-id", type=int, help="Process specific product detail ID")
@click.option("--batch-size", type=int, default=50, help="Batch size for processing")
def process(all, detail_id, batch_size):
    """Process product details into processed_products."""
    from app.models.database import SessionLocal
    from your_module import process_single_product, batch_process_all
    
    db = SessionLocal()
    try:
        if detail_id:
            result = process_single_product(detail_id, db)
            click.echo(f"Processed detail {detail_id} → {result.id}")
        elif all:
            results = batch_process_all(db, batch_size)
            click.echo(f"Processed {len(results)} products")
        else:
            click.echo("Specify --all or --detail-id")
    finally:
        db.close()
```

## Tips

1. **All fields are nullable** - Populate incrementally as you develop
2. **Use reason fields** - Document why you made each classification
3. **Track versions** - Update `processor_version` when logic changes
4. **Don't delete raw data** - Keep `product_details` intact for reprocessing
5. **Batch processing** - Process in chunks for large datasets

## Troubleshooting

### "No module named 'app'"
```bash
cd api
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### "Enum value not recognized"
Use exact string values from the enum definitions above.

### "Foreign key constraint fails"
Ensure `product_detail_id` exists in `product_details` table.

### "Precision loss in percentages"
Use Python's `Decimal` type:
```python
from decimal import Decimal
processed.guaranteed_analysis_crude_protein_pct = Decimal("28.50")
```

## What's Next?

1. **Build your processors** - Implement ingredient analysis, quality classification, etc.
2. **Test with sample data** - Process a few products manually to validate
3. **Create API endpoints** - Expose processed data via REST API
4. **Develop scoring** - Use processed data to calculate food scores

## Related Documentation

- Full documentation: `api/docs/PROCESSED_PRODUCTS_TABLE.md`
- Migration guide: `api/migrations/README.md`
- Model code: `api/app/models/product.py`
- Schema code: `api/app/schemas/processed_product.py`

## Questions?

This table is ready to use. You can start populating it with your processing logic whenever you're ready. All fields are optional, so start simple and add complexity over time.