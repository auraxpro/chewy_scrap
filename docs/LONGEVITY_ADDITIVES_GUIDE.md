# Longevity Additives Classifier Guide

## Overview

The **Longevity Additives Classifier** identifies longevity-promoting additives in dog food product ingredients. These additives are categorized into four main groups: Herbs, Botanicals, Probiotics, and Other Longevity Additives.

**Classification Categories:**
- **Herbs** - Medicinal and culinary herbs (rosemary, turmeric, oregano, etc.)
- **Botanicals** - Fruits, vegetables, and plant extracts (blueberry, spirulina, green tea, etc.)
- **Probiotics** - Beneficial bacteria cultures (lactobacillus, bifidobacterium, etc.)
- **Other Longevity Additives** - Mushrooms, bee products, joint support, antioxidants, and more

## Key Features

### 1. Ingredient Parsing
- Splits ingredients by comma
- Normalizes text (lowercase, clean whitespace, remove special characters)
- Handles variations in formatting and spelling

### 2. Multi-Category Keyword Matching
Each ingredient is checked against four keyword categories:
- **Herbs** - 50+ main keywords, 80+ support keywords
- **Botanicals** - 60+ main keywords, 80+ support keywords
- **Probiotics** - 20+ main keywords, 30+ support keywords
- **Other Longevity Additives** - 30+ main keywords, 80+ support keywords

### 3. Keyword Matching Strategy
- **Main Keywords**: Primary identifiers (e.g., "rosemary", "probiotics", "reishi mushroom")
- **Support Keywords**: Variations and related terms (e.g., "rosemary extract", "organic rosemary", "natural rosemary extract")
- Matching uses word boundaries for single words and phrase matching for multi-word keywords

### 4. Database Integration
Results are saved to `processed_products` table:
- `longevity_additives` - Comma-separated list of found additives (original format)
- `longevity_additives_count` - Count of unique additives found

---

## Quick Start

### Basic Usage

```python
from app.processors.longevity_additives_classifier import (
    LongevityAdditivesClassifier,
    classify_longevity_additives,
)

# Method 1: Using convenience function
result = classify_longevity_additives(
    ingredients="Chicken, brown rice, rosemary extract, turmeric, blueberry extract, probiotics, lactobacillus acidophilus"
)

print(f"Found {result.longevity_additives_count} longevity additive(s)")
print(f"Additives: {', '.join(result.longevity_additives)}")

# Method 2: Using classifier instance (recommended for batch processing)
classifier = LongevityAdditivesClassifier()

result = classifier.classify(
    ingredients="Salmon, quinoa, spirulina, chlorella, green tea extract, reishi mushroom, bee pollen"
)
```

### Classification Result

The `LongevityAdditivesResult` object contains:

```python
@dataclass
class LongevityAdditivesResult:
    longevity_additives: List[str]  # List of found additive ingredients
    longevity_additives_count: int  # Count of unique additives found
```

**Example Output:**
```
longevity_additives_count: 5
longevity_additives: ['rosemary extract', 'turmeric', 'blueberry extract', 'probiotics', 'lactobacillus acidophilus']
```

---

## Keyword Categories

### Herbs

**Main Keywords:**
- rosemary, rosemary extract
- parsley, parsley extract
- turmeric, turmeric extract, turmeric root
- oregano, oregano extract
- basil, basil extract
- cilantro, cilantro extract
- ginger, ginger extract
- sage, sage extract
- thyme, thyme extract
- chamomile, chamomile extract
- peppermint, peppermint extract
- spearmint, spearmint extract
- lemongrass, lemongrass extract
- dandelion, dandelion extract
- fennel, fennel extract
- echinacea, echinacea extract
- milk thistle, milk thistle extract
- nettle, nettle extract
- licorice root, licorice root extract
- yucca, yucca extract
- coriander, coriander seed
- dill, dill seed, dill extract
- marjoram, marjoram extract
- savory, savory extract
- lemon balm, lemon balm extract
- motherwort, motherwort extract
- hawthorn, hawthorn berry, hawthorn extract
- ashwagandha, ashwagandha root, ashwagandha extract

