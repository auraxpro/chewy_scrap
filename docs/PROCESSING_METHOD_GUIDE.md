# Processing Method Classifier Guide

## Overview

The **Processing Method Classifier** analyzes dog food products and classifies them into processing method categories based on keyword matching across multiple product fields with advanced negation handling and composite method detection.

**Classification Categories:**
- `Uncooked (Not Frozen)` - Raw, refrigerated products
- `Uncooked (Flash Frozen)` - Raw, flash frozen products
- `Uncooked (Frozen)` - Raw, frozen products
- `Lightly Cooked (Not Frozen)` - Gently cooked, fresh products
- `Lightly Cooked (Frozen)` - Gently cooked, frozen products
- `Freeze Dried` - Freeze-dried products
- `Air Dried` - Air-dried products
- `Dehydrated` - Dehydrated products
- `Baked` - Oven-baked products
- `Extruded` - Traditional kibble, extruded products
- `Retorted` - Canned, wet food products
- `Other` - Products that don't match any category

---

## Key Features

### 1. Multi-Field Analysis (6 Fields)
The classifier examines:
- `product_name` - Product name
- `details` - Product details/description
- `more_details` - Additional product details
- `ingredient_list` - List of ingredients
- `specifications` - Product specifications
- `feeding_instructions` - Feeding instructions

### 2. Advanced Keyword Matching
Uses main keywords and supporting keywords for each method:

**Scoring System:**
- **Main keyword match**: +5 points
- **Supporting keyword match**: +2 points
- **Negated main keyword**: -3 points
- **Negated supporting keyword**: -1 point

### 3. Negation Detection
Automatically detects negation words (no, not, never, without, etc.) within 0-4 tokens before keywords:
- "never frozen" → negates frozen matches
- "not extruded" → negates extruded matches
- "no retort pouch" → negates retorted matches

### 4. Composite Method Detection
Supports two-step processing methods:
- **Uncooked + Frozen variants** (Flash Frozen, Frozen)
- **Lightly Cooked + Frozen**

Terminal processes (Freeze Dried, Air Dried, Dehydrated, Baked, Extruded, Retorted) cannot be composite.

### 5. Disambiguation Rules
Smart rules to handle conflicting methods:
- **Extruded vs Baked**: Defaults to Extruded unless "oven-baked" or "gently baked" appear
- **Retorted indicators**: "canned", "in gravy", "pâté" → assign Retorted
- **Freeze Dried vs Frozen**: "freeze-dried" wins unless "keep frozen" present
- **Air Dried vs Dehydrated**: Air dried wins if it's a main keyword match
- **Uncooked vs Lightly Cooked**: Heat verbs override raw unless clearly contrasted

### 6. Minimum Threshold
Method must have:
- Score ≥ 3, OR
- At least 1 non-negated main keyword hit

Otherwise, classified as "Other".

---

## Quick Start

### Basic Usage

```python
from app.processors.processing_method_classifier import (
    ProcessingMethodClassifier,
    classify_processing_method,
)

# Method 1: Using convenience function
result = classify_processing_method(
    product_name="Freeze-Dried Raw Chicken Recipe",
    specifications="Freeze-dried for shelf stability",
    details="Complete freeze-dried raw dog food"
)

print(f"Primary Method: {result.processing_method_1.value}")
print(f"Secondary Method: {result.processing_method_2}")
print(f"Confidence: {result.confidence}")
print(f"Reason: {result.reason}")

# Method 2: Using classifier instance (recommended for batch)
classifier = ProcessingMethodClassifier()

result = classifier.classify(
    product_name="Raw Frozen Beef Patties",
    specifications="Keep frozen, raw frozen dog food",
    details="Frozen raw meals for dogs"
)
```

### Classification Result

The `ProcessingClassificationResult` object contains:

```python
@dataclass
class ProcessingClassificationResult:
    processing_method_1: ProcessingMethod      # Primary method
    processing_method_2: Optional[ProcessingMethod]  # Secondary (composite)
    confidence: float                          # 0.0 to 1.0
    matched_keywords_1: List[str]             # Primary keywords matched
    matched_keywords_2: List[str]             # Secondary keywords matched
    reason: str                               # Human-readable explanation
```

