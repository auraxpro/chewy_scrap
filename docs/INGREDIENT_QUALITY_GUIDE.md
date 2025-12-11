# Ingredient Quality Classifier Guide

## Overview

The **Ingredient Quality Classifier** analyzes dog food product ingredients and classifies them into categories (Protein, Fat, Carbohydrates, Fiber) with quality ratings (High, Good, Moderate, Low). It also identifies Dirty Dozen ingredients and Synthetic Nutrition additions.

**Classification Categories:**
- **Protein** - Meat, poultry, fish, and plant-based proteins
- **Fat** - Oils and fats from various sources
- **Carbohydrates** - Grains, vegetables, and starches
- **Fiber** - Fiber sources from various ingredients

**Quality Ratings:**
- `High` - Premium quality ingredients (e.g., organic whole meat, wild-caught fish)
- `Good` - Good quality ingredients (e.g., whole meat, brown rice)
- `Moderate` - Moderate quality ingredients (e.g., white rice, potatoes)
- `Low` - Low quality ingredients (e.g., by-products, corn gluten meal)

**Additional Classifications:**
- **Dirty Dozen** - 12 problematic ingredients (BHA, BHT, Ethoxyquin, Propylene Glycol, Artificial Colors, Corn, Wheat, Soy, By-products, Animal Digest, Rendered Fat, Sugar)
- **Synthetic Nutrition** - Synthetic vitamins, amino acids, and minerals

## Key Features

### 1. Ingredient Parsing
- Splits ingredients by comma
- Normalizes text (lowercase, clean whitespace)
- Handles variations in formatting

### 2. Multi-Category Classification
Each ingredient is classified into one of four categories:
- **Protein** - Animal and plant proteins
- **Fat** - Oils and fats
- **Carbohydrates** - Grains and starches
- **Fiber** - Fiber sources

### 3. Quality Rating Within Categories
Within each category, ingredients are rated:
- **High** - Premium quality (organic, wild-caught, etc.)
- **Good** - Good quality (whole ingredients, named cuts)
- **Moderate** - Moderate quality (basic ingredients)
- **Low** - Low quality (by-products, meals, unspecified)

### 4. Dirty Dozen Detection
Identifies 12 problematic ingredients:
1. BHA (Butylated Hydroxyanisole)
2. BHT (Butylated Hydroxytoluene)
3. Ethoxyquin
4. Propylene Glycol
5. Artificial Colors
6. Corn
7. Wheat
8. Soy
9. By-products
10. Animal Digest
11. Rendered Fat
12. Sugar

### 5. Synthetic Nutrition Detection
Identifies synthetic additions:
- **Synthetic Vitamins** - Vitamin A, B, C, D, E, K supplements
- **Synthetic Amino Acids** - L-Lysine, DL-Methionine, etc.
- **Synthetic Minerals** - Zinc Oxide, Calcium Carbonate, etc.

### 6. Quality Class Determination (Weighted Deduction)
Determines overall quality class for each category using a weighted deduction formula:

**Weighted Deduction Formula:**
```
Weighted Deduction = (count_high × 0 + count_good × 2 + count_moderate × 3 + count_low × 5) / total_ingredients
```

**Tier Point Values:**
- High Quality: 0 points
- Good Quality: 2 points
- Moderate Quality: 3 points
- Low Quality: 5 points

**Tier Thresholds (After Weighted Average):**
- 0.00 - 1.00 → `High` (0 pts deduction)
- 1.01 - 2.00 → `Good` (-2 pts deduction)
- 2.01 - 3.50 → `Moderate` (-3 pts deduction)
- 3.51+ → `Low` (-5 pts deduction)

**Example:**
- 2 High ingredients (2 × 0 = 0)
- 2 Good ingredients (2 × 2 = 4)
- 3 Moderate ingredients (3 × 3 = 9)
- 3 Low ingredients (3 × 5 = 15)
- Total: 10 ingredients
- Weighted Average: (0 + 4 + 9 + 15) / 10 = 2.8
- Result: 2.8 falls in 2.01-3.50 range → `Moderate` quality class