**Support Keywords:**
- natural rosemary extract, antioxidant rosemary extract
- organic rosemary, organic rosemary extract
- fresh parsley, organic parsley, dried parsley
- natural parsley extract
- curcumin, organic turmeric, organic turmeric extract
- wild oregano, organic oregano, oregano oil
- natural oregano extract
- organic basil, sweet basil, basil leaf
- fresh cilantro, coriander leaf, coriander extract
- fresh ginger, dried ginger, organic ginger
- natural ginger extract
- garden sage, organic sage, sage leaf extract
- fresh thyme, thyme leaf, natural thyme extract
- organic chamomile, chamomile flower
- organic peppermint, peppermint oil
- organic spearmint, spearmint oil
- organic lemongrass, lemongrass oil
- dandelion root, dandelion leaf
- natural dandelion extract
- fennel seed, fennel seed extract
- organic fennel extract
- organic echinacea, echinacea purpurea
- organic milk thistle, silymarin
- milk thistle seed extract
- organic nettle, nettle leaf extract
- organic licorice root, licorice root powder
- natural licorice extract
- yucca schidigera, yucca powder
- ground coriander seed, organic coriander
- curcuma longa, turmeric powder
- dried oregano, origanum vulgare
- sweet basil, ocimum basilicum
- basil powder
- organic dill, anethum graveolens
- dill weed, dried dill seed
- foeniculum vulgare, fennel powder
- organic thyme, thymus vulgaris
- dried marjoram, origanum majorana
- savory herb, satureja hortensis
- parsley flakes, petroselinum crispum
- peppermint leaves, mentha piperita
- spearmint leaves, mentha spicata
- salvia officinalis
- lemon balm powder, melissa officinalis
- leonurus cardiaca
- crataegus monogyna
- withania somnifera, winter cherry

### Botanicals

**Main Keywords:**
- blueberry, blueberry extract
- cranberry, cranberry extract
- spinach, spinach extract
- carrot, carrot extract
- pumpkin, pumpkin extract
- kelp, kelp extract
- spirulina, spirulina extract
- chlorella, chlorella extract
- green tea, green tea extract
- aloe vera, aloe vera extract
- apple, apple extract
- beet, beet extract
- broccoli, broccoli extract
- tomato, tomato extract
- sweet potato, sweet potato extract
- pomegranate, pomegranate extract
- chicory root, chicory root extract
- seaweed, seaweed extract
- barley grass, barley grass extract
- wheatgrass, wheatgrass extract
- acai, acai berry, acai extract
- goji, goji berry, goji extract
- elderberry, elderberry extract
- raspberry, raspberry extract
- blackberry, blackberry extract
- grape, grape extract
- mango, mango extract
- papaya, papaya extract
- kale, kale extract
- cucumber, cucumber extract
- zucchini, zucchini extract
- dandelion greens