**Example Output:**
```
processing_method_1: Freeze Dried
processing_method_2: None
confidence: 1.0
matched_keywords_1: ['freeze dried', 'freeze-dried raw', 'freeze-dried nuggets']
reason: "Classified as 'Freeze Dried' with high confidence based on keywords: 'freeze dried', 'freeze-dried raw', 'freeze-dried nuggets'"
```

---

## Classifier Details

### Classification Logic

1. **Combine all text fields** into a single searchable string
2. **Normalize text** (lowercase, clean whitespace, remove special chars)
3. **Calculate scores** for each method with negation handling:
   - Find keyword matches
   - Check for negation words within 4 tokens before keyword
   - Apply positive or negative points accordingly
4. **Get best match** (highest score)
5. **Check minimum threshold** (score ≥ 3 OR has main keyword)
6. **Apply disambiguation rules** to resolve conflicts
7. **Detect composite methods** for multi-step processing
8. **Calculate confidence** based on score and match quality
9. **Generate human-readable reason**

### Keyword Matching Strategy

**Main Keywords** (5 points):
- High-signal indicators of processing method
- Example: "freeze dried", "raw", "extruded"

**Supporting Keywords** (2 points):
- Marketing terms and descriptive phrases
- Example: "freeze-dried nuggets", "raw frozen blend", "traditional kibble"

**Negation Handling**:
- Looks back 0-4 tokens before keyword
- Negation words: no, not, never, without, free of, doesn't, isn't, aren't, non-, un-
- Applies penalty scoring when negation detected

### Composite Method Detection

**Allowed Composites:**
1. **Uncooked (Not Frozen) + Frozen variant** → Uncooked (Frozen)
2. **Uncooked (Not Frozen) + Flash Frozen variant** → Uncooked (Flash Frozen)
3. **Lightly Cooked (Not Frozen) + Frozen variant** → Lightly Cooked (Frozen)

**Logic:**
- If primary method is Uncooked or Lightly Cooked
- AND a Frozen/Flash Frozen variant scores ≥ 3
- Assign that as secondary method

**Not Allowed:**
- Freeze Dried, Air Dried, Dehydrated, Baked, Extruded, Retorted are terminal processes
- Cannot be combined with other methods

### Disambiguation Rules in Detail

#### Rule 1: Extruded vs Baked
```
If both score similarly:
  - Default to Extruded
  - UNLESS "oven-baked" or "gently baked" appear as main keywords
  - AND "extruded" is not mentioned
```

#### Rule 2: Retorted Indicators
```
If any of these appear: "canned", "in gravy", "pâté", "retort pouch", "sterilized"
  - AND Retorted score ≥ 3
  - Assign Retorted
```

#### Rule 3: Freeze Dried vs Frozen
```
If Freeze Dried has main keyword match:
  - Check for "keep frozen", "thaw before serving", "store frozen"
  - If NOT present → Freeze Dried wins
  - If present → Frozen wins
```

#### Rule 4: Air Dried vs Dehydrated
```
If both score similarly:
  - Check for "air dried" as main keyword match
  - If present → Air Dried wins
```

#### Rule 5: Uncooked vs Lightly Cooked
```
If heat verbs present: "gently cooked", "sous vide", "lightly cooked", "cooked"
  - AND Lightly Cooked scores ≥ 3
  - Override Uncooked → Lightly Cooked
```

---

## Processor Usage

The `ProcessingMethodProcessor` handles database operations and batch processing.

### Process Single Product

```python
from app.processors.processing_method_processor import ProcessingMethodProcessor
from app.models.database import SessionLocal

db = SessionLocal()
processor = ProcessingMethodProcessor(db)

# Process one product
processed = processor.process_single(product_detail_id=123)

print(f"Primary Method: {processed.processing_method_1}")
print(f"Secondary Method: {processed.processing_method_2}")
print(f"Reason: {processed.processing_adulteration_method_reason}")
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

### Reprocess Method

```python
# Reprocess all "Freeze Dried" products
results = processor.reprocess_method("Freeze Dried")

# Reprocess with limit
results = processor.reprocess_method("Extruded", limit=50)
```

### Statistics

```python
# Get statistics
stats = processor.get_statistics()
print(stats)
# Output:
# {
#     'Freeze Dried': 234,
#     'Extruded': 567,
#     'Uncooked (Frozen)': 89,
#     '_composite_methods': {'Uncooked (Frozen)': 45},
#     '_composite_count': 45,
#     '_total_processed': 890,
#     '_total_details': 1000,
#     '_unprocessed': 110
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
  - processing_method_1 (enum: all 11 processing methods + 'Other')
  - processing_method_2 (enum: optional, for composite methods)
  - processing_adulteration_method_reason (text)
  - processed_at (timestamp)
  - processor_version (varchar)
