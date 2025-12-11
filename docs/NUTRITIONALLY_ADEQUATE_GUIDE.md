# Nutritionally Adequate Classifier Guide

## Overview

The **Nutritionally Adequate Classifier** identifies whether a dog food product is nutritionally adequate (complete and balanced) by analyzing product details, specifications, and feeding instructions. This classification helps determine if a product meets AAFCO (Association of American Feed Control Officials) standards for complete and balanced nutrition.

**Classification Categories:**
- **Yes** - Product is complete and balanced, meets AAFCO standards
- **No** - Product is not complete and balanced, intended for supplemental/intermittent feeding
- **Other** - Unable to determine from available information

## Key Features

### 1. Multi-Field Text Analysis
The classifier analyzes text from multiple database fields:
- `details` - Key benefits/features
- `more_details` - Additional product details
- `specifications` - Technical specifications
- `feeding_instructions` - Feeding instructions
- `transition_instructions` - Transition instructions

### 2. Text Normalization
- Converts to lowercase
- Removes special characters (keeps hyphens and apostrophes)
- Normalizes whitespace
- Combines all fields with separator

### 3. Priority-Based Detection
The classifier uses a priority-based approach:
1. **No** - Detected first (highest priority)
   - Looks for "not nutritionally complete & balanced" keywords
   - Identifies products intended for supplemental/intermittent feeding
2. **Yes** - Detected second
   - Looks for "complete and balanced" keywords
   - Identifies AAFCO-compliant products
3. **Other** - Fallback when no keywords match

### 4. Keyword Matching Strategy
- **Main Keywords**: Primary identifiers (exact match = 1.0 confidence)
- **Support Keywords**: Variations and related terms
  - Phrase match = 0.8 confidence
  - Partial match = 0.5 confidence

### 5. Database Integration
Results are saved to `processed_products` table:
- `nutritionally_adequate` - Classification result (Yes/No/Other)
- `nutritionally_adequate_reason` - Explanation of classification

---

## Quick Start

### Basic Usage

```python
from app.processors.nutritionally_adequate_classifier import (
    NutritionallyAdequateClassifier,
)

# Create classifier instance
classifier = NutritionallyAdequateClassifier()

# Classify a product
result = classifier.classify(
    details="This product is formulated to meet AAFCO Dog Food Nutrient Profiles for maintenance of adult dogs.",
    more_details="Complete and balanced nutrition for all life stages.",
    specifications="AAFCO compliant formulation",
    feeding_instructions="Feed according to package directions",
    transition_instructions="Gradually transition over 7-10 days"
)

print(f"Classification: {result.nutritionally_adequate}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Reason: {result.reason}")
```

### Classification Result

The `NutritionallyAdequateResult` object contains:

```python
@dataclass
class NutritionallyAdequateResult:
    nutritionally_adequate: str  # "Yes", "No", or "Other"
    confidence: float  # Confidence score (0.0 to 1.0)
    matched_keywords: List[str]  # Keywords that matched
    reason: str  # Explanation of classification
```

**Example Output:**
```
nutritionally_adequate: "Yes"
confidence: 1.0
matched_keywords: ['complete and balanced', 'formulated to meet aafco dog food nutrient profiles for', 'aafco compliant']
reason: "Classified as Yes based on keywords: complete and balanced, formulated to meet aafco dog food nutrient profiles for, aafco compliant"
```

---

## Keyword Categories

### Yes Keywords - Complete and Balanced

**Main Keywords:**
- `complete and balanced`

**Support Keywords:**
- `formulated to meet aafco dog food nutrient profiles for`
- `animal feeding tests using aafco procedures substantiate that this product provides complete and balanced nutrition for`
- `this product is formulated to meet the nutritional levels established by the aafco dog food nutrient profiles for maintenance of adult dogs`
- `animal feeding tests using aafco procedures`
- `substantiates complete and balanced nutrition`
- `meets aafco nutrient profiles`
- `formulated for all life stages`
- `meets nutritional levels established by aafco`
- `aafco compliant`
- `nutritionally adequate`
- `meets dog food nutrient guidelines`
- `balanced for maintenance`
- `suitable for growth and maintenance`
- `developed to support dog health`
- `veterinarian formulated to aafco standards`
- `aafco feeding trials`
- `provides full and balanced nutrition`
- `meets all nutritional requirements`
- `covers canine nutritional needs`
- `meets aafco recommendations`
- `aafco approved formulation`

### No Keywords - Not Nutritionally Complete & Balanced

**Main Keywords:**
- `not nutritionally complete & balanced`
- `not nutritionally complete and balanced`

