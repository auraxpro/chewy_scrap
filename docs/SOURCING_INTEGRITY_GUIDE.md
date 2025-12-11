# Sourcing Integrity Classifier Guide

## Overview

The **Sourcing Integrity Classifier** analyzes dog food products and classifies them into sourcing integrity categories based on keyword matching across multiple product fields.

**Classification Categories:**
- `Human Grade (organic)` - Products with both human-grade and organic certifications
- `Human Grade` - Products made with human-grade ingredients
- `Feed Grade` - Products made with feed-grade ingredients
- `Other` - Products that don't match any specific category

## Key Features

### 1. Multi-Field Analysis
The classifier examines 4 product fields:
- `product_category` - Product category from scraped data
- `product_name` - Product name
- `specifications` - Product specifications/description
- `ingredient_list` - List of ingredients

### 2. Keyword-Based Classification
Uses main keywords and supporting keywords for each category:

**Human Grade (organic):**
- Main: "Organic human-grade"
- Supporting: USDA organic, certified organic, organic meat, organic vegetables, human grade + organic, etc.

**Human Grade:**
- Main: "Human Grade", "Human-grade"
- Supporting: human grade ingredients, USDA inspected, fit for human consumption, human edible, made in human food facility, etc.

**Feed Grade:**
- Main: "Feed Grade", "Feed-grade"
- Supporting: feed quality, animal feed, not for human consumption, rendered meat, by-products, meat meal, etc.

### 3. Confidence Scoring
- **Main keyword exact match**: 1.0 confidence
- **Supporting keyword phrase match**: 0.8 confidence
- **Supporting keyword partial match**: 0.6 confidence
- **Supporting single word match**: 0.7 confidence

### 4. Special Logic for Human Grade (organic)
Must detect BOTH human-grade AND organic indicators to classify as "Human Grade (organic)". If only one is present, falls back to the appropriate single category or "Other".

---

## Quick Start

### Basic Usage

```python
from app.processors.sourcing_integrity_classifier import (
    SourcingIntegrityClassifier,
    classify_sourcing_integrity,
)

# Method 1: Using convenience function
result = classify_sourcing_integrity(
    product_name="Organic Human Grade Chicken Recipe",
    specifications="USDA organic certified, made in human food facility",
    ingredient_list="Organic chicken, organic vegetables"
)

print(f"Category: {result.sourcing_integrity.value}")
print(f"Confidence: {result.confidence}")
print(f"Reason: {result.reason}")

# Method 2: Using classifier instance (recommended for batch processing)
classifier = SourcingIntegrityClassifier()

result = classifier.classify(
    product_category="Premium Dog Food",
    product_name="Human Grade Beef Formula",
    specifications="Human grade ingredients, USDA inspected",
    ingredient_list="Human edible beef, restaurant quality vegetables"
)
```

### Classification Result

The `SourcingClassificationResult` object contains:

```python
@dataclass
class SourcingClassificationResult:
    sourcing_integrity: SourcingIntegrity  # Enum value
    confidence: float                       # 0.0 to 1.0
    matched_keywords: List[str]            # Keywords that matched
    reason: str                            # Human-readable explanation
```

**Example Output:**
```
sourcing_integrity: Human Grade (organic)
confidence: 1.0
matched_keywords: ['USDA organic', 'human grade ingredients', 'organic chicken']
reason: "Classified as 'Human Grade (organic)' with high confidence based on keywords: 'USDA organic', 'human grade ingredients', 'organic chicken'"
```

---

## Classifier Details

### Classification Logic

1. **Combine all text fields** into a single searchable string
2. **Normalize text** (lowercase, clean whitespace, remove special chars)
3. **Calculate scores** for each category based on keyword matches
4. **Special handling for Human Grade (organic)**:
   - Check for both human-grade AND organic indicators
   - If both present → "Human Grade (organic)"
   - If only one present → continue to next priority
5. **Apply priority order**:
   - Human Grade (organic) (highest)
   - Human Grade
   - Feed Grade
   - Other (fallback)

### Keyword Matching Strategy

**Main Keywords** (1.0 confidence):
- Exact phrase match for multi-word keywords
- Word boundary match for single-word keywords

**Supporting Keywords**:
- **Multi-word phrase** (0.8 confidence): Exact phrase match
- **Multi-word partial** (0.6 confidence): All words present but not consecutive
- **Single word** (0.7 confidence): Word boundary match

### Human Grade (organic) Detection

To be classified as "Human Grade (organic)", the product must contain:

**Human Grade Indicators:**
- "human grade" or "human-grade"
- "human quality"
- "human edible"
- "human food facility"
- "human consumption"
- "food-grade facility"
- And similar variations

**AND Organic Indicators:**
- "organic"
- "USDA organic"
- "certified organic"
- "organically"

---

## Processor Usage

The `SourcingIntegrityProcessor` handles database operations and batch processing.

### Process Single Product

```python
from app.processors.sourcing_integrity_processor import SourcingIntegrityProcessor
from app.models.database import SessionLocal

db = SessionLocal()
processor = SourcingIntegrityProcessor(db)

# Process one product
processed = processor.process_single(product_detail_id=123)

print(f"Sourcing Integrity: {processed.sourcing_integrity}")
print(f"Reason: {processed.sourcing_integrity_reason}")
```

### Process All Products

```python
# Process all products (creates new or updates existing records)
results = processor.process_all()

print(f"Total: {results['total']}")
print(f"Success: {results['success']}")
print(f"Failed: {results['failed']}")

# Process only unprocessed products
results = processor.process_all(skip_existing=True)

# Process with limit
results = processor.process_all(limit=100, skip_existing=True)
```

### Batch Processing

```python
# Process specific product IDs
product_ids = [1, 2, 3, 4, 5]
results = processor.process_batch(product_ids)

# Process with error handling
results = processor.process_batch(product_ids, skip_errors=False)  # Raises on error
```

### Reprocess Category

```python
# Reprocess all "Human Grade" products
results = processor.reprocess_category("Human Grade")

# Reprocess with limit
results = processor.reprocess_category("Human Grade (organic)", limit=50)
```

### Statistics

```python
# Get statistics
stats = processor.get_statistics()
print(stats)
# Output:
# {
#     'Human Grade (organic)': 45,
#     'Human Grade': 123,
#     'Feed Grade': 67,
#     'Other': 234,
#     '_total_processed': 469,
#     '_total_details': 500,
#     '_unprocessed': 31
# }

# Print formatted statistics
processor.print_statistics()
```

---

## Integration with Database

### Database Schema

The processor updates the `processed_products` table:

```sql
processed_products:
  - sourcing_integrity (enum: 'Human Grade (organic)', 'Human Grade', 'Feed Grade', 'Other')
  - sourcing_integrity_reason (text)
  - processed_at (timestamp)
  - processor_version (varchar)
```

### Workflow

1. **Processor reads** from `product_details` table
2. **Classifier analyzes** the product fields
3. **Processor writes** results to `processed_products` table
4. If record exists, it's updated; otherwise, a new record is created

---

## Command Line Interface (CLI)

### Using the Unified CLI

The main CLI tool provides easy access to sourcing integrity processing:

```bash
# Process all unprocessed products
python cli.py --process --sourcing

# Process with limit
python cli.py --process --sourcing --limit 100

# Process single product
python cli.py --process --sourcing --product-id 123

# Reprocess all products (force)
python cli.py --process --sourcing --force

# Reprocess specific sourcing integrity category
python cli.py --process --sourcing --reprocess-sourcing "Human Grade"
python cli.py --process --sourcing --reprocess-sourcing "Human Grade (organic)"
python cli.py --process --sourcing --reprocess-sourcing "Feed Grade"

# Show help
python cli.py --help
```

### Using the Standalone Script

Use the standalone script for more options:

```bash
# Process all unprocessed products
python scripts/process_sourcing_integrity.py

# Process with limit
python scripts/process_sourcing_integrity.py --limit 100

# Reprocess all products
python scripts/process_sourcing_integrity.py --reprocess

# Reprocess specific category
python scripts/process_sourcing_integrity.py --reprocess-category "Human Grade"

# Show statistics only
python scripts/process_sourcing_integrity.py --stats-only

# Test mode (no database changes)
python scripts/process_sourcing_integrity.py --test
```

### Direct Module Execution

```bash
# Run classifier tests
python -m app.processors.sourcing_integrity_classifier

# Run processor demo
python -m app.processors.sourcing_integrity_processor
```

---

## Examples

### Example 1: Human Grade (organic) Product

```python
classifier = SourcingIntegrityClassifier()

result = classifier.classify(
    product_name="Organic Human Grade Chicken Recipe",
    specifications="USDA organic certified, made in human food facility",
    ingredient_list="Organic chicken, organic vegetables, certified organic"
)

# Result:
# sourcing_integrity: Human Grade (organic)
# confidence: 1.0
# matched_keywords: ['USDA organic', 'human grade', 'organic chicken', ...]
```

