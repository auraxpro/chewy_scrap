# Starchy Carb Extraction Guide

## Overview

The **Starchy Carb Processor** extracts nutrition values from Chewy scraped product fields and calculates starchy carbohydrate percentage for dog food products. It uses regex pattern matching to extract guaranteed analysis values and applies different calculation formulas based on food type (Dry vs Wet/Raw).

**Feature Name:** Starchy Carb Process Feature

**Extracted Values:**
- `crude_protein_pct` - Crude protein percentage
- `crude_fat_pct` - Crude fat percentage
- `crude_fiber_pct` - Crude fiber percentage
- `crude_moisture_pct` - Moisture percentage
- `crude_ash_pct` - Crude ash percentage (defaults to 6.0% if missing)
- `starchy_carb_pct` - Calculated starchy carbohydrate percentage

---

## Key Features

### 1. Multi-Field Extraction
The processor searches for nutrition values in priority order:
1. **Primary:** `guaranteed_analysis` field
2. **Fallback 1:** `details` field
3. **Fallback 2:** `more_details` field
4. **Fallback 3:** `specifications` field
5. **Fallback 4:** `product_name` field (last resort)

### 2. Flexible Format Support
The regex patterns handle various formats commonly found in product data:

**Supported Formats:**
- `Crude Protein | 4.1%min`
- `Crude Protein | 37.0% (min)`
- `Crude Fat | 6.7% min`
- `Crude Fiber | 2.3% max`
- `Moisture | 74.5% max`
- `Protein: 28%`
- `28% protein`
- `Crude Protein (Min): 28.0 %`

### 3. Regex Patterns
Each nutrient uses case-insensitive patterns:

**Crude Protein:**
- `crude\s+protein.*?([0-9]+\.?[0-9]*)\s*%`
- `protein.*?([0-9]+\.?[0-9]*)\s*%`

**Crude Fat:**
- `crude\s+fat.*?([0-9]+\.?[0-9]*)\s*%`
- `fat.*?([0-9]+\.?[0-9]*)\s*%`

**Crude Fiber:**
- `crude\s+fiber.*?([0-9]+\.?[0-9]*)\s*%`
- `fiber.*?([0-9]+\.?[0-9]*)\s*%`

**Moisture:**
- `moisture.*?([0-9]+\.?[0-9]*)\s*%`

**Ash:**
- `crude\s+ash.*?([0-9]+\.?[0-9]*)\s*%`
- `ash.*?([0-9]+\.?[0-9]*)\s*%`

**Extraction Rules:**
- Uses the **first** valid numeric match found
- Strips commas and spaces from values
- Converts to float
- Returns `None` if no match found

### 4. Calculation Formulas

#### Dry Food Formula
For **Dry** food category:
```
starchy_carb_pct = 100 - (protein + fat + fiber + moisture + ash)
```

**Rules:**
- Moisture can be excluded if missing (assumes null)
- Ash defaults to 6.0% if missing
- Result cannot be negative (minimum 0.0)
- Rounded to 1 decimal place

**Example:**
- Protein: 28%, Fat: 15%, Fiber: 5%, Moisture: 10%, Ash: 7%
- Carbs = 100 - (28 + 15 + 5 + 10 + 7) = **35.0%**

#### Wet Food & Raw Food Conversion Formula
For **Wet**, **Raw**, or **Fresh** food categories:
```
Step 1: Wet Matter = 100 - (protein + fat + fiber + moisture + ash)
Step 2: Dry Matter = 100 - Moisture
Step 3: Carb % = (Wet Matter / Dry Matter) × 100
```

**Rules:**
- **Moisture is required** for Wet/Raw conversion (returns `None` if missing)
- Ash defaults to 6.0% if missing
- Result cannot be negative (minimum 0.0)
- Rounded to 1 decimal place

**Example:**
- Protein: 4.1%, Fat: 6.7%, Fiber: 2.3%, Moisture: 74.5%, Ash: 7%
- Wet Matter = 100 - (4.1 + 6.7 + 2.3 + 74.5 + 7) = 5.4%
- Dry Matter = 100 - 74.5 = 25.5%
- Carbs = (5.4 / 25.5) × 100 = **21.2%**

### 5. Category-Based Calculation
The processor automatically selects the appropriate formula based on `food_category`:

- **Dry** → Uses Dry Food Formula
- **Wet**, **Raw**, **Fresh** → Uses Wet/Raw Conversion Formula
- **Other**, **Soft**, or **Unknown** → Defaults to Dry Formula

**Fallback Logic:**
If `food_category` is not set:
- Moisture > 70% → Uses Wet/Raw Formula
- Otherwise → Uses Dry Formula

### 6. Default Values
- **Ash:** Defaults to **6.0%** if not found in text
- **Moisture:** Can be `None` for Dry food, but **required** for Wet/Raw food

---

## Database Schema

### Input Fields (from `product_details` table)
- `guaranteed_analysis` (TEXT) - Primary source
- `details` (TEXT) - Fallback 1
- `more_details` (TEXT) - Fallback 2
- `specifications` (TEXT) - Fallback 3
- `product_name` (TEXT) - Fallback 4
- `ingredients` (TEXT) - Used for validation only

