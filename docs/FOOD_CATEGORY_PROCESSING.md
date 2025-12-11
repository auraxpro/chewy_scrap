# Food Category Processing Guide

## Overview

The Food Category Processing system automatically classifies dog food products into categories (Raw, Fresh, Dry, Wet, Other) using keyword-based classification.

## Quick Start

### Process All Unprocessed Products

```bash
cd api
source .venv/bin/activate
python cli.py --process --category
```

### Process Single Product

```bash
python cli.py --process --category --product-id 123
```

### Show Statistics

```bash
python cli.py --process --category
```

---

## Classification Rules

The classifier uses **keyword matching** on three fields from `product_details`:
- `product_category`
- `product_name`
- `specifications`

### Categories and Keywords

#### Raw
- **Main Keywords:** `raw`
- **Supporting Keywords:** raw food, raw frozen, raw patties, raw nuggets, uncooked, minimally processed, primal raw, raw meal, raw recipe, raw medallions, frozen raw dog food, raw blend, raw coated, raw bites, raw infused, raw bones, raw mix-ins, raw meat formula, BARF diet, biologically appropriate raw food

#### Fresh
- **Main Keywords:** `fresh`
- **Supporting Keywords:** fresh food, gently cooked, lightly cooked, refrigerated, homemade style, fresh frozen, fresh meals, human grade meals, cooked fresh, fresh pet food, whole food diet, fridge-stored, fresh delivery, real food for dogs, refrigerated dog food, made fresh weekly, freshly prepared, gently prepared, made fresh, home-style dog food, cooked to order, fresh from our kitchen

#### Dry
- **Main Keywords:** `kibble`
- **Supporting Keywords:** kibble, dry food, dry kibble, crunchy bites, oven-baked dry, extruded, dry formula, premium dry, grain-free kibble, dry dog formula, dehydrated nuggets, dry meal, dry blend, baked kibble, shelf-stable kibble, complete dry food, balanced dry food, oven-baked bites, dry protein blend, everyday kibble, traditional kibble, premium dry dog food, dry crunch, vet recommended kibble, hard dog food, biscuit-style food

#### Wet
- **Main Keywords:** `wet`, `canned`
- **Supporting Keywords:** wet food, canned food, moist food, slow-cooked in gravy, shelf-stable pouch, stew-like consistency, gently cooked and sealed, cooked in the can, retort pouch, cooked for safety, moisture rich food, stewed, loaf, pate, pâté, broth, gravy, chunk in gravy, shredded in broth, homestyle stew, meat chunks in jelly, pouch food, pull-tab can, shelf-stable wet food, slow cooked, canned entrée, meat loaf style, toppers in gravy, wet entree, classic canned dog food, gravy-rich, soft dog food, tender chunks, loaf-style, meaty stew, canned recipe, hydrated meals, slow-cooked wet food, premium canned dog food, savory wet meal, juicy dog food, ready-to-serve wet, broth-infused, vet-recommended wet food, complete wet food

#### Other
- **Default:** Products that don't match any category keywords

### Confidence Scoring

- **Main keyword exact match:** 1.0 confidence
- **Supporting phrase match:** 0.8 confidence
- **Supporting partial match:** 0.6 confidence
- **Single word match:** 0.7 confidence

---

## CLI Commands

### Basic Usage

```bash
# Process all unprocessed products
python cli.py --process --category

# Process with limit
python cli.py --process --category --limit 100

# Process single product
python cli.py --process --category --product-id 123

# Show statistics
python cli.py --process --category

# Show CLI help
python cli.py --help
```

### Advanced Usage

```bash
# Reprocess all (force update existing)
python cli.py --process --category --force

# Reprocess specific category
python cli.py --process --category --reprocess-category Dry

# Process with custom version
python cli.py --process --category

# Reprocess 50 Dry products
python cli.py --process --category --reprocess-category Dry --limit 50
```

### Help

```bash
python cli.py --help
```

---

## Python API Usage

### Basic Classification

```python
from app.processors.category_classifier import classify_food_category

# Classify a product
result = classify_food_category(
    product_category="Dry Dog Food",
    product_name="Blue Buffalo Wilderness High Protein Kibble",
    specifications="Grain-free dry formula"
)

print(result.category)           # FoodCategory.DRY
print(result.confidence)         # 1.0
print(result.matched_keywords)   # ['kibble', 'dry food', ...]
print(result.reason)             # "Classified as 'Dry' with high confidence..."
```

### Process and Save to Database

```python
from app.models.database import SessionLocal
from app.processors.food_category_processor import FoodCategoryProcessor

# Create database session
db = SessionLocal()

# Create processor
processor = FoodCategoryProcessor(db, processor_version="v1.0.0")

# Process single product
processed = processor.process_single(product_detail_id=123)
print(f"Category: {processed.food_category}")
print(f"Reason: {processed.category_reason}")

# Process all unprocessed
results = processor.process_all(limit=100, skip_existing=True)
print(f"Processed: {results['success']}/{results['total']}")

# Show statistics
processor.print_statistics()

# Close session
db.close()
```

### Batch Processing

```python
from app.processors.food_category_processor import FoodCategoryProcessor
from app.models.database import SessionLocal

db = SessionLocal()
processor = FoodCategoryProcessor(db)

# Process specific IDs
product_ids = [1, 2, 3, 4, 5]
results = processor.process_batch(product_ids, skip_errors=True)

print(f"Success: {results['success']}")
print(f"Failed: {results['failed']}")

db.close()
```

---

## Database Schema