**Support Keywords:**
- `this product is intended for intermittent or supplemental feeding only`
- `this food is not complete and balanced and should be fed only as a topper or with a complete and balanced base food`
- `intended for intermittent or supplemental feeding only`
- `not complete and balanced`
- `feed as a topper only`
- `feed with a complete and balanced base`
- `not a sole source of nutrition`
- `should be fed with a balanced food`
- `does not meet aafco nutrient profiles`
- `incomplete nutrition`
- `not a complete diet`
- `lacks full nutrient profile`
- `not suitable as primary food`
- `for intermittent feeding`
- `not for long-term feeding`
- `supplemental use only`
- `feed in combination with other foods`
- `requires additional nutritional support`
- `not aafco compliant`
- `not formulated to meet aafco standards`
- `unbalanced formula`
- `missing essential nutrients`

---

## Using the Processor

### Command Line Interface

The easiest way to process products is through the CLI:

```bash
# Process all products
python scripts/main.py --process --nutritionally-adequate

# Process with limit
python scripts/main.py --process --nutritionally-adequate --limit 100

# Process single product
python scripts/main.py --process --nutritionally-adequate --product-id 123

# Force reprocess all (skip existing check)
python scripts/main.py --process --nutritionally-adequate --force
```

### Python API

```python
from app.processors.nutritionally_adequate_processor import (
    NutritionallyAdequateProcessor,
)
from app.models.database import SessionLocal

# Create database session
db = SessionLocal()

try:
    # Create processor
    processor = NutritionallyAdequateProcessor(db, processor_version="v1.0.0")
    
    # Process single product
    result = processor.process_single(product_detail_id=123)
    print(f"Nutritionally Adequate: {result.nutritionally_adequate}")
    print(f"Reason: {result.nutritionally_adequate_reason}")
    
    # Process all products
    stats = processor.process_all(limit=100, skip_existing=True)
    print(f"Processed: {stats['success']}/{stats['total']}")
    
    # Get statistics
    processor.print_statistics()
    
finally:
    db.close()
```

### Batch Processing

```python
from app.processors.nutritionally_adequate_processor import (
    NutritionallyAdequateProcessor,
)
from app.models.database import SessionLocal

db = SessionLocal()
processor = NutritionallyAdequateProcessor(db)

# Process specific product IDs
product_ids = [123, 456, 789]
results = processor.process_batch(product_ids, skip_errors=True)

print(f"Success: {results['success']}")
print(f"Failed: {results['failed']}")
if results.get('failed_ids'):
    print(f"Failed IDs: {results['failed_ids']}")
```

---

## Database Schema

### ProcessedProduct Fields

The processor updates these fields in the `processed_products` table:

| Field | Type | Description |
|-------|------|-------------|
| `nutritionally_adequate` | `NutritionallyAdequateEnum` | Classification result: `Yes`, `No`, or `Other` |
| `nutritionally_adequate_reason` | `TEXT` | Explanation of classification |

### Enum Values

The `NutritionallyAdequateEnum` supports three values:
- `Yes` - Product is complete and balanced
- `No` - Product is not complete and balanced
- `Other` - Unable to determine

---

## Classification Examples

### Example 1: Complete and Balanced (Yes)

**Input:**
```
details: "Formulated to meet AAFCO Dog Food Nutrient Profiles for maintenance of adult dogs. Complete and balanced nutrition."
specifications: "AAFCO compliant"
feeding_instructions: "Feed according to package directions"
```

**Output:**
```
nutritionally_adequate: "Yes"
confidence: 1.0
reason: "Classified as Yes based on keywords: complete and balanced, formulated to meet aafco dog food nutrient profiles for, aafco compliant"
```

### Example 2: Not Complete (No)

**Input:**
```
details: "This product is intended for intermittent or supplemental feeding only."
more_details: "Not a complete and balanced diet. Feed as a topper only."
```

**Output:**
```
nutritionally_adequate: "No"
confidence: 1.0
reason: "Classified as No based on keywords: this product is intended for intermittent or supplemental feeding only, not complete and balanced, feed as a topper only"
```

### Example 3: No Information (Other)

**Input:**
```
details: "Premium dog food with natural ingredients."
specifications: "Made with real chicken"
```

**Output:**
```
nutritionally_adequate: "Other"
confidence: 0.8
reason: "No nutritionally adequate keywords detected in product information"
```

---

## Statistics and Reporting

### Get Statistics

```python
from app.processors.nutritionally_adequate_processor import (
    NutritionallyAdequateProcessor,
)
from app.models.database import SessionLocal

db = SessionLocal()
processor = NutritionallyAdequateProcessor(db)

# Get statistics dictionary
stats = processor.get_statistics()
print(stats)

# Print formatted statistics
processor.print_statistics()
```

### Statistics Output