**Support Keywords:**
- wild blueberry, organic blueberry, blueberry powder
- natural blueberry extract
- organic cranberry, dried cranberry, cranberry powder
- cranberry juice powder
- natural cranberry extract
- organic spinach, dried spinach
- spinach leaf powder
- natural spinach extract
- organic carrot, dehydrated carrot
- carrot powder, natural carrot extract
- organic pumpkin, dried pumpkin
- pumpkin powder, natural pumpkin extract
- ascophyllum nodosum, brown kelp
- kelp meal, kelp powder
- organic spirulina, spirulina powder
- organic chlorella, chlorella powder
- camellia sinensis, matcha powder
- natural green tea extract
- aloe barbadensis, aloe gel powder
- aloe vera juice powder
- organic apple, dried apple
- apple pomace, apple powder
- organic beet, beetroot powder
- beet juice powder, natural beet extract
- organic broccoli, broccoli powder
- tomato pomace, lycopene
- natural tomato extract
- organic sweet potato, sweet potato flour
- sweet potato powder
- organic pomegranate, pomegranate powder
- chicory inulin, chicory fiber
- dried chicory root, natural chicory extract
- dried seaweed, kelp flakes
- seaweed powder
- hordeum vulgare, barley grass powder
- triticum aestivum, wheatgrass juice powder
- euterpe oleracea, freeze-dried acai
- dried acai powder
- lycium barbarum, goji powder
- sambucus nigra, dried elderberry
- elderberry powder
- rubus idaeus, raspberry powder
- rubus fruticosus, blackberry powder
- vitis vinifera, grape skin extract
- grape seed extract
- mangifera indica, mango powder
- carica papaya, papaya powder
- brassica oleracea var. sabellica
- kale powder
- cucumis sativus, cucumber juice powder
- cucurbita pepo var. cylindrica
- zucchini powder
- taraxacum officinale
- dried dandelion leaf, dandelion root powder

### Probiotics

**Main Keywords:**
- probiotics
- probiotic blend
- probiotic cultures
- live cultures
- lactobacillus acidophilus
- lactobacillus casei
- lactobacillus plantarum
- lactobacillus rhamnosus
- bifidobacterium bifidum
- bifidobacterium animalis
- bifidobacterium longum
- bacillus coagulans
- bacillus subtilis
- enterococcus faecium
- streptococcus thermophilus
- pediococcus acidilactici
- lactobacillus brevis
- lactobacillus fermentum
- bifidobacterium breve
- dried bacillus coagulans fermentation
- dried bacillus coagulans fermentation product

**Support Keywords:**
- lactobacillus acidophilus fermentation product
- l. acidophilus
- lactobacillus casei fermentation product
- l. casei
- lactobacillus plantarum fermentation product
- l. plantarum
- lactobacillus rhamnosus fermentation product
- l. rhamnosus
- bifidobacterium bifidum fermentation product
- b. bifidum
- bifidobacterium animalis fermentation product
- b. animalis
- bifidobacterium longum fermentation product
- b. longum
- bacillus coagulans fermentation product
- b. coagulans
- bacillus subtilis fermentation product
- b. subtilis
- enterococcus faecium fermentation product
- e. faecium
- probiotic blend
- direct-fed microbials
- stabilized probiotics
- dried fermentation product
- freeze-dried probiotics
- microencapsulated probiotics
- streptococcus thermophilus fermentation product
- s. thermophilus
- pediococcus acidilactici fermentation product
- p. acidilactici
- lactobacillus brevis fermentation product
- l. brevis
- lactobacillus fermentum fermentation product
- l. fermentum
- bifidobacterium breve fermentation product
- b. breve
- shelf-stable probiotics
- viable probiotic culture
- probiotic consortium
- probiotic culture blend
- multi-strain probiotics

### Other Longevity Additives

**Main Keywords:**
- medicinal mushrooms
- functional mushrooms
- reishi mushroom
- shiitake mushroom
- maitake mushroom
- cordyceps mushroom
- turkey tail mushroom
- lion's mane mushroom
- chaga mushroom
- bee products
- bee pollen
- royal jelly
- colostrum
- green-lipped mussel
- glucosamine
- chondroitin sulfate
- msm
- astaxanthin
- curcumin
- resveratrol
- omega-3 fish oil
- krill oil
- algal dha
- camelina oil
- hemp seed
- chia seed
- sunflower seed
- black cumin seed
- quinoa
- amaranth
- coq10
- l-carnitine
- taurine

