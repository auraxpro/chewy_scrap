# Brand Detection Guide

This guide explains how to use the brand detection system to automatically detect brand names from product information.

## Overview

The brand detection system uses a multi-step approach to detect brand names from product data:

1. **Primary Method**: Extract brand from product name using starts-with and contains matching (~85% accuracy)
2. **Fallback Method**: Search in details, specifications, and ingredients (~+8% accuracy)
3. **Fuzzy Matching**: Use fuzzy matching for edge cases (~+2% accuracy)

**Total Expected Accuracy: ~97%**

## How Brand Detection Works

### 1. Product Name Matching (Primary)

Chewy almost always includes the brand at the start of the product title. Examples:

- `"Blue Buffalo Life Protection Formula Chicken & Rice Recipe..."`
- `"Hill's Science Diet Adult 7+ Chicken Meal..."`
- `"Taste of the Wild Sierra Mountain Grain-Free..."`
- `"Purina ONE SmartBlend Chicken..."`
- `"Merrick Backcountry Raw Infused..."`

The system:
- Matches brands using longest prefix first (e.g., "Purina Pro Plan" before "Purina")
- Uses case-insensitive matching
- Prefers starts-with matches over contains matches

### 2. Fallback Fields

If no brand is found in the product name, the system searches:
- `details`
- `specifications`
- `ingredients`
- `more_details`

### 3. Fuzzy Matching

For edge cases (misspellings, abbreviations), fuzzy matching is used with a similarity threshold of 0.45.

## Providing Brand Information

### Option 1: Edit `brands.py` File (Recommended)

Edit `/app/processors/brands.py` and add brands to the `BRANDS` list:

```python
BRANDS = [
    "By Chewy",
    "+PlusPET",
    "1-TDC",
    # Add your brands here...
    "Blue Buffalo",
    "Hill's Science Diet",
    "Taste of the Wild",
    # ... more brands
]
```

**Important**: Order matters! Put longer/more specific brands first:
- ✅ `"Purina Pro Plan"` before `"Purina"`
- ✅ `"Hill's Science Diet"` before `"Hill's"`

### Option 2: Pass Custom Brand List

You can pass a custom brand list when initializing the processor:

```python
from app.processors.brand_processor import BrandProcessor

custom_brands = ["Brand A", "Brand B", "Brand C"]
processor = BrandProcessor(db, brands=custom_brands)
```

### Option 3: Extract Brands from Database

You can extract unique brands from your product names:

```python
from app.models.database import SessionLocal
from app.models import ProductDetails
from sqlalchemy import func

db = SessionLocal()
# Get unique product names and extract potential brands
# (This would require custom logic to identify brand patterns)
```

## Usage

### Basic Usage

```python
from app.models.database import SessionLocal
from app.processors.brand_processor import BrandProcessor

db = SessionLocal()
processor = BrandProcessor(db)

# Process a single product
processor.process_single(product_detail_id=123)

# Process all products
results = processor.process_all()

# Process with options
results = processor.process_all(limit=100, skip_existing=True)
```

### Command Line Script

```bash
# Process all unprocessed products
python scripts/process_brands.py

# Process all products (including already processed)
python scripts/process_brands.py --reprocess

# Process with limit
python scripts/process_brands.py --limit 100

# Show statistics only
python scripts/process_brands.py --stats-only

# Test mode (no database changes)
python scripts/process_brands.py --test
```

### Integration with Main Processing Pipeline

The brand processor can be integrated into your main processing pipeline:

```python
from app.processors.brand_processor import BrandProcessor

# In your processing pipeline
processors = [
    ("Category", FoodCategoryProcessor(db, "v1.0.0")),
    ("Brand", BrandProcessor(db, "v1.0.0")),  # Add brand processor
    ("Sourcing", SourcingIntegrityProcessor(db, "v1.0.0")),
    # ... other processors
]
```

## Database Schema

The brand detection adds the following fields to `processed_products`:

- `brand` (VARCHAR): Detected brand name
- `brand_detection_method` (VARCHAR): Method used ("starts_with", "contains", "fallback", "fuzzy", "none")
- `brand_detection_confidence` (VARCHAR): Confidence level ("high", "medium", "low", "none")
- `brand_detection_reason` (TEXT): Human-readable reason for the detection

## Migration

Run the Alembic migration to add brand fields:

```bash
alembic upgrade head
```

Or manually:

```bash
python -m alembic upgrade head
```

## Statistics

View brand detection statistics:

```python
processor = BrandProcessor(db)
stats = processor.get_statistics()
processor.print_statistics()
```

Output includes:
- Top brands (by count)
- Detection methods breakdown
- Confidence levels
- Processing progress

## Testing

Test brand detection without database changes:

```bash
python scripts/process_brands.py --test
```

This will test the classifier with sample product names and show detection results.

## Troubleshooting

### Brand Not Detected

1. **Check if brand is in the list**: Verify the brand exists in `brands.py`
2. **Check product name**: Ensure the product name contains the brand
3. **Check order**: Make sure longer brand names come before shorter ones
4. **Check spelling**: Verify exact spelling matches (case-insensitive)

### False Positives

1. **Review brand list**: Remove or reorder brands that cause conflicts
2. **Check detection method**: Review `brand_detection_method` to understand how it was detected
3. **Adjust fuzzy threshold**: Modify `threshold` in `detect_brand_fuzzy()` if needed

### Performance

- Brand detection is fast (O(n) where n = number of brands)
- Normalized brand list is pre-computed for fast matching
- Fuzzy matching is only used as a last resort

## Best Practices

1. **Keep brand list updated**: Add new brands as you discover them
2. **Order matters**: Put specific brands before generic ones
3. **Review statistics**: Regularly check detection statistics for accuracy
4. **Test before bulk processing**: Use `--test` mode to verify detection logic
5. **Monitor confidence levels**: Review low-confidence detections manually

## Example Workflow

```python
# 1. Update brand list
# Edit app/processors/brands.py

# 2. Run migration (if not already done)
# alembic upgrade head

# 3. Test detection
python scripts/process_brands.py --test

# 4. Process products
python scripts/process_brands.py --limit 100

# 5. Review statistics
python scripts/process_brands.py --stats-only

# 6. Process all products
python scripts/process_brands.py
```

## API Usage

The brand processor follows the same pattern as other processors:

```python
from app.processors.brand_processor import process_brands

# Process all
results = process_brands(db)

# Process specific IDs
results = process_brands(db, product_detail_ids=[1, 2, 3])

# Process with limit
results = process_brands(db, limit=100, skip_existing=True)
```