### Input Table: `product_details`
```sql
product_details
├── id (PK)
├── product_category    -- Used for classification
├── product_name        -- Used for classification
├── specifications      -- Used for classification
└── ... (other fields)
```

### Output Table: `processed_products`
```sql
processed_products
├── id (PK)
├── product_detail_id (FK → product_details.id)
├── food_category (ENUM)       -- Result: Raw/Fresh/Dry/Wet/Other
├── category_reason (TEXT)     -- Explanation of classification
├── processed_at (TIMESTAMP)   -- When processed
├── processor_version (VARCHAR) -- Version tracking
└── ... (other fields)
```

---

## Examples

### Example 1: Dry Kibble

**Input:**
- `product_category`: "Dry Dog Food"
- `product_name`: "Blue Buffalo Wilderness High Protein Kibble"
- `specifications`: "Grain-free dry formula"

**Output:**
- `food_category`: "Dry"
- `category_reason`: "Classified as 'Dry' with high confidence based on keywords: 'kibble', 'dry food'"
- `confidence`: 1.0

### Example 2: Raw Frozen

**Input:**
- `product_category`: "Frozen Dog Food"
- `product_name`: "Primal Raw Frozen Beef Formula"
- `specifications`: "Raw frozen patties, uncooked"

**Output:**
- `food_category`: "Raw"
- `category_reason`: "Classified as 'Raw' with high confidence based on keywords: 'raw', 'raw frozen', 'uncooked'"
- `confidence`: 1.0

### Example 3: Fresh Meals

**Input:**
- `product_category`: "Fresh Dog Food"
- `product_name`: "The Farmer's Dog Fresh Meals"
- `specifications`: "Gently cooked, refrigerated, human grade"

**Output:**
- `food_category`: "Fresh"
- `category_reason`: "Classified as 'Fresh' with high confidence based on keywords: 'fresh', 'gently cooked', 'refrigerated'"
- `confidence`: 1.0

### Example 4: Wet Canned

**Input:**
- `product_category`: "Canned Dog Food"
- `product_name`: "Merrick Grain Free Wet Dog Food"
- `specifications`: "Chunks in gravy, pate style"

**Output:**
- `food_category`: "Wet"
- `category_reason`: "Classified as 'Wet' with high confidence based on keywords: 'canned', 'wet food', 'gravy'"
- `confidence`: 1.0

---

## Workflow

### 1. Initial Processing
```bash
# Process all scraped products
python cli.py --process --category

# Check results
python cli.py --process --category
```

### 2. Verify Results
```python
from app.models.database import SessionLocal
from app.models import ProcessedProduct

db = SessionLocal()

# Check some results
samples = db.query(ProcessedProduct).limit(10).all()
for p in samples:
    print(f"{p.id}: {p.food_category} - {p.category_reason}")

db.close()
```

### 3. Handle Misclassifications

If you find misclassifications, you can:

**Option A: Reprocess specific products**
```bash
python scripts/process_food_categories.py --single 123
```

**Option B: Reprocess entire category**
```bash
python scripts/process_food_categories.py --reprocess-category Other
```

**Option C: Update keywords and reprocess all**
1. Edit `api/app/processors/category_classifier.py`
2. Update keyword lists
3. Reprocess: `python scripts/process_food_categories.py --all --reprocess`

---

## Performance

### Expected Speed
- **~5-10 products/second** on typical hardware
- **1,000 products** in ~2-3 minutes
- **10,000 products** in ~20-30 minutes

### Optimization Tips
- Use `--limit` for testing
- Use `skip_existing=True` (default) to only process new records
- Process in batches during development

---

## Troubleshooting

### Issue: "ProcessedProduct has no food_category"
**Solution:** Make sure you've run the migration:
```bash
alembic upgrade head
```

### Issue: "No module named 'app'"
**Solution:** Run from the api directory:
```bash
cd api
python cli.py --process --category
```

### Issue: Low confidence classifications
**Solution:** Check the matched keywords and adjust keyword lists if needed.

### Issue: Many "Other" classifications
**Solution:** Review the `category_reason` field to understand why products aren't matching. Consider adding more keywords.

---

## Statistics Interpretation

```bash
python cli.py --process --category
```

**Output:**
```
======================================================================
FOOD CATEGORY STATISTICS
======================================================================

By Category:
  Raw                234 products
  Fresh               89 products
  Dry              3,456 products
  Wet              1,234 products
  Other              156 products

Overall:
  Total Processed:   5,169
  Total Details:     5,500
  Unprocessed:         331
  Progress:          94.0%
======================================================================
```

**What to look for:**
- **High "Other" count** → Keywords may be too specific
- **Imbalanced distribution** → Expected (more dry food than raw)
- **Low progress %** → Run processing with larger limit
- **Unprocessed count** → Products without processed_products record

---

## Next Steps

After processing food categories:

1. **Verify accuracy** - Sample check classifications
2. **Process other fields** - Implement other processors for:
   - Sourcing integrity
   - Processing methods
   - Ingredient analysis
   - Guaranteed analysis parsing
3. **Build scoring system** - Use processed data for scoring
4. **API endpoints** - Expose classification data via REST API

---

## Related Files

- Classifier: `api/app/processors/category_classifier.py`
- Processor: `api/app/processors/food_category_processor.py`
- CLI: `api/cli.py`
- Model: `api/app/models/product.py`
- Schema: `api/app/schemas/processed_product.py`

---

## Support

For issues or questions:
1. Check the `category_reason` field for classification explanations
2. Run `--test` mode to validate classifier behavior
3. Review keyword lists in `category_classifier.py`
4. Use `--stats` to understand distribution