### Output Fields (to `processed_products` table)
- `guaranteed_analysis_crude_protein_pct` (NUMERIC(5,2)) - Protein percentage
- `guaranteed_analysis_crude_fat_pct` (NUMERIC(5,2)) - Fat percentage
- `guaranteed_analysis_crude_fiber_pct` (NUMERIC(5,2)) - Fiber percentage
- `guaranteed_analysis_crude_moisture_pct` (NUMERIC(5,2)) - Moisture percentage
- `guaranteed_analysis_crude_ash_pct` (NUMERIC(5,2)) - Ash percentage
- `starchy_carb_pct` (NUMERIC(5,2)) - Calculated starchy carbs

### Workflow

1. **Processor reads** from `product_details` table (guaranteed_analysis + fallbacks)
2. **Extractor analyzes** text with regex patterns
3. **Calculator applies** appropriate formula based on food_category
4. **Processor writes** results to `processed_products` table
5. If record exists, it's updated; otherwise, a new record is created

---

## Command Line Interface (CLI)

### Using the Unified CLI

```bash
# Process all unprocessed products
python cli.py --process --starchy-carb

# Process with limit
python cli.py --process --starchy-carb --limit 100

# Process single product
python cli.py --process --starchy-carb --product-id 123

# Reprocess all products (force)
python cli.py --process --starchy-carb --force

# Show help
python cli.py --help
```

### Using the Standalone Script

```bash
# Process all unprocessed products
python scripts/process_starchy_carb.py --all

# Process with limit
python scripts/process_starchy_carb.py --all --limit 100

# Process single product
python scripts/process_starchy_carb.py --single 123

# Reprocess all products
python scripts/process_starchy_carb.py --all --reprocess

# Show statistics
python scripts/process_starchy_carb.py --stats
```

---

## Examples

### Example 1: Dry Food Extraction

**Input Data:**
```
guaranteed_analysis: "Crude Protein | 37.0% (min)
Crude Fat | 15.0% (min)
Crude Fiber | 5.0% (max)
Moisture | 10.0% (min)"
```

**Extracted Values:**
- Protein: 37.0%
- Fat: 15.0%
- Fiber: 5.0%
- Moisture: 10.0%
- Ash: 6.0% (default)

**Calculation (Dry Food):**
- Carbs = 100 - (37.0 + 15.0 + 5.0 + 10.0 + 6.0) = **27.0%**

### Example 2: Wet Food Extraction

**Input Data:**
```
guaranteed_analysis: "Crude Protein | 4.1%min
Crude Fat | 6.7% min
Crude Fiber | 2.3% max
Moisture | 74.5% max"
```

**Extracted Values:**
- Protein: 4.1%
- Fat: 6.7%
- Fiber: 2.3%
- Moisture: 74.5%
- Ash: 6.0% (default)

**Calculation (Wet Food):**
- Wet Matter = 100 - (4.1 + 6.7 + 2.3 + 74.5 + 6.0) = 6.4%
- Dry Matter = 100 - 74.5 = 25.5%
- Carbs = (6.4 / 25.5) × 100 = **25.1%**

### Example 3: Missing Moisture (Dry Food)

**Input Data:**
```
guaranteed_analysis: "Crude Protein | 28%
Crude Fat | 15%
Crude Fiber | 5%"
```

**Extracted Values:**
- Protein: 28.0%
- Fat: 15.0%
- Fiber: 5.0%
- Moisture: None
- Ash: 6.0% (default)

**Calculation (Dry Food - moisture excluded):**
- Carbs = 100 - (28.0 + 15.0 + 5.0 + 6.0) = **46.0%**

### Example 4: Missing Moisture (Wet Food)

**Input Data:**
```
guaranteed_analysis: "Crude Protein | 4.1%
Crude Fat | 6.7%
Crude Fiber | 2.3%"
food_category: "Wet"
```

**Extracted Values:**
- Protein: 4.1%
- Fat: 6.7%
- Fiber: 2.3%
- Moisture: None
- Ash: 6.0% (default)

**Result:** `None` (moisture required for Wet/Raw conversion)

---

## Python API Usage

### Basic Usage

```python
from app.processors.starchy_carb_processor import StarchyCarbProcessor
from app.models.database import SessionLocal

# Initialize database session
db = SessionLocal()

# Create processor
processor = StarchyCarbProcessor(db, processor_version="v1.0.0")

# Process single product
result = processor.process_single(product_detail_id=123)

print(f"Protein: {result.guaranteed_analysis_crude_protein_pct}%")
print(f"Fat: {result.guaranteed_analysis_crude_fat_pct}%")
print(f"Fiber: {result.guaranteed_analysis_crude_fiber_pct}%")
print(f"Moisture: {result.guaranteed_analysis_crude_moisture_pct}%")
print(f"Ash: {result.guaranteed_analysis_crude_ash_pct}%")
print(f"Starchy Carbs: {result.starchy_carb_pct}%")

# Process all products
results = processor.process_all(limit=100, skip_existing=True)
print(f"Processed: {results['success']}, Failed: {results['failed']}")

# Show statistics
processor.print_statistics()

db.close()
```

