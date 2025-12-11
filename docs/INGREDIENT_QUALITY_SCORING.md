# Ingredient Quality Scoring System

## Overview

The Ingredient Quality Scoring System calculates scores for dog food products based on weighted deduction formulas applied to four macro ingredient groups: Protein, Fat, Carbohydrates, and Fiber.

## Scoring Formula

### Weighted Deduction Calculation

For each macro group (Protein, Fat, Carb, Fiber), the system calculates a weighted deduction:

```
Weighted Deduction = (Σ (Ingredient Count × Tier Point Value)) / Total Ingredients
```

Where:
- **Ingredient Count** = number of ingredients in that quality tier
- **Tier Point Value** = tier point value (High=0, Good=2, Moderate=3, Low=5)
- **Total Ingredients** = total number of ingredients in that macro category

### Tier Point Values

| Quality Tier | Tier Point Value | Final Deduction |
|--------------|------------------|-----------------|
| High Quality | 0                | 0 pts           |
| Good Quality | 2                | -2 pts          |
| Moderate Quality | 3            | -3 pts          |
| Low Quality  | 5                | -5 pts          |

### Tier Thresholds

After calculating the weighted average, the system maps it to a final tier:

| Weighted Avg Score | Final Tier | Final Deduction |
|-------------------|------------|-----------------|
| 0.00 – 1.00       | High       | 0 pts           |
| 1.01 – 2.00       | Good       | -2 pts          |
| 2.01 – 3.50       | Moderate   | -3 pts          |
| 3.51+             | Low        | -5 pts          |

### Final Score Calculation

The final ingredient quality score is calculated as:

```
Final Score = Base Score - Average Deduction
```

Where:
- **Base Score** = 100.0 (starting point)
- **Average Deduction** = average of deductions from all four macro groups

## Example Calculation

### Example Product

A dog food contains:
- **Protein**: 2 High, 2 Good, 3 Moderate, 3 Low (Total: 10)
- **Fat**: 1 High, 2 Good, 0 Moderate, 1 Low (Total: 4)
- **Carb**: 3 High, 1 Good, 1 Moderate, 0 Low (Total: 5)
- **Fiber**: 2 High, 1 Good, 0 Moderate, 0 Low (Total: 3)

### Step-by-Step Calculation

#### 1. Protein Weighted Deduction

```
Weighted Sum = (2×0) + (2×2) + (3×3) + (3×5)
             = 0 + 4 + 9 + 15
             = 28

Weighted Average = 28 / 10 = 2.8

Tier Mapping: 2.8 falls in range 2.01-3.50 → Moderate Tier
Final Deduction: -3 pts
```

#### 2. Fat Weighted Deduction

```
Weighted Sum = (1×0) + (2×2) + (0×3) + (1×5)
             = 0 + 4 + 0 + 5
             = 9

Weighted Average = 9 / 4 = 2.25

Tier Mapping: 2.25 falls in range 2.01-3.50 → Moderate Tier
Final Deduction: -3 pts
```

#### 3. Carb Weighted Deduction

```
Weighted Sum = (3×0) + (1×2) + (1×3) + (0×5)
             = 0 + 2 + 3 + 0
             = 5

Weighted Average = 5 / 5 = 1.0

Tier Mapping: 1.0 falls in range 0.00-1.00 → High Tier
Final Deduction: 0 pts
```

#### 4. Fiber Weighted Deduction

```
Weighted Sum = (2×0) + (1×2) + (0×3) + (0×5)
             = 0 + 2 + 0 + 0
             = 2

Weighted Average = 2 / 3 = 0.67

Tier Mapping: 0.67 falls in range 0.00-1.00 → High Tier
Final Deduction: 0 pts
```

#### 5. Final Score

```
Average Deduction = (3 + 3 + 0 + 0) / 4 = 1.5

Final Score = 100 - 1.5 = 98.5
```

## Implementation

### IngredientQualityScorer Class

The scorer is implemented in `app/scoring/ingredient_quality_scorer.py`:

```python
from app.scoring.ingredient_quality_scorer import IngredientQualityScorer

scorer = IngredientQualityScorer(db, weight=0.35)
score = scorer.calculate_score(product)
details = scorer.get_score_details(product)
```

### Key Methods

#### `calculate_score(product: ProductList) -> float`

Calculates the ingredient quality score (0-100) based on weighted deductions.

#### `get_score_details(product: ProductList) -> Dict`