---

## Quick Start

### Basic Usage

```python
from app.processors.ingredient_quality_classifier import (
    IngredientQualityClassifier,
    classify_ingredient_quality,
)

# Method 1: Using convenience function
result = classify_ingredient_quality(
    ingredients="Organic chicken, organic beef, wild-caught salmon, sweet potatoes, carrots, flaxseed oil"
)

print(f"Protein Quality: {result.protein_quality_class.value}")
print(f"Fat Quality: {result.fat_quality_class.value}")
print(f"Carb Quality: {result.carb_quality_class.value}")
print(f"Fiber Quality: {result.fiber_quality_class.value}")
print(f"Dirty Dozen Count: {result.dirty_dozen_ingredients_count}")
print(f"Synthetic Nutrition Count: {result.synthetic_nutrition_addition_count}")

# Method 2: Using classifier instance (recommended for batch processing)
classifier = IngredientQualityClassifier()

result = classifier.classify(
    ingredients="Chicken meal, brown rice, chicken fat, corn gluten meal, BHA, artificial colors"
)
```

### Classification Result

The `IngredientQualityResult` object contains:

```python
@dataclass
class IngredientQualityResult:
    # All ingredients
    ingredients_all: str
    
    # Protein results
    protein_ingredients_all: str
    protein_ingredients_high: List[str]
    protein_ingredients_good: List[str]
    protein_ingredients_moderate: List[str]
    protein_ingredients_low: List[str]
    protein_ingredients_other: List[str]
    protein_quality_class: QualityClass
    
    # Fat results
    fat_ingredients_all: str
    fat_ingredients_high: List[str]
    fat_ingredients_good: List[str]
    fat_ingredients_moderate: List[str]
    fat_ingredients_low: List[str]
    fat_ingredients_other: List[str]
    fat_quality_class: QualityClass
    
    # Carb results
    carb_ingredients_all: str
    carb_ingredients_high: List[str]
    carb_ingredients_good: List[str]
    carb_ingredients_moderate: List[str]
    carb_ingredients_low: List[str]
    carb_ingredients_other: List[str]
    carb_quality_class: QualityClass
    
    # Fiber results
    fiber_ingredients_all: str
    fiber_ingredients_high: List[str]
    fiber_ingredients_good: List[str]
    fiber_ingredients_moderate: List[str]
    fiber_ingredients_low: List[str]
    fiber_ingredients_other: List[str]
    fiber_quality_class: QualityClass
    
    # Dirty Dozen
    dirty_dozen_ingredients: List[str]
    dirty_dozen_ingredients_count: int
    
    # Synthetic Nutrition
    synthetic_nutrition_addition: List[str]
    synthetic_nutrition_addition_count: int
```

**Example Output:**
```
protein_quality_class: High
protein_ingredients_high: ['Organic chicken', 'Organic beef', 'Wild-caught salmon']
protein_ingredients_good: []
protein_ingredients_moderate: []
protein_ingredients_low: []
fat_quality_class: Good
fat_ingredients_high: []
fat_ingredients_good: ['Flaxseed oil']
carb_quality_class: High
carb_ingredients_high: ['Sweet potatoes']
dirty_dozen_ingredients_count: 0
synthetic_nutrition_addition_count: 0
```

---

## Classifier Details

### Classification Logic

1. **Split ingredients** by comma
2. **Normalize each ingredient** (lowercase, clean whitespace)
3. **Classify each ingredient** into category and quality:
   - Check Protein keywords (High → Good → Moderate → Low)
   - If not found, check Fat keywords
   - If not found, check Carb keywords
   - If not found, check Fiber keywords
   - If not found, mark as "Other" category
4. **Group ingredients** by category
5. **Determine quality class** for each category
6. **Identify Dirty Dozen** ingredients
7. **Identify Synthetic Nutrition** additions