### Example 2: Human Grade Product

```python
result = classifier.classify(
    product_name="Human Grade Beef Formula",
    specifications="Human grade ingredients, USDA inspected facility",
    ingredient_list="Human edible beef, restaurant quality vegetables"
)

# Result:
# sourcing_integrity: Human Grade
# confidence: 1.0
# matched_keywords: ['human grade', 'Human grade ingredients', 'USDA inspected', ...]
```

### Example 3: Feed Grade Product

```python
result = classifier.classify(
    product_name="Complete Dog Food",
    specifications="Feed grade, meat meal, by-products",
    ingredient_list="Meat by-product meal, rendered meat, animal feed quality"
)

# Result:
# sourcing_integrity: Feed Grade
# confidence: 1.0
# matched_keywords: ['feed grade', 'meat meal', 'by-products', ...]
```

### Example 4: Other Category

```python
result = classifier.classify(
    product_name="Premium Recipe",
    specifications="High quality ingredients",
    ingredient_list="Chicken, rice, vegetables"
)

# Result:
# sourcing_integrity: Other
# confidence: 0.8
# matched_keywords: []
# reason: "No sourcing integrity keywords detected in product information"
```

### Example 5: Organic Only (Not Human Grade)

```python
result = classifier.classify(
    product_name="Organic Chicken Meal",
    specifications="USDA organic certified",
    ingredient_list="Organic chicken meal, organic vegetables"
)

# Result:
# sourcing_integrity: Other (or Human Grade (organic) if classifier is less strict)
# Note: Without human-grade indicators, may not qualify for Human Grade (organic)
```

---

## Batch Processing Best Practices

### Reuse Classifier Instance

```python
# Good: Reuse classifier instance
classifier = SourcingIntegrityClassifier()
for product in products:
    result = classifier.classify(...)

# Better: Use batch method
products = [
    {
        "product_category": "Dog Food",
        "product_name": "Product 1",
        "specifications": "...",
        "ingredient_list": "..."
    },
    # ... more products
]
results = classifier.classify_batch(products)
```

### Database Processing

```python
from sqlalchemy.orm import Session
from app.models import ProductDetails, ProcessedProduct
from app.processors.sourcing_integrity_processor import SourcingIntegrityProcessor

def classify_all_products(db: Session, limit: int = 100):
    """Classify all products that don't have sourcing integrity yet."""
    
    processor = SourcingIntegrityProcessor(db)
    
    # Find products without classification
    unclassified = db.query(ProductDetails).outerjoin(
        ProcessedProduct,
        ProductDetails.id == ProcessedProduct.product_detail_id
    ).filter(
        (ProcessedProduct.id.is_(None)) |
        (ProcessedProduct.sourcing_integrity.is_(None))
    ).limit(limit).all()
    
    print(f"Found {len(unclassified)} unclassified products")
    
    # Process in batch
    detail_ids = [d.id for d in unclassified]
    results = processor.process_batch(detail_ids)
    
    return results
```

---

## Testing

### Run Built-in Tests

```python
# Test the classifier
python api/app/processors/sourcing_integrity_classifier.py

# Test the processor
python api/app/processors/sourcing_integrity_processor.py
```

### Custom Test Cases

```python
from app.processors.sourcing_integrity_classifier import SourcingIntegrityClassifier

classifier = SourcingIntegrityClassifier()

test_products = [
    ("Organic Human Grade", "USDA organic, human food facility", "organic chicken"),
    ("Human Grade Beef", "USDA inspected", "human edible beef"),
    ("Budget Food", "Feed grade ingredients", "meat meal, by-products"),
]

for name, specs, ingredients in test_products:
    result = classifier.classify(
        product_name=name,
        specifications=specs,
        ingredient_list=ingredients
    )
    print(f"{name}: {result.sourcing_integrity.value} (confidence: {result.confidence})")
```

---

## Advanced Usage

### Custom Confidence Thresholds

```python
classifier = SourcingIntegrityClassifier()

result = classifier.classify(...)

# Apply custom threshold
if result.confidence >= 0.8:
    print(f"High confidence: {result.sourcing_integrity.value}")
elif result.confidence >= 0.5:
    print(f"Medium confidence: {result.sourcing_integrity.value}")
else:
    print(f"Low confidence: {result.sourcing_integrity.value}")
```

### Analyzing Matches