```

### Workflow

1. **Processor reads** from `product_details` table (6 fields)
2. **Classifier analyzes** with negation detection and scoring
3. **Processor writes** results to `processed_products` table
4. If record exists, it's updated; otherwise, a new record is created

---

## Command Line Interface (CLI)

### Using the Unified CLI

```bash
# Process all unprocessed products
python cli.py --process --processing

# Process with limit
python cli.py --process --processing --limit 100

# Process single product
python cli.py --process --processing --product-id 123

# Reprocess all products (force)
python cli.py --process --processing --force

# Reprocess specific processing method
python cli.py --process --processing --reprocess-processing "Freeze Dried"
python cli.py --process --processing --reprocess-processing "Extruded"
python cli.py --process --processing --reprocess-processing "Uncooked (Frozen)"
python cli.py --process --processing --reprocess-processing "Lightly Cooked (Not Frozen)"
python cli.py --process --processing --reprocess-processing "Baked"

# Valid processing methods for reprocessing:
# - "Uncooked (Not Frozen)"
# - "Uncooked (Flash Frozen)"
# - "Uncooked (Frozen)"
# - "Lightly Cooked (Not Frozen)"
# - "Lightly Cooked (Frozen)"
# - "Freeze Dried"
# - "Air Dried"
# - "Dehydrated"
# - "Baked"
# - "Extruded"
# - "Retorted"
# - "Other"

# Show help
python cli.py --help
```

### Direct Module Execution

```bash
# Run classifier tests
python -m app.processors.processing_method_classifier

# Run processor demo
python -m app.processors.processing_method_processor
```

---

## Examples

### Example 1: Freeze Dried Product

```python
classifier = ProcessingMethodClassifier()

result = classifier.classify(
    product_name="Primal Freeze-Dried Chicken Formula",
    specifications="Freeze-dried raw nuggets, shelf-stable",
    details="Complete freeze-dried raw dog food"
)

# Result:
# processing_method_1: Freeze Dried
# processing_method_2: None
# confidence: 1.0
# matched_keywords_1: ['freeze dried', 'freeze-dried raw', 'freeze-dried nuggets']
```

### Example 2: Raw Frozen with Composite

```python
result = classifier.classify(
    product_name="Raw Frozen Beef Patties",
    specifications="Keep frozen, raw frozen dog food",
    details="Frozen raw meals for dogs"
)

# Result:
# processing_method_1: Uncooked (Frozen)
# processing_method_2: None
# confidence: 1.0
# matched_keywords_1: ['raw', 'frozen', 'raw frozen', 'kept frozen']
```

### Example 3: Lightly Cooked Fresh (Not Frozen)

```python
result = classifier.classify(
    product_name="Gently Cooked Fresh Meals",
    specifications="Lightly cooked, never frozen, refrigerated",
    details="Fresh cooked dog food, keep refrigerated"
)

# Result:
# processing_method_1: Lightly Cooked (Not Frozen)
# processing_method_2: None
# confidence: 0.9
# matched_keywords_1: ['lightly cooked', 'gently cooked', 'never frozen (negated)', 'refrigerated']
```

### Example 4: Extruded Kibble

```python
result = classifier.classify(
    product_name="Premium Dry Kibble",
    specifications="Traditional kibble, dry food",
    details="Extruded dry dog food"
)

# Result:
# processing_method_1: Extruded
# processing_method_2: None
# confidence: 1.0
# matched_keywords_1: ['extruded', 'traditional kibble', 'kibble', 'dry food']
```

### Example 5: Retorted (Canned)

```python
result = classifier.classify(
    product_name="Classic Canned Dog Food",
    specifications="Wet food in gravy, shelf-stable",
    details="Chunks in gravy, pate style"
)

# Result:
# processing_method_1: Retorted
# processing_method_2: None
# confidence: 1.0
# matched_keywords_1: ['canned', 'wet food', 'gravy', 'pate']
```

### Example 6: Air Dried

```python
result = classifier.classify(
    product_name="Air Dried Beef Recipe",
    specifications="Gently air dried, cold air dried",
    details="Slowly air dried dog food"
)