### Direct Calculation

```python
from app.processors.starchy_carb_processor import StarchyCarbProcessor

processor = StarchyCarbProcessor(None)

# Dry food calculation
dry_carbs = processor.calculate_starchy_carbs(
    protein=28.0,
    fat=15.0,
    fiber=5.0,
    moisture=10.0,
    ash=6.0,
    food_category="Dry"
)
print(f"Dry Food Carbs: {dry_carbs}%")  # 35.0%

# Wet food calculation
wet_carbs = processor.calculate_starchy_carbs(
    protein=4.1,
    fat=6.7,
    fiber=2.3,
    moisture=74.5,
    ash=6.0,
    food_category="Wet"
)
print(f"Wet Food Carbs: {wet_carbs}%")  # 21.2%
```

### Extraction Only

```python
from app.processors.starchy_carb_processor import StarchyCarbProcessor
from app.models.product import ProductDetails
from app.models.database import SessionLocal

db = SessionLocal()
processor = StarchyCarbProcessor(db)

# Get product detail
detail = db.query(ProductDetails).get(123)

# Extract nutrition values
nutrition_values = processor.extract_all_nutrition_values(detail)

print(f"Protein: {nutrition_values['crude_protein_pct']}%")
print(f"Fat: {nutrition_values['crude_fat_pct']}%")
print(f"Fiber: {nutrition_values['crude_fiber_pct']}%")
print(f"Moisture: {nutrition_values['crude_moisture_pct']}%")
print(f"Ash: {nutrition_values['crude_ash_pct']}%")

db.close()
```

---

## Validation

### Ingredient Validation (Optional)

The processor includes an optional ingredient validation method to confirm carb presence:

```python
processor = StarchyCarbProcessor(db)

# Check if ingredients contain starchy carb sources
has_carbs = processor.validate_ingredients(detail.ingredients)

# Searches for: potato, sweet potato, rice, brown rice, millet, barley,
# oats, quinoa, chickpea, lentil, pea, corn, wheat
```

**Note:** This is confirmational only and does not affect the numeric output.

---

## Error Handling

### Missing Required Values

**Dry Food:**
- Missing protein, fat, or fiber → Returns `None`
- Missing moisture → Excluded from calculation
- Missing ash → Uses default 6.0%

**Wet/Raw Food:**
- Missing protein, fat, or fiber → Returns `None`
- Missing moisture → Returns `None` (required for conversion)
- Missing ash → Uses default 6.0%

### Invalid Values

- Negative values → Clamped to 0.0
- Invalid dry matter (≤ 0) → Returns `None`
- Non-numeric matches → Skipped, tries next pattern

---

## Statistics

View processing statistics:

```bash
python scripts/process_starchy_carb.py --stats
```

**Output includes:**
- Count of products with each nutrition value extracted
- Total processed vs unprocessed
- Progress percentage

---

## Best Practices

1. **Run Food Category Processing First**
   - Process food categories before starchy carb extraction for accurate formula selection
   - Command: `python cli.py --process --category`

2. **Handle Missing Data**
   - Dry food can work without moisture
   - Wet/Raw food requires moisture
   - Ash defaults to 6.0% if missing

3. **Reprocessing**
   - Use `--force` flag to reprocess already processed products
   - Useful when food categories are updated

4. **Batch Processing**
   - Use `--limit` for testing
   - Process in batches for large datasets

---

## Troubleshooting

### Issue: Carbs are None

**Possible Causes:**
- Missing protein, fat, or fiber values
- Wet/Raw food missing moisture
- Invalid dry matter calculation

**Solution:**
- Check `guaranteed_analysis` field has required values
- Verify food_category is set correctly
- Review extraction patterns match your data format

### Issue: Incorrect Carb Values

**Possible Causes:**
- Wrong food_category (Dry vs Wet/Raw)
- Missing values not handled correctly
- Regex patterns not matching your format

**Solution:**
- Verify food_category is correct
- Check extracted values match expected
- Review regex patterns if format is unusual

### Issue: Extraction Not Finding Values

**Possible Causes:**
- Values in unexpected fields
- Format not matching regex patterns
- Case sensitivity issues

**Solution:**
- Check all fallback fields (details, more_details, specifications)
- Verify format matches supported patterns
- Patterns are case-insensitive, so check for typos

---

## Related Documentation

- [Food Category Processing Guide](./FOOD_CATEGORY_PROCESSING.md) - Classify food categories
- [Processed Products Quickstart](./PROCESSED_PRODUCTS_QUICKSTART.md) - Database schema overview
- [CLI Guide](./CLI_GUIDE.md) - Command-line interface reference

---

## Version History

- **v1.0.0** - Initial implementation
  - Multi-field extraction with fallbacks
  - Dry and Wet/Raw calculation formulas
  - Category-based formula selection
  - Default ash value: 6.0%