```python
result = classifier.classify(...)

print(f"Category: {result.sourcing_integrity.value}")
print(f"Confidence: {result.confidence}")
print(f"Matched {len(result.matched_keywords)} keywords:")
for kw in result.matched_keywords:
    print(f"  - {kw}")
```

### Text Normalization

```python
classifier = SourcingIntegrityClassifier()

# Access internal normalization method
text = "USDA Organic Human-Grade Ingredients"
normalized = classifier._normalize_text(text)
print(f"Original: {text}")
print(f"Normalized: {normalized}")
# Output: "usda organic human grade ingredients"
```

---

## Troubleshooting

### Issue: Wrong Classification

**Check matched keywords:**
```python
result = classifier.classify(...)
print(f"Matched: {result.matched_keywords}")
print(f"Reason: {result.reason}")
```

**Review input text:**
```python
combined = classifier._combine_text(
    product_category,
    product_name,
    specifications,
    ingredient_list
)
print(f"Combined text: {combined}")
```

### Issue: Low Confidence

- **Cause**: Weak keyword matches (partial matches only)
- **Solution**: Add more supporting keywords or check for main keyword variations

### Issue: Human Grade (organic) Not Detected

- **Cause**: Missing either human-grade OR organic indicators
- **Solution**: Verify both types of keywords are present in the text

### Issue: Performance Concerns

- **Use batch processing** for large datasets
- **Reuse classifier instance** instead of creating new ones
- **Process in chunks** with limits

---

## API Integration

### Convenience Function

```python
from app.processors.sourcing_integrity_processor import process_sourcing_integrity
from app.models.database import SessionLocal

db = SessionLocal()

# Process all
results = process_sourcing_integrity(db)

# Process specific IDs
results = process_sourcing_integrity(db, product_detail_ids=[1, 2, 3])

# Process with options
results = process_sourcing_integrity(
    db,
    limit=100,
    skip_existing=True
)
```

---

## Version Information

**Current Version**: v1.0.0

**Features**:
- Multi-field classification (4 fields)
- Keyword-based matching with confidence scoring
- Special logic for Human Grade (organic) detection
- Batch processing support
- Database integration with processed_products table

---

## Keywords Reference

### Human Grade (organic)

**Main Keywords:**
- Organic human-grade

**Supporting Keywords:**
- USDA organic, certified organic, organic meat, organic vegetables, organic certified
- human grade + organic, made with organic ingredients, organic-certified facility
- organic produce, organically sourced, all-organic formula, non-GMO and organic
- organic pet food, 100% organic, premium organic ingredients, organic human grade food
- organic superfoods, clean organic label, small batch organic
- organic chicken, organic beef, organic lamb, organic turkey
- humanely raised organic, organic whole foods

### Human Grade

**Main Keywords:**
- Human Grade, Human-grade

**Supporting Keywords:**
- human grade ingredients, human quality, USDA inspected
- fit for human consumption, human edible, made in human food facility
- made in USDA-inspected facility, cooked in human-grade kitchens
- made in human food kitchens, crafted to human food standards
- made in USDA kitchen, inspected for human consumption, food-grade facility
- premium human-grade meat, prepared in human-quality facilities
- meets human food safety standards, small batch human grade
- restaurant quality, human-approved formulas, made with human edible meat
- real food for dogs, human-grade sourcing, home-cooked quality

### Feed Grade

**Main Keywords:**
- Feed Grade, Feed-grade

**Supporting Keywords:**
- feed quality, animal feed, not for human consumption, rendered meat
- by-products, meat meal, feed-safe, pet feed, feed-grade ingredients
- feed-use only, not USDA inspected, 4D meat, meat by-product meal
- not human edible, factory scraps, feed-grade facility
- waste-derived protein, animal digest, feed standard
- bulk animal feed, meat and bone meal, slaughterhouse waste
- unfit for human consumption

---

## Summary

The Sourcing Integrity Classifier provides:

✅ **4 sourcing categories** with clear definitions  
✅ **Multi-field analysis** across product data  
✅ **Keyword-based matching** with confidence scoring  
✅ **Special logic** for Human Grade (organic) detection  
✅ **Database integration** for automated processing  
✅ **Batch processing** for efficiency  
✅ **Statistics tracking** for monitoring  

**Use Cases:**
- Classify new products as they're scraped
- Reprocess existing products after keyword updates
- Generate sourcing integrity reports
- Filter products by sourcing quality
- Monitor sourcing integrity distribution

For questions or issues, refer to the test examples in the classifier and processor modules.