# Result:
# processing_method_1: Air Dried
# processing_method_2: None
# confidence: 1.0
# matched_keywords_1: ['air dried', 'gently air dried', 'cold air dried']
```

### Example 7: Negation Example

```python
result = classifier.classify(
    product_name="Fresh Cooked Dog Food",
    specifications="Gently cooked, never frozen, no heat processing",
    details="Lightly cooked fresh meals"
)

# Note: "never frozen" negates frozen keywords
# "no heat processing" might conflict but lightly cooked wins
```

---

## Batch Processing Best Practices

### Reuse Classifier Instance

```python
# Good: Reuse classifier instance
classifier = ProcessingMethodClassifier()
for product in products:
    result = classifier.classify(...)

# Better: Use batch method
products = [
    {
        "product_name": "Product 1",
        "details": "...",
        "specifications": "...",
        # ... other fields
    },
    # ... more products
]
results = classifier.classify_batch(products)
```

### Database Processing

```python
from sqlalchemy.orm import Session
from app.models import ProductDetails, ProcessedProduct
from app.processors.processing_method_processor import ProcessingMethodProcessor

def classify_all_products(db: Session, limit: int = 100):
    """Classify all products that don't have processing method yet."""
    
    processor = ProcessingMethodProcessor(db)
    
    # Find products without classification
    unclassified = db.query(ProductDetails).outerjoin(
        ProcessedProduct,
        ProductDetails.id == ProcessedProduct.product_detail_id
    ).filter(
        (ProcessedProduct.id.is_(None)) |
        (ProcessedProduct.processing_method_1.is_(None))
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
python api/app/processors/processing_method_classifier.py

# Test the processor
python api/app/processors/processing_method_processor.py
```

### Custom Test Cases

```python
from app.processors.processing_method_classifier import ProcessingMethodClassifier

classifier = ProcessingMethodClassifier()

test_products = [
    ("Freeze-Dried Raw", "Freeze-dried for shelf stability", "Primal nuggets"),
    ("Raw Frozen", "Keep frozen", "Raw frozen patties"),
    ("Gently Cooked", "Lightly cooked, refrigerated", "Fresh meals"),
]

for name, specs, details in test_products:
    result = classifier.classify(
        product_name=name,
        specifications=specs,
        details=details
    )
    print(f"{name}: {result.processing_method_1.value} (confidence: {result.confidence})")
```

---

## Advanced Usage

### Negation Analysis

```python
classifier = ProcessingMethodClassifier()

# Test negation
result = classifier.classify(
    product_name="Fresh Dog Food",
    specifications="Gently cooked, never frozen, not extruded"
)

# Check matched keywords for negation markers
print("Matched keywords:")
for kw in result.matched_keywords_1:
    if "(negated)" in kw:
        print(f"  - {kw} ← NEGATED")
    else:
        print(f"  - {kw}")
```

### Composite Method Analysis

```python
result = classifier.classify(
    product_name="Lightly Cooked Frozen Meals",
    specifications="Gently cooked then frozen, thaw before serving"
)

if result.processing_method_2:
    print(f"Primary: {result.processing_method_1.value}")
    print(f"Secondary: {result.processing_method_2.value}")
    print("This is a composite (two-step) processing method")
```

### Confidence Thresholding

```python
result = classifier.classify(...)

if result.confidence >= 0.9:
    print(f"Very high confidence: {result.processing_method_1.value}")
elif result.confidence >= 0.7:
    print(f"High confidence: {result.processing_method_1.value}")
elif result.confidence >= 0.5:
    print(f"Medium confidence: {result.processing_method_1.value}")
else:
    print(f"Low confidence: {result.processing_method_1.value}")
    print("Manual review recommended")
```

---

## Troubleshooting

### Issue: Wrong Classification

**Check matched keywords:**
```python
result = classifier.classify(...)
print(f"Primary Keywords: {result.matched_keywords_1}")
if result.processing_method_2:
    print(f"Secondary Keywords: {result.matched_keywords_2}")
print(f"Reason: {result.reason}")
```

**Review input text:**
```python
combined = classifier._combine_text(
    product_name, details, more_details,
    ingredient_list, specifications, feeding_instructions
)
print(f"Combined text: {combined}")
```

### Issue: Negation Not Detected

- **Check distance**: Negation words must be within 4 tokens before keyword
- **Check text**: Ensure text is properly formatted (not broken across fields)
- **Example**: "This product is not frozen" → "not" is 1 token before "frozen" ✓

### Issue: Low Confidence

- **Cause**: Weak keyword matches (only supporting keywords, no main keywords)
- **Solution**: Check if main keywords are present, review keyword list

### Issue: Composite Method Not Detected

- **Cause**: Secondary method score < 3
- **Solution**: Verify both processing indicators are present in text

### Issue: Disambiguation Not Working

- **Check rules**: Review which disambiguation rule should apply
- **Check text**: Verify specific trigger words are present
- **Example**: For Extruded vs Baked, check for "oven-baked" or "gently baked"

---

## Keywords Reference

### Uncooked (Not Frozen)

**Main:** raw, not frozen

**Supporting:** raw, not frozen, refrigerated, ready to serve, fridge fresh, gently handled, prepared daily, fridge-stored, raw and fresh, delivered fresh, no freezing, never frozen, fresh never frozen, uncooked, fridge-kept, stored in fridge, raw refrigerated, uncooked and unfrozen, raw ready-to-eat, raw kept cold not frozen, fresh raw blend, raw uncooked blend, raw not frozen formula, raw not frozen patties, raw not frozen nuggets, raw meal no freezing, cold but not frozen, raw no freeze preservation, raw minimal processing, raw kept in refrigerator

### Uncooked (Flash Frozen)

**Main:** raw, flash frozen

**Supporting:** raw flash frozen, instantly frozen, preserved raw, rapid frozen, IQF raw, flash frozen, flash freeze, flash-frozen raw, rapidly frozen, frozen immediately, preserved by flash freezing, ultra-cold frozen, raw frozen fast, instant frozen, fresh then flash frozen, flash frozen patties, flash frozen nuggets, flash frozen raw blend, flash frozen formula, raw quick frozen, flash frozen meals, nitrogen frozen, raw sealed and flash frozen, raw fast frozen preservation, raw deep frozen, flash freeze preserved

### Uncooked (Frozen)

**Main:** raw, frozen

**Supporting:** frozen, deep frozen, freeze to preserve, frozen chubs, frozen dog food, frozen form, frozen meals, frozen nuggets, frozen packaging, frozen patties, frozen raw, frozen recipe, kept frozen, raw frozen, ships frozen, store frozen, human-grade raw meals, uncooked, not cooked, raw frozen dog food, raw kept frozen, stored frozen, frozen patties, raw frozen blend, raw frozen meal, raw and frozen, frozen meat mix, frozen formula, frozen fresh raw, stay frozen, raw in freezer, freezer-stored raw, frozen raw mix, raw frozen medallions, frozen whole prey, frozen bones and meat

### Lightly Cooked (Not Frozen)

**Main:** fresh food, lightly cooked, not frozen

**Supporting:** fresh food, lightly cooked, gently cooked, gently prepared, slow cooked, sous vide, flash cooked, lightly steamed, partially cooked, gently blanched, keep refrigerated, fresh never frozen, refrigerated, ready to serve, fridge fresh, fridge-stored, delivered fresh, no freezing, minimally cooked, small batch cooked, cooked fresh, home cooked, just cooked, prepared fresh, cooked meals, fridge cooked meals, cooked not frozen, ready-to-serve cooked, fridge-ready meals, lightly simmered, cooked and refrigerated, real cooked food, cooked daily, heat-prepared meals

### Lightly Cooked (Frozen)

**Main:** fresh food, lightly cooked, frozen

**Supporting:** fresh food, frozen lightly cooked, lightly cooked, gently cooked, gently prepared, slow cooked, sous vide, flash cooked, lightly steamed, partially cooked, gently blanched, fresh-frozen, frozen fresh, kept frozen, ships frozen, frozen meals, cooked then frozen, cooked and frozen, frozen cooked meals, frozen gently prepared, small batch cooked and frozen, frozen dog entrees, frozen fresh-cooked, cooked frozen food, frozen homemade meals, cooked frozen recipes, slow-cooked and frozen, minimally cooked and frozen, thaw before serving

### Freeze Dried

**Main:** freeze dried

**Supporting:** freeze dried, freeze dried nuggets, primal freeze dried, freeze-dried, freeze-dried nuggets, freeze-dried raw, freeze-dried meal, freeze-dried patties, freeze-dried bites, freeze-dried toppers, freeze-dried formula, freeze-dried dog food, freeze-dried treats, freeze-dried beef, freeze-dried chicken, freeze-dried nuggets for dogs, freeze-dried complete meal, freeze-dried whole food, raw freeze-dried, shelf-stable raw, raw preserved through freeze drying, primal nuggets, freeze-dried complete and balanced, freeze-dried blend, freeze-dried entrée, freeze-dried lamb formula, freeze-dried raw diet, shelf-stable freeze-dried

### Air Dried

**Main:** air dried

**Supporting:** air dried, cold dried, air-dried raw, gently air dried, sun dried, wind dried, low-temperature dried, gently dried, slow dried, cold-air dried, fresh dried, slow air dried, air dried nuggets, air dried bites, air dried recipes, low heat dried, nutrient-rich air dried, air dehydrated, handcrafted air dried, natural air dried, artisan air dried, air-dried food, air dried patties

### Dehydrated

**Main:** dehydrated

**Supporting:** dehydrated, gently dehydrated, slow dehydrated, dried raw, raw dehydrated, dehydrated dog food, dehydrated meals, dehydrated patties, dehydrated recipes, rehydrate with water, dry mix formula, add water to serve, warm water preparation, shelf-stable dehydrated, dry pre-mix, dehydrated whole foods, dehydrated base mix

### Baked

**Main:** baked

**Supporting:** baked, oven baked, gently baked, slow baked, low-temp baked, baked kibble, oven roasted, handcrafted baked, artisan baked, small batch baked, baked dry food, air baked, dry baked, baked recipe, baked formula, crunchy bites, dry oven-cooked, lightly baked, oven-baked dog food, baked in small batches, slow-cooked in oven, crunchy baked bites

### Extruded

**Main:** extruded

**Supporting:** extruded, traditional kibble, cold-pressed kibble, pellet kibble, crunchy kibble, high heat processed, standard kibble, oven-extruded, expanded kibble, steam extruded, heat extruded, high-temp kibble, processed kibble, machine-processed kibble, dry expanded pet food, typical kibble, mass-produced kibble, kibble, dry food, dry kibble, crunchy bites, dry formula, premium dry, grain-free kibble, extruded kibble, high-pressure extrusion, extruded dry food, puffed kibble, commercial kibble, hot extruded, dry extruded, extruded pet food

### Retorted

**Main:** retorted, wet food

**Supporting:** canned food, high heat sterilized, shelf-stable wet, thermally processed, pressure cooked, canned, wet food, slow-cooked in gravy, shelf-stable pouch, stew-like consistency, gently cooked and sealed, cooked in the can, retort pouch, cooked for safety, moisture rich food, moist food, stewed, loaf, pate, broth, gravy, chunk in gravy, shredded in broth, homestyle stew, meat chunks in jelly, pouch food, pull-tab can, shelf-stable wet food, slow cooked, canned entrée, meat loaf style, toppers in gravy, wet entree, classic canned dog food, retort processed, canned dog food, wet food in can, sealed can, cooked in can, moist food in can

---

## Summary

The Processing Method Classifier provides:

✅ **11 processing method categories** with clear definitions  
✅ **Multi-field analysis** across 6 product data fields  
✅ **Keyword-based matching** with advanced scoring (+5, +2 points)  
✅ **Negation detection** with penalty scoring (-3, -1 points)  
✅ **Composite method detection** for two-step processing  
✅ **Disambiguation rules** for conflicting methods  
✅ **Database integration** for automated processing  
✅ **Batch processing** for efficiency  
✅ **Statistics tracking** with composite method counts  

**Use Cases:**
- Classify new products as they're scraped
- Reprocess existing products after keyword/logic updates
- Generate processing method reports
- Filter products by processing type
- Monitor processing method distribution
- Detect multi-step processing (composite methods)
- Handle negation in product descriptions

**Technical Highlights:**
- Minimum threshold: score ≥ 3 OR main keyword match
- Negation window: 0-4 tokens before keyword
- Confidence calculation: Based on score and non-negated matches
- Terminal processes: Cannot be composite methods
- Source trust ranking: Higher-trust sources prioritized in tie-breaking

For questions or issues, refer to the test examples in the classifier and processor modules.