Returns detailed breakdown including:
- Weighted averages for each macro group
- Deduction points for each group
- Ingredient counts by tier
- Final score breakdown

### Integration with Scoring Service

The scorer is automatically used by `ScoringService` when calculating product scores:

```python
from app.services.scoring_service import ScoringService

service = ScoringService(db)
score = service.calculate_product_score(product_id)
```

The ingredient quality component will include:
- Component score (0-100)
- Weight (default 0.35 = 35%)
- Weighted score
- Detailed breakdown in JSON format

## Database Fields Used

The scorer reads from `processed_products` table:

**Protein Fields:**
- `protein_ingredients_high` (INTEGER)
- `protein_ingredients_good` (INTEGER)
- `protein_ingredients_moderate` (INTEGER)
- `protein_ingredients_low` (INTEGER)

**Fat Fields:**
- `fat_ingredients_high` (INTEGER)
- `fat_ingredients_good` (INTEGER)
- `fat_ingredients_moderate` (INTEGER)
- `fat_ingredients_low` (INTEGER)

**Carb Fields:**
- `carb_ingredients_high` (INTEGER)
- `carb_ingredients_good` (INTEGER)
- `carb_ingredients_moderate` (INTEGER)
- `carb_ingredients_low` (INTEGER)

**Fiber Fields:**
- `fiber_ingredients_high` (INTEGER)
- `fiber_ingredients_good` (INTEGER)
- `fiber_ingredients_moderate` (INTEGER)
- `fiber_ingredients_low` (INTEGER)

## Edge Cases

### No Ingredients in Category

If a macro group has zero ingredients, the system defaults to **Moderate tier** (-3 pts deduction).

### All Ingredients Same Tier

If all ingredients in a category are the same tier, the weighted average equals that tier's point value, and the deduction matches that tier.

### Mixed Quality Ingredients

The weighted average ensures that mixed quality ingredients are properly accounted for. For example:
- 1 High + 1 Low = (0 + 5) / 2 = 2.5 → Moderate (-3 pts)
- 2 High + 1 Low = (0 + 0 + 5) / 3 = 1.67 → Good (-2 pts)

## Testing

### Test the Scorer

```python
from app.scoring.ingredient_quality_scorer import IngredientQualityScorer
from app.models.database import SessionLocal

db = SessionLocal()
scorer = IngredientQualityScorer(db)

# Get a product
product = db.query(ProductList).first()

# Calculate score
score = scorer.calculate_score(product)
print(f"Ingredient Quality Score: {score:.2f}")

# Get details
details = scorer.get_score_details(product)
print(f"Protein Deduction: {details['protein']['deduction']}")
print(f"Fat Deduction: {details['fat']['deduction']}")
print(f"Carb Deduction: {details['carb']['deduction']}")
print(f"Fiber Deduction: {details['fiber']['deduction']}")
print(f"Total Deduction: {details['total_deduction']}")
print(f"Final Score: {details['final_score']:.2f}")
```

### Example Output

```json
{
  "base_score": 100.0,
  "protein": {
    "high_count": 2,
    "good_count": 2,
    "moderate_count": 3,
    "low_count": 3,
    "weighted_average": 2.8,
    "deduction": 3.0
  },
  "fat": {
    "high_count": 1,
    "good_count": 2,
    "moderate_count": 0,
    "low_count": 1,
    "weighted_average": 2.25,
    "deduction": 3.0
  },
  "carb": {
    "high_count": 3,
    "good_count": 1,
    "moderate_count": 1,
    "low_count": 0,
    "weighted_average": 1.0,
    "deduction": 0.0
  },
  "fiber": {
    "high_count": 2,
    "good_count": 1,
    "moderate_count": 0,
    "low_count": 0,
    "weighted_average": 0.67,
    "deduction": 0.0
  },
  "total_deduction": 1.5,
  "final_score": 98.5,
  "dirty_dozen_count": 0,
  "synthetic_nutrition_count": 0
}
```

## Summary

The Ingredient Quality Scoring System:

✅ **Uses weighted deduction formula** for fair scoring  
✅ **Applies to four macro groups** (Protein, Fat, Carb, Fiber)  
✅ **Maps weighted averages to tiers** using defined thresholds  
✅ **Calculates final score** starting from 100 with deductions  
✅ **Provides detailed breakdowns** for transparency  
✅ **Handles edge cases** gracefully  

**Key Benefits:**
- Fair scoring even with mixed quality ingredients
- Transparent calculation process
- Detailed breakdowns for analysis
- Consistent scoring across all products