### Keyword Matching Strategy

**Main Keywords** (highest priority):
- Exact phrase match for multi-word keywords
- Word boundary match for single-word keywords

**Supporting Keywords**:
- Multi-word phrase: Exact phrase match
- Single word: Word boundary match

### Quality Class Determination (Weighted Deduction)

For each category, the overall quality class is determined using a weighted deduction system:

1. **Count ingredients** in each quality tier (High, Good, Moderate, Low)
2. **Calculate weighted average**:
   ```
   Weighted Avg = (count_high × 0 + count_good × 2 + count_moderate × 3 + count_low × 5) / total_ingredients
   ```
3. **Map to quality tier** based on thresholds:
   - 0.00 - 1.00 → `High`
   - 1.01 - 2.00 → `Good`
   - 2.01 - 3.50 → `Moderate`
   - 3.51+ → `Low`

This weighted approach ensures that mixed-quality ingredient groups are properly evaluated rather than using simple majority rules.

---

## Processor Usage

The `IngredientQualityProcessor` handles database operations and batch processing.

### Process Single Product

```python
from app.processors.ingredient_quality_processor import IngredientQualityProcessor
from app.models.database import SessionLocal

db = SessionLocal()
processor = IngredientQualityProcessor(db)

# Process one product
processed = processor.process_single(product_detail_id=123)

print(f"Protein Quality: {processed.protein_quality_class}")
print(f"Fat Quality: {processed.fat_quality_class}")
print(f"Carb Quality: {processed.carb_quality_class}")
print(f"Fiber Quality: {processed.fiber_quality_class}")
print(f"Dirty Dozen Count: {processed.dirty_dozen_ingredients_count}")
print(f"Synthetic Nutrition Count: {processed.synthetic_nutrition_addition_count}")
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

### Reprocess Quality Class

```python
# Reprocess all "High" quality products
results = processor.reprocess_quality_class("High")

# Reprocess with limit
results = processor.reprocess_quality_class("Good", limit=50)
```

### Statistics

```python
# Get statistics
stats = processor.get_statistics()
print(stats)
# Output:
# {
#     'protein_quality': {'High': 45, 'Good': 123, 'Moderate': 67, 'Low': 34},
#     'fat_quality': {'High': 12, 'Good': 89, 'Low': 156},
#     'carb_quality': {'High': 78, 'Good': 134, 'Moderate': 45, 'Low': 23},
#     'fiber_quality': {'High': 56, 'Good': 98, 'Moderate': 67, 'Low': 12},
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

The processor updates the `processed_products` table with the following fields:

**All Ingredients:**
- `ingredients_all` (TEXT) - All ingredients as comma-separated string

**Protein Fields:**
- `protein_ingredients_all` (TEXT) - All protein ingredients
- `protein_ingredients_high` (INTEGER) - Count of high quality proteins
- `protein_ingredients_good` (INTEGER) - Count of good quality proteins
- `protein_ingredients_moderate` (INTEGER) - Count of moderate quality proteins
- `protein_ingredients_low` (INTEGER) - Count of low quality proteins
- `protein_ingredients_other` (TEXT) - Undetected protein ingredients
- `protein_quality_class` (ENUM: High/Good/Moderate/Low)

**Fat Fields:**
- `fat_ingredients_all` (TEXT) - All fat ingredients
- `fat_ingredients_high` (INTEGER) - Count of high quality fats
- `fat_ingredients_good` (INTEGER) - Count of good quality fats
- `fat_ingredients_low` (INTEGER) - Count of low quality fats
- `fat_ingredients_other` (TEXT) - Undetected fat ingredients
- `fat_quality_class` (ENUM: High/Good/Low) - Note: Fat has no Moderate level