```
======================================================================
NUTRITIONALLY ADEQUATE STATISTICS
======================================================================

Nutritionally Adequate Status:
  Yes              1,234 products
  No                 567 products
  Other              890 products
  NULL               123 products

Overall:
  Total Processed:    2,691
  Total Details:      2,814
  Unprocessed:         123
  Progress:           95.6%
======================================================================
```

---

## Workflow Integration

### Typical Processing Workflow

1. **Scrape Product Details**
   ```bash
   python scripts/main.py --scrape --details
   ```

2. **Process Nutritionally Adequate Status**
   ```bash
   python scripts/main.py --process --nutritionally-adequate
   ```

3. **View Statistics**
   ```bash
   python scripts/main.py --stats
   ```

### Integration with Other Processors

The nutritionally adequate processor can be run alongside other processors:

```bash
# Process multiple features
python scripts/main.py --process --category
python scripts/main.py --process --sourcing
python scripts/main.py --process --processing
python scripts/main.py --process --nutritionally-adequate
python scripts/main.py --process --ingredient-quality
python scripts/main.py --process --longevity-additives
```

---

## Troubleshooting

### Common Issues

#### 1. Enum Value Error

**Error:**
```
invalid input value for enum nutritionallyadequateenum: "Other"
```

**Solution:**
Add "Other" to the enum type in PostgreSQL:

```sql
ALTER TYPE nutritionallyadequateenum ADD VALUE IF NOT EXISTS 'Other';
```

Or use the provided script:
```bash
python scripts/add_nutritionally_adequate_other.py
```

#### 2. No Text Available

**Issue:** Product has no details, specifications, or feeding instructions.

**Result:** Classified as "Other" with reason "No text available for classification"

**Solution:** Ensure product details are scraped before processing:
```bash
python scripts/main.py --scrape --details --product-id 123
```

#### 3. Low Confidence Scores

**Issue:** Classification confidence is low (< 0.5)

**Possible Causes:**
- Text doesn't contain clear nutritionally adequate statements
- Keywords are misspelled or formatted differently
- Product information is incomplete

**Solution:** Review the `nutritionally_adequate_reason` field to see which keywords matched (if any)

---

## Best Practices

### 1. Process After Scraping
Always scrape product details before processing:
```bash
# Step 1: Scrape
python scripts/main.py --scrape --details

# Step 2: Process
python scripts/main.py --process --nutritionally-adequate
```

### 2. Use Limits for Testing
Test with a small limit first:
```bash
python scripts/main.py --process --nutritionally-adequate --limit 10
```

### 3. Check Statistics Regularly
Monitor processing progress:
```bash
python scripts/main.py --stats
```

### 4. Handle Errors Gracefully
The processor skips errors by default. Check failed IDs:
```python
results = processor.process_batch(product_ids, skip_errors=True)
if results.get('failed_ids'):
    print(f"Failed IDs: {results['failed_ids']}")
```

---

## Advanced Usage

### Custom Classification Logic

You can extend the classifier with custom keywords:

```python
from app.processors.nutritionally_adequate_classifier import (
    NutritionallyAdequateClassifier,
    YES_KEYWORDS,
    NO_KEYWORDS,
)

# Add custom keywords
YES_KEYWORDS.supporting.append("custom keyword here")
NO_KEYWORDS.supporting.append("another custom keyword")

classifier = NutritionallyAdequateClassifier()
result = classifier.classify(...)
```

### Reprocessing Specific Categories

Reprocess products with a specific classification:

```python
from app.processors.nutritionally_adequate_processor import (
    NutritionallyAdequateProcessor,
)
from app.models.database import SessionLocal
from sqlalchemy import and_

db = SessionLocal()
processor = NutritionallyAdequateProcessor(db)

# Find products classified as "Other"
from app.models import ProcessedProduct
other_products = db.query(ProcessedProduct).filter(
    ProcessedProduct.nutritionally_adequate == "Other"
).all()

# Reprocess them
product_ids = [p.product_detail_id for p in other_products]
results = processor.process_batch(product_ids, skip_errors=True)
```

---

## Related Documentation

- [CLI Guide](./CLI_GUIDE.md) - Command-line interface usage
- [Processed Products Quickstart](./PROCESSED_PRODUCTS_QUICKSTART.md) - Database schema overview
- [Workflow Guide](./WORKFLOW.md) - End-to-end processing workflow
- [Ingredient Quality Guide](./INGREDIENT_QUALITY_GUIDE.md) - Related ingredient analysis
- [Processing Method Guide](./PROCESSING_METHOD_GUIDE.md) - Processing method classification

---

## Version History

- **v1.0.0** (2025-12-11) - Initial implementation
  - Yes/No/Other classification
  - Multi-field text analysis
  - Priority-based detection
  - CLI integration

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the CLI help: `python scripts/main.py --help`
3. Check database enum values: `SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'nutritionallyadequateenum')`