**Support Keywords:**
- mushroom blend, mushroom complex
- beta-glucans, 1,3/1,6-beta-glucans
- immune mushroom
- reishi extract, ganoderma lucidum
- reishi powder
- shiitake extract, lentinus edodes
- maitake extract, grifola frondosa
- cordyceps militaris, cordyceps sinensis
- turkey tail extract
- coriolus versicolor, trametes versicolor
- lion's mane extract, hericium erinaceus
- chaga extract, inonotus obliquus
- bee superfoods, dried bee pollen
- pollen granules
- royal jelly powder
- bovine colostrum, colostrum powder
- igg-rich colostrum
- perna canaliculus
- green-lipped mussel powder
- glm powder, mussel extract
- joint complex, joint support
- glucosamine hcl, glucosamine sulfate
- chondroitin, chondroitin sulfate sodium
- msm (methylsulfonylmethane)
- sulfur donor, cartilage support
- natural astaxanthin
- haematococcus pluvialis extract
- carotenoid antioxidant
- turmeric extract
- curcumin (95%), curcuminoids
- turmeric curcumin
- piperine-enhanced
- black pepper extract
- resveratrol (trans-resveratrol)
- polygonum cuspidatum extract
- japanese knotweed extract
- fish oil powder
- salmon oil, sardine oil
- anchovy oil, menhaden oil
- concentrated epa/dha
- triglyceride-form omega-3
- krill oil powder
- phospholipid omega-3
- algal oil, dha algal oil
- schizochytrium sp.
- camelina sativa oil, camelina meal
- ala source
- hempseed powder, cold-pressed hemp
- chia seed powder, milled chia
- sunflower seed meal
- black cumin (nigella sativa)
- nigella seed, thymoquinone source
- quinoa flakes, puffed quinoa
- amaranth flour
- coenzyme q10, ubiquinone
- ubiquinol, mitochondrial support
- l-carnitine tartrate
- acetyl-l-carnitine, carnitine
- taurine supplement, taurine additive
- heart support
- antioxidant complex
- longevity blend, vitality blend
- superfood blend
- omega-3 fortification
- joint & hip formula
- mobility support
- immune support complex
- skin & coat support
- cognitive support
- senior vitality, senior support
- longevity formula

---

## Processing with Database

### Using the Processor

```python
from app.models.database import SessionLocal
from app.processors.longevity_additives_processor import (
    LongevityAdditivesProcessor,
)

# Create database session
db = SessionLocal()

try:
    # Initialize processor
    processor = LongevityAdditivesProcessor(db, processor_version="v1.0.0")

    # Process single product
    result = processor.process_single(product_detail_id=123)
    print(f"Found {result.longevity_additives_count} additives")
    print(f"Additives: {result.longevity_additives}")

    # Process batch
    results = processor.process_batch([123, 456, 789])
    print(f"Success: {results['success']}, Failed: {results['failed']}")

    # Process all products
    results = processor.process_all(limit=100, skip_existing=True)
    print(f"Total: {results['total']}, Success: {results['success']}")

    # Get statistics
    stats = processor.get_statistics()
    print(f"Products with additives: {stats['with_additives']}")
    print(f"Average count: {stats['avg_additives_count']}")

    # Print formatted statistics
    processor.print_statistics()

finally:
    db.close()
```

### Convenience Function

```python
from app.models.database import SessionLocal
from app.processors.longevity_additives_processor import (
    process_longevity_additives,
)

db = SessionLocal()

# Process all products
results = process_longevity_additives(db, limit=100, skip_existing=True)

# Process specific products
results = process_longevity_additives(db, product_detail_ids=[123, 456, 789])
```

---

## Command Line Interface

### Using the Standalone Script

```bash
# Process all unprocessed products
python scripts/process_longevity_additives.py

# Process with limit
python scripts/process_longevity_additives.py --limit 100

# Reprocess all products (including already processed)
python scripts/process_longevity_additives.py --reprocess

# Show statistics only
python scripts/process_longevity_additives.py --stats-only

# Test mode (no database changes)
python scripts/process_longevity_additives.py --test
```

### Using the Unified CLI