**Carb Fields:**
- `carb_ingredients_all` (TEXT) - All carb ingredients
- `carb_ingredients_high` (INTEGER) - Count of high quality carbs
- `carb_ingredients_good` (INTEGER) - Count of good quality carbs
- `carb_ingredients_moderate` (INTEGER) - Count of moderate quality carbs
- `carb_ingredients_low` (INTEGER) - Count of low quality carbs
- `carb_ingredients_other` (TEXT) - Undetected carb ingredients
- `carb_quality_class` (ENUM: High/Good/Moderate/Low)

**Fiber Fields:**
- `fiber_ingredients_all` (TEXT) - All fiber ingredients
- `fiber_ingredients_high` (INTEGER) - Count of high quality fiber
- `fiber_ingredients_good` (INTEGER) - Count of good quality fiber
- `fiber_ingredients_moderate` (INTEGER) - Count of moderate quality fiber
- `fiber_ingredients_low` (INTEGER) - Count of low quality fiber
- `fiber_ingredients_other` (TEXT) - Undetected fiber ingredients
- `fiber_quality_class` (ENUM: High/Good/Moderate/Low)

**Dirty Dozen:**
- `dirty_dozen_ingredients` (TEXT) - Comma-separated list of dirty dozen ingredients found
- `dirty_dozen_ingredients_count` (INTEGER) - Count of dirty dozen ingredients

**Synthetic Nutrition:**
- `synthetic_nutrition_addition` (TEXT) - Comma-separated list of synthetic nutrition additions
- `synthetic_nutrition_addition_count` (INTEGER) - Count of synthetic nutrition additions

### Workflow

1. **Processor reads** from `product_details.ingredients` field
2. **Classifier analyzes** the ingredient list
3. **Processor writes** results to `processed_products` table
4. If record exists, it's updated; otherwise, a new record is created

---

## Command Line Interface (CLI)

### Using the Unified CLI

The main CLI tool provides easy access to ingredient quality processing:

```bash
# Process all unprocessed products
python cli.py --process --ingredient-quality

# Process with limit
python cli.py --process --ingredient-quality --limit 100

# Process single product
python cli.py --process --ingredient-quality --product-id 123

# Reprocess all products (force)
python cli.py --process --ingredient-quality --force

# Reprocess specific quality class
python cli.py --process --ingredient-quality --reprocess-quality "High"
python cli.py --process --ingredient-quality --reprocess-quality "Good"
python cli.py --process --ingredient-quality --reprocess-quality "Moderate"
python cli.py --process --ingredient-quality --reprocess-quality "Low"

# Show help
python cli.py --help
```

### Using the Standalone Script

Use the standalone script for more options:

```bash
# Process all unprocessed products
python scripts/process_ingredient_quality.py

# Process with limit
python scripts/process_ingredient_quality.py --limit 100

# Reprocess all products
python scripts/process_ingredient_quality.py --reprocess

# Reprocess specific quality class
python scripts/process_ingredient_quality.py --reprocess-quality "High"

# Show statistics only
python scripts/process_ingredient_quality.py --stats-only

# Test mode (no database changes)
python scripts/process_ingredient_quality.py --test
```

### Direct Module Execution

```bash
# Run classifier tests
python -m app.processors.ingredient_quality_classifier

# Run processor demo
python -m app.processors.ingredient_quality_processor
```

---

## Examples

### Example 1: High Quality Product

```python
classifier = IngredientQualityClassifier()

result = classifier.classify(
    ingredients="Organic chicken, organic beef, wild-caught salmon, organic sweet potatoes, organic carrots, flaxseed oil"
)

# Result:
# protein_quality_class: High
# protein_ingredients_high: ['Organic chicken', 'Organic beef', 'Wild-caught salmon']
# fat_quality_class: Good
# fat_ingredients_good: ['Flaxseed oil']
# carb_quality_class: High
# carb_ingredients_high: ['Organic sweet potatoes']
# fiber_quality_class: High
# fiber_ingredients_high: ['Organic carrots']
# dirty_dozen_ingredients_count: 0
# synthetic_nutrition_addition_count: 0
```

### Example 2: Mixed Quality Product (Weighted Deduction)