```bash
# Process longevity additives
python scripts/main.py --process --longevity-additives

# Process with limit
python scripts/main.py --process --longevity-additives --limit 100

# Process single product
python scripts/main.py --process --longevity-additives --product-id 123

# Reprocess all (force)
python scripts/main.py --process --longevity-additives --force
```

---

## Database Schema

Results are saved to the `processed_products` table:

```sql
-- Longevity Additives Fields
longevity_additives TEXT,              -- Comma-separated list of found additives
longevity_additives_count INTEGER,      -- Count of unique additives found
```

### Example Data

```sql
SELECT 
    product_detail_id,
    longevity_additives,
    longevity_additives_count
FROM processed_products
WHERE longevity_additives_count > 0
LIMIT 5;
```

**Example Results:**
```
product_detail_id | longevity_additives                                    | longevity_additives_count
------------------|-------------------------------------------------------|--------------------------
123               | rosemary extract, turmeric, blueberry extract          | 3
456               | probiotics, lactobacillus acidophilus, spirulina       | 3
789               | reishi mushroom, bee pollen, omega-3 fish oil          | 3
```

---

## Text Normalization

The classifier normalizes text before matching:

1. **Lowercase conversion** - "Rosemary Extract" → "rosemary extract"
2. **Whitespace cleanup** - Multiple spaces → single space
3. **Special character removal** - Removes punctuation except hyphens and apostrophes
4. **Trimming** - Removes leading/trailing whitespace

**Example:**
```
Original: "Organic Rosemary Extract, Turmeric (Curcuma longa)"
Normalized: "organic rosemary extract turmeric curcuma longa"
```

---

## Matching Strategy

### Single Word Keywords
Uses word boundaries to prevent partial matches:
- Keyword: "sage"
- Matches: "sage", "sage extract", "garden sage"
- Does NOT match: "message", "sausage"

### Multi-Word Keywords
Uses phrase matching:
- Keyword: "green tea extract"
- Matches: "green tea extract", "organic green tea extract"
- Does NOT match: "green extract", "tea extract"

### Priority Matching
- Main keywords are checked first
- Support keywords are checked if no main keyword match
- First match wins (no duplicate entries)

---

## Examples

### Example 1: Herbs and Botanicals

**Input:**
```
Chicken, brown rice, rosemary extract, turmeric, blueberry extract, cranberry, spinach, fish oil
```

**Output:**
```python
LongevityAdditivesResult(
    longevity_additives=[
        'rosemary extract',
        'turmeric',
        'blueberry extract',
        'cranberry',
        'spinach'
    ],
    longevity_additives_count=5
)
```

### Example 2: Probiotics and Mushrooms

**Input:**
```
Beef, sweet potato, probiotics, lactobacillus acidophilus, reishi mushroom, shiitake mushroom, omega-3 fish oil
```

**Output:**
```python
LongevityAdditivesResult(
    longevity_additives=[
        'probiotics',
        'lactobacillus acidophilus',
        'reishi mushroom',
        'shiitake mushroom',
        'omega-3 fish oil'
    ],
    longevity_additives_count=5
)
```

### Example 3: Multiple Categories

**Input:**
```
Salmon, quinoa, spirulina, chlorella, green tea extract, aloe vera, goji berry, elderberry, bee pollen, royal jelly, glucosamine, chondroitin sulfate, astaxanthin, resveratrol, CoQ10, taurine
```

**Output:**
```python
LongevityAdditivesResult(
    longevity_additives=[
        'quinoa',
        'spirulina',
        'chlorella',
        'green tea extract',
        'aloe vera',
        'goji berry',
        'elderberry',
        'bee pollen',
        'royal jelly',
        'glucosamine',
        'chondroitin sulfate',
        'astaxanthin',
        'resveratrol',
        'CoQ10',
        'taurine'
    ],
    longevity_additives_count=15
)
```

### Example 4: No Additives