```python
result = classifier.classify(
    ingredients="Chicken meal, brown rice, chicken fat, corn gluten meal, wheat flour, BHA, artificial colors"
)

# Protein Analysis:
# - 1 Low ingredient (chicken meal)
# Weighted Avg = (0×0 + 0×2 + 0×3 + 1×5) / 1 = 5.0
# 5.0 > 3.50 → Low quality class

# Fat Analysis:
# - 1 Good ingredient (chicken fat)
# Weighted Avg = (0×0 + 1×2 + 0×3 + 0×5) / 1 = 2.0
# 2.0 falls in 1.01-2.00 → Good quality class

# Carb Analysis:
# - 1 Good ingredient (brown rice)
# - 2 Low ingredients (corn gluten meal, wheat flour)
# Weighted Avg = (0×0 + 1×2 + 0×3 + 2×5) / 3 = 12/3 = 4.0
# 4.0 > 3.50 → Low quality class

# Result:
# protein_quality_class: Low
# protein_ingredients_low: ['Chicken meal']
# fat_quality_class: Good
# fat_ingredients_good: ['Chicken fat']
# carb_quality_class: Low
# carb_ingredients_good: ['Brown rice']
# carb_ingredients_low: ['Corn gluten meal', 'Wheat flour']
# dirty_dozen_ingredients_count: 4
# dirty_dozen_ingredients: ['Corn gluten meal', 'Wheat flour', 'BHA', 'Artificial colors']
# synthetic_nutrition_addition_count: 0
```

### Example 2b: Mixed Quality with Weighted Calculation

```python
# Example matching the weighted deduction formula:
# Ingredients: 2 High, 2 Good, 3 Moderate, 3 Low

result = classifier.classify(
    ingredients="Organic chicken, organic beef, chicken breast, salmon fillet, white rice, potatoes, potato starch, chicken meal, meat by-products, animal digest"
)

# Protein Analysis (assuming classification):
# - 2 High (organic chicken, organic beef)
# - 2 Good (chicken breast, salmon fillet)
# - 0 Moderate
# - 2 Low (chicken meal, meat by-products, animal digest)
# Weighted Avg = (2×0 + 2×2 + 0×3 + 3×5) / 7 = (0 + 4 + 0 + 15) / 7 = 19/7 = 2.71
# 2.71 falls in 2.01-3.50 → Moderate quality class

# This demonstrates how mixed quality ingredients result in a weighted average
# rather than simple majority rule
```

### Example 3: Low Quality Product

```python
result = classifier.classify(
    ingredients="Meat by-products, corn, wheat, soybean meal, animal digest, rendered fat, BHT, propylene glycol"
)

# Result:
# protein_quality_class: Low
# protein_ingredients_low: ['Meat by-products', 'Animal digest']
# fat_quality_class: Low
# fat_ingredients_low: ['Rendered fat']
# carb_quality_class: Low
# carb_ingredients_low: ['Corn', 'Wheat', 'Soybean meal']
# dirty_dozen_ingredients_count: 7
# dirty_dozen_ingredients: ['Corn', 'Wheat', 'Soybean meal', 'Meat by-products', 'Animal digest', 'Rendered fat', 'BHT']
# synthetic_nutrition_addition_count: 0
```

### Example 4: Product with Synthetic Nutrition

```python
result = classifier.classify(
    ingredients="Chicken breast, brown rice, salmon oil, sweet potatoes, Vitamin A Supplement, Zinc Oxide, Calcium Carbonate"
)

# Result:
# protein_quality_class: Good
# protein_ingredients_good: ['Chicken breast']
# fat_quality_class: High
# fat_ingredients_high: ['Salmon oil']
# carb_quality_class: High
# carb_ingredients_high: ['Sweet potatoes']
# carb_ingredients_good: ['Brown rice']
# dirty_dozen_ingredients_count: 0
# synthetic_nutrition_addition_count: 3
# synthetic_nutrition_addition: ['Vitamin A Supplement', 'Zinc Oxide', 'Calcium Carbonate']
```

### Example 5: Empty or Missing Ingredients

```python
result = classifier.classify(ingredients=None)
# or
result = classifier.classify(ingredients="")

# Result:
# All quality classes default to Moderate
# All counts are 0
# All ingredient lists are empty
```

---

## Batch Processing Best Practices

### Reuse Classifier Instance

```python
# Good: Reuse classifier instance
classifier = IngredientQualityClassifier()
for product in products:
    result = classifier.classify(product.ingredients)
```

### Database Processing

```python
from sqlalchemy.orm import Session
from app.models import ProductDetails, ProcessedProduct
from app.processors.ingredient_quality_processor import IngredientQualityProcessor

def classify_all_products(db: Session, limit: int = 100):
    """Classify all products that don't have ingredient quality yet."""
    
    processor = IngredientQualityProcessor(db)
    
    # Find products without classification
    unclassified = db.query(ProductDetails).outerjoin(
        ProcessedProduct,
        ProductDetails.id == ProcessedProduct.product_detail_id
    ).filter(
        (ProcessedProduct.id.is_(None)) |
        (ProcessedProduct.ingredients_all.is_(None))
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

```bash
# Test the classifier
python scripts/process_ingredient_quality.py --test

# Test the processor (no database changes)
python scripts/process_ingredient_quality.py --test
```

### Custom Test Cases

```python
from app.processors.ingredient_quality_classifier import IngredientQualityClassifier

classifier = IngredientQualityClassifier()

test_ingredients = [
    "Organic chicken, organic beef, wild-caught salmon",
    "Chicken meal, brown rice, chicken fat",
    "Meat by-products, corn, wheat, BHA",
    "Chicken breast, salmon oil, sweet potatoes, Vitamin A Supplement",
]

for ingredients in test_ingredients:
    result = classifier.classify(ingredients)
    print(f"\nIngredients: {ingredients}")
    print(f"Protein: {result.protein_quality_class.value}")
    print(f"Fat: {result.fat_quality_class.value}")
    print(f"Carb: {result.carb_quality_class.value}")
    print(f"Fiber: {result.fiber_quality_class.value}")
    print(f"Dirty Dozen: {result.dirty_dozen_ingredients_count}")
    print(f"Synthetic Nutrition: {result.synthetic_nutrition_addition_count}")
```

---

## Advanced Usage

### Analyzing Ingredient Lists

```python
result = classifier.classify(ingredients)

print(f"Total Ingredients: {len(result.ingredients_all.split(', '))}")
print(f"\nProtein Ingredients ({result.protein_quality_class.value}):")
print(f"  High: {len(result.protein_ingredients_high)}")
print(f"  Good: {len(result.protein_ingredients_good)}")
print(f"  Moderate: {len(result.protein_ingredients_moderate)}")
print(f"  Low: {len(result.protein_ingredients_low)}")
print(f"  Other: {len(result.protein_ingredients_other)}")

if result.dirty_dozen_ingredients:
    print(f"\nDirty Dozen Found ({result.dirty_dozen_ingredients_count}):")
    for ingredient in result.dirty_dozen_ingredients:
        print(f"  - {ingredient}")

if result.synthetic_nutrition_addition:
    print(f"\nSynthetic Nutrition ({result.synthetic_nutrition_addition_count}):")
    for addition in result.synthetic_nutrition_addition:
        print(f"  - {addition}")
```

### Text Normalization

```python
classifier = IngredientQualityClassifier()