**Input:**
```
Chicken meal, brown rice, chicken fat, corn gluten meal, wheat flour, BHA, artificial colors
```

**Output:**
```python
LongevityAdditivesResult(
    longevity_additives=[],
    longevity_additives_count=0
)
```

---

## Statistics

### Get Statistics

```python
processor = LongevityAdditivesProcessor(db)
stats = processor.get_statistics()

print(f"Products with additives: {stats['with_additives']}")
print(f"Products without additives: {stats['without_additives']}")
print(f"Average additives count: {stats['avg_additives_count']}")
print(f"Maximum additives count: {stats['max_additives_count']}")
print(f"Total processed: {stats['_total_processed']}")
print(f"Unprocessed: {stats['_unprocessed']}")
```

### Print Formatted Statistics

```python
processor.print_statistics()
```

**Example Output:**
```
======================================================================
LONGEVITY ADDITIVES STATISTICS
======================================================================

Products with Longevity Additives:
  With Additives:        1,234 products
  Without Additives:     5,678 products

Additive Counts:
  Average:                 3.2 additives
  Maximum:                15 additives

Overall:
  Total Processed:      6,912
  Total Details:       7,500
  Unprocessed:           588
  Progress:             92.2%
======================================================================
```

---

## Best Practices

### 1. Batch Processing
For large datasets, use batch processing with limits:
```python
processor.process_all(limit=1000, skip_existing=True)
```

### 2. Error Handling
Always wrap processing in try-except blocks:
```python
try:
    result = processor.process_single(product_id)
except ValueError as e:
    print(f"Product not found: {e}")
except Exception as e:
    print(f"Processing error: {e}")
```

### 3. Skip Existing Records
Use `skip_existing=True` to avoid reprocessing:
```python
processor.process_all(skip_existing=True)
```

### 4. Version Tracking
Specify processor version for tracking:
```python
processor = LongevityAdditivesProcessor(db, processor_version="v1.0.0")
```

---

## Troubleshooting

### No Additives Found

**Possible Causes:**
1. Ingredients not in expected format (comma-separated)
2. Keywords not matching due to spelling variations
3. Special characters interfering with matching

**Solutions:**
- Check ingredient format: `"ingredient1, ingredient2, ingredient3"`
- Verify keywords include expected variations
- Check normalization output

### Duplicate Additives

The classifier automatically prevents duplicates by tracking found additives in a set.

### Performance

For large datasets:
- Use `limit` parameter to process in batches
- Use `skip_existing=True` to avoid reprocessing
- Process during off-peak hours

---

## API Integration

The processed data is available through the API:

```python
# Get processed product with longevity additives
GET /api/v1/products/{product_id}/processed

# Response includes:
{
    "longevity_additives": "rosemary extract, turmeric, blueberry extract",
    "longevity_additives_count": 3,
    ...
}
```

---

## Version History

- **v1.0.0** - Initial release
  - Herbs category (50+ main, 80+ support keywords)
  - Botanicals category (60+ main, 80+ support keywords)
  - Probiotics category (20+ main, 30+ support keywords)
  - Other Longevity Additives category (30+ main, 80+ support keywords)
  - Database integration
  - CLI support

---

## Related Documentation

- [Ingredient Quality Guide](./INGREDIENT_QUALITY_GUIDE.md) - Ingredient quality classification
- [Processing Method Guide](./PROCESSING_METHOD_GUIDE.md) - Processing method classification
- [Sourcing Integrity Guide](./SOURCING_INTEGRITY_GUIDE.md) - Sourcing integrity classification
- [CLI Guide](./CLI_GUIDE.md) - Command-line interface usage
- [Workflow Guide](./WORKFLOW.md) - Complete processing workflow

---

## Support

For issues or questions:
1. Check this documentation
2. Review example code in test mode: `python scripts/process_longevity_additives.py --test`
3. Check database statistics: `python scripts/process_longevity_additives.py --stats-only`