# Access internal normalization method
text = "Organic Chicken, Wild-Caught Salmon, Sweet Potatoes"
normalized = classifier._normalize_text(text)
print(f"Original: {text}")
print(f"Normalized: {normalized}")
# Output: "organic chicken wild caught salmon sweet potatoes"
```

---

## Troubleshooting

### Issue: Ingredients Not Classified

**Check ingredient format:**
```python
result = classifier.classify(ingredients)
print(f"All ingredients: {result.ingredients_all}")
print(f"Protein ingredients: {result.protein_ingredients_all}")
print(f"Fat ingredients: {result.fat_ingredients_all}")
```

**Review normalization:**
```python
classifier = IngredientQualityClassifier()
normalized = classifier._normalize_text("Organic Chicken, Wild-Caught Salmon")
print(f"Normalized: {normalized}")
```

### Issue: Wrong Quality Classification

**Check matched keywords:**
- Review the keyword lists in the classifier
- Verify ingredient spelling and variations
- Check if ingredient matches multiple categories (first match wins)

### Issue: Dirty Dozen Not Detected

- Verify ingredient names match keyword patterns exactly
- Check for variations (e.g., "BHA" vs "Butylated Hydroxyanisole")
- Review the dirty dozen keyword lists

### Issue: Performance Concerns

- **Use batch processing** for large datasets
- **Reuse classifier instance** instead of creating new ones
- **Process in chunks** with limits
- **Use database indexes** on frequently queried fields

---

## API Integration

### Convenience Function

```python
from app.processors.ingredient_quality_processor import process_ingredient_quality
from app.models.database import SessionLocal

db = SessionLocal()

# Process all
results = process_ingredient_quality(db)

# Process specific IDs
results = process_ingredient_quality(db, product_detail_ids=[1, 2, 3])

# Process with options
results = process_ingredient_quality(
    db,
    limit=100,
    skip_existing=True
)
```

---

## Version Information

**Current Version**: v1.0.0

**Features**:
- Multi-category classification (Protein, Fat, Carb, Fiber)
- Quality rating within each category (High/Good/Moderate/Low)
- Dirty Dozen ingredient detection (12 categories)
- Synthetic Nutrition detection (Vitamins, Amino Acids, Minerals)
- Batch processing support
- Database integration with processed_products table
- Comprehensive statistics tracking

---

## Keywords Reference

### Protein Quality Keywords

**High Quality:**
- Main: organic whole meat, organic fresh meat, organic raw meat, wild-caught, wild caught, line caught
- Supporting: organic chicken, organic beef, organic lamb, USDA organic chicken, certified organic meat, etc.

**Good Quality:**
- Main: whole meat, fresh meat, raw meat, human grade meat, pasture-raised chicken, grass-fed beef
- Supporting: chicken breast, beef sirloin, salmon fillet, beef liver, pasture-raised pork, etc.

**Moderate Quality:**
- Main: whole meat, meat, raw meat, chicken, beef, lamb, fish meat
- Supporting: chicken, turkey, duck, beef, lamb, pork, salmon, whitefish, etc.

**Low Quality:**
- Main: by-products, meat meals, animal digest, rendered proteins, plant based protein
- Supporting: meat by-products, poultry by-products, chicken meal, animal digest, soy protein isolate, etc.

### Fat Quality Keywords

**High Quality:**
- Main: fish oil, salmon oil, krill oil, duck fat
- Supporting: chicken fat, duck fat, lamb fat, salmon oil, fish oil, krill oil, etc.

**Good Quality:**
- Main: flaxseed oil, avocado oil, plant oils, olive oil
- Supporting: avocado oil, chia seed oil, coconut oil, flaxseed oil, hemp seed oil, etc.

**Low Quality:**
- Main: seed oils, low-quality fats, by-product fats, rendered fats, hydrogenated oils, trans fats
- Supporting: sunflower oil, canola oil, vegetable oils, soybean oil, palm oil, rendered fat, etc.

### Carbohydrate Quality Keywords

**High Quality:**
- Main: sweet potatoes, pumpkin, butternut squash, lentils, garbanzo beans, green beans, carrots
- Supporting: sweet potatoes, pumpkin, butternut squash, lentils, garbanzo beans, etc.

**Good Quality:**
- Main: oats, quinoa, brown rice, barley, millet, amaranth, rye, buckwheat
- Supporting: oats, quinoa, brown rice, barley, millet, whole grain oats, etc.

**Moderate Quality:**
- Main: white rice, potatoes, potato starch, sweet potato flour, rice flour, tapioca
- Supporting: white rice, potatoes, potato starch, rice flour, tapioca, etc.

**Low Quality:**
- Main: corn, cornmeal, corn gluten meal, wheat, wheat flour, wheat gluten meal
- Supporting: corn, cornmeal, wheat, wheat flour, soy grits, rice bran, brewer's rice, etc.

### Fiber Quality Keywords

**High Quality:**
- Main: pumpkin, flaxseed, chia seed, psyllium husk, beet greens, kale, spinach, alfalfa
- Supporting: pumpkin, flaxseed, chia seed, psyllium husk, kale, spinach, etc.

**Good Quality:**
- Main: beet pulp, sweet potatoes, peas, lentils, garbanzo beans, tomato pomace
- Supporting: beet pulp, sweet potatoes, peas, lentils, tomato pomace, FOS, etc.

**Moderate Quality:**
- Main: cellulose, rice bran, oat hulls, peanut hulls, wheat bran, soy hulls
- Supporting: cellulose, rice bran, oat hulls, wheat bran, powdered cellulose, etc.

**Low Quality:**
- Main: soybean hulls, corn fiber, wheat fiber, peanut skins, hull fiber
- Supporting: soybean hulls, corn fiber, wheat fiber, peanut shells, grain hulls, etc.

### Dirty Dozen Keywords

1. **BHA** - BHA, Butylated Hydroxyanisole, BHA preservative
2. **BHT** - BHT, Butylated Hydroxytoluene, BHT preservative
3. **Ethoxyquin** - Ethoxyquin, Ethoxyquin preservative
4. **Propylene Glycol** - Propylene Glycol, Propylene Glycol preservative
5. **Artificial Colors** - Artificial colors, Red 40, Yellow 5, Blue 1, etc.
6. **Corn** - Corn, Ground corn, Cornmeal, Corn gluten meal
7. **Wheat** - Wheat, Wheat flour, Whole grain wheat, Wheat bran
8. **Soy** - Soy, Soybeans, Soy protein, Soy flour
9. **By-products** - Animal by-products, Poultry by-products, Meat by-products
10. **Animal Digest** - Animal digest, Meat digest, Poultry digest
11. **Rendered Fat** - Rendered fat, Animal fat, Poultry fat
12. **Sugar** - Sugar, Corn syrup, Cane sugar, High fructose corn syrup

### Synthetic Nutrition Keywords

**Synthetic Vitamins:**
- Vitamin A, B, C, D, E, K supplements
- Retinyl palmitate, Ascorbic acid, Cholecalciferol, etc.

**Synthetic Amino Acids:**
- L-Lysine, DL-Methionine, L-Threonine, L-Carnitine, etc.

**Synthetic Minerals:**
- Zinc Oxide, Calcium Carbonate, Ferrous Sulfate, Magnesium Oxide, etc.

---

## Summary

The Ingredient Quality Classifier provides:

✅ **4 ingredient categories** (Protein, Fat, Carb, Fiber)  
✅ **4 quality ratings** per category (High, Good, Moderate, Low)  
✅ **Dirty Dozen detection** (12 problematic ingredients)  
✅ **Synthetic Nutrition detection** (Vitamins, Amino Acids, Minerals)  
✅ **Comprehensive ingredient analysis** with counts and lists  
✅ **Database integration** for automated processing  
✅ **Batch processing** for efficiency  
✅ **Statistics tracking** for monitoring  

**Use Cases:**
- Classify ingredients as products are scraped
- Analyze ingredient quality across product lines
- Identify products with Dirty Dozen ingredients
- Track synthetic nutrition additions
- Generate ingredient quality reports
- Filter products by ingredient quality
- Monitor ingredient quality distribution

For questions or issues, refer to the test examples in the classifier and processor modules.

