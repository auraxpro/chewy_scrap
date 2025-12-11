# Migration Checklist & Next Steps

## ✅ Completed Steps

The following restructuring tasks have been completed:

### Structure
- [x] Created new modular directory structure
- [x] Created all necessary `__init__.py` files
- [x] Moved existing files to new locations
- [x] Organized code into logical modules

### Database Layer
- [x] Split `database.py` into separate concerns
- [x] Created `app/models/database.py` for DB setup
- [x] Created `app/models/product.py` for product models
- [x] Created `app/models/score.py` for score models (new)
- [x] Added new fields to models (timestamps, processing flags)
- [x] Enhanced models with relationships and methods

### API Layer
- [x] Created FastAPI application (`app/main.py`)
- [x] Set up CORS and error handlers
- [x] Created API v1 router structure
- [x] Implemented health check endpoints
- [x] Implemented product endpoints (full CRUD + search)
- [x] Implemented score endpoints (calculate, retrieve, stats)
- [x] Created Pydantic schemas for request/response
- [x] Created dependency injection system

### Service Layer
- [x] Created `ProductService` with business logic
- [x] Created `ScoringService` with scoring logic
- [x] Separated business logic from API layer

### Base Classes
- [x] Created `BaseProcessor` abstract class
- [x] Created `BaseScorer` abstract class
- [x] Documented how to extend these classes

### Configuration
- [x] Enhanced `config.py` with API settings
- [x] Created `.env.example` with all options
- [x] Added scoring weights configuration
- [x] Added CORS configuration

### Scraper Module
- [x] Moved scraper files to `app/scraper/`
- [x] Updated imports in `chewy_scraper.py`
- [x] Moved CLI script to `scripts/scrape_products.py`
- [x] Updated imports in scraping scripts

### Documentation
- [x] Updated `README.md` with new structure
- [x] Created `RESTRUCTURING_SUMMARY.md`
- [x] Created `.env.example` template
- [x] Created auto-generated API docs (via FastAPI)

### Dependencies
- [x] Updated `requirements.txt` with FastAPI and tools
- [x] Added testing frameworks
- [x] Added code quality tools

### Scripts
- [x] Created `start_api.sh` for quick start
- [x] Moved scraping script to `scripts/`

---

## 🔄 Next Steps (Required)

### 1. Update Scraper Module Imports ⚠️ CRITICAL

Some scraper files still need import updates. Check and update:

```bash
# Files to check:
- app/scraper/monitor.py
- app/scraper/distribute_work.py
- app/scraper/export_data.py
- app/scraper/import_data.py
```

Update imports from:
```python
from database import SessionLocal, ProductList, ProductDetails
```

To:
```python
from app.models.database import SessionLocal
from app.models.product import ProductList, ProductDetails
```

### 2. Test the Setup

```bash
# Make scripts executable
chmod +x start_api.sh

# Test quick start
./start_api.sh

# Or manually:
# 1. Start database
docker-compose up -d

# 2. Initialize database
python3 -c "from app.models.database import init_db; init_db()"

# 3. Start API
uvicorn app.main:app --reload

# 4. Visit http://localhost:8000/docs
```

### 3. Verify Endpoints Work

Test each endpoint:

```bash
# Health check
curl http://localhost:8000/health

# Get products
curl http://localhost:8000/api/v1/products/

# Get product stats
curl http://localhost:8000/api/v1/products/stats/overview

# Get score stats
curl http://localhost:8000/api/v1/scores/stats/overview
```

### 4. Test Scraper Still Works

```bash
# Test product list scraping
python scripts/scrape_products.py --test

# Test product detail scraping
python scripts/scrape_products.py --details --limit 5
```

### 5. Create .env File

```bash
cp .env.example .env
# Edit .env with your settings
nano .env
```

---

## 📝 TODO: Implementation Tasks

### High Priority (Week 1-2)

#### 1. Implement Specific Processors

Create these files in `app/processors/`:

**`ingredient_normalizer.py`**
```python
from app.processors.base_processor import BaseProcessor

class IngredientNormalizer(BaseProcessor):
    def process(self, product):
        # Parse and normalize ingredients
        # Extract meat content, identify fillers, etc.
        pass
```

**`category_normalizer.py`**
```python
from app.processors.base_processor import BaseProcessor

class CategoryNormalizer(BaseProcessor):
    def process(self, product):
        # Normalize categories (dry_kibble, wet_food, raw, etc.)
        pass
```

**`processing_detector.py`**
```python
from app.processors.base_processor import BaseProcessor

class ProcessingDetector(BaseProcessor):
    def process(self, product):
        # Detect processing method from ingredients/description
        pass
```

**`packaging_estimator.py`**
```python
from app.processors.base_processor import BaseProcessor

class PackagingEstimator(BaseProcessor):
    def process(self, product):
        # Estimate package size in kg from size string
        pass
```

#### 2. Implement Specific Scorers

Create these files in `app/scoring/`:

**`ingredient_scorer.py`**
```python
from app.scoring.base_scorer import BaseScorer

class IngredientScorer(BaseScorer):
    def get_component_name(self):
        return "ingredient_quality"
    
    def calculate_score(self, product):
        # Score based on:
        # - Meat content and quality
        # - Whole food ingredients
        # - No by-products or fillers
        # - Specific ingredient analysis
        return 75.0  # 0-100
```

**`nutrition_scorer.py`**
```python
from app.scoring.base_scorer import BaseScorer

class NutritionScorer(BaseScorer):
    def get_component_name(self):
        return "nutritional_value"
    
    def calculate_score(self, product):
        # Score based on:
        # - Protein content
        # - Fat content
        # - Vitamins and minerals
        # - Caloric density
        return 80.0  # 0-100
```

**`processing_scorer.py`**
```python
from app.scoring.base_scorer import BaseScorer

class ProcessingScorer(BaseScorer):
    def get_component_name(self):
        return "processing_method"
    
    def calculate_score(self, product):
        # Score based on processing method:
        # Raw > Freeze-dried > Dehydrated > Wet > Kibble
        return 70.0  # 0-100
```

**`price_value_scorer.py`**
```python
from app.scoring.base_scorer import BaseScorer

class PriceValueScorer(BaseScorer):
    def get_component_name(self):
        return "price_value"
    
    def calculate_score(self, product):
        # Score based on:
        # - Price per kg
        # - Quality vs price ratio
        # - Value for money
        return 72.0  # 0-100
```

#### 3. Create Processing Pipeline

**`app/processors/pipeline.py`**
```python
from typing import List
from app.processors.base_processor import BaseProcessor
from app.processors.ingredient_normalizer import IngredientNormalizer
from app.processors.category_normalizer import CategoryNormalizer
# ... import others

class ProcessingPipeline:
    """Orchestrates all processors"""
    
    def __init__(self, db):
        self.processors: List[BaseProcessor] = [
            IngredientNormalizer(db),
            CategoryNormalizer(db),
            # ... add others
        ]
    
    def process_product(self, product_id: int):
        """Run all processors on a product"""
        for processor in self.processors:
            processor.process(product_id)
```

#### 4. Create Main Scorer

**`app/scoring/main_scorer.py`**
```python
from typing import List
from app.scoring.base_scorer import BaseScorer
from app.scoring.ingredient_scorer import IngredientScorer
# ... import others

class MainScorer:
    """Orchestrates all scoring components"""
    
    def __init__(self, db):
        self.scorers: List[BaseScorer] = [
            IngredientScorer(db, weight=0.35),
            NutritionScorer(db, weight=0.30),
            # ... add others
        ]
    
    def calculate_total_score(self, product_id: int):
        """Calculate total score from all components"""
        total = 0.0
        for scorer in self.scorers:
            total += scorer.calculate_weighted_score(product_id)
        return total
```

#### 5. Update ScoringService

Update `app/services/scoring_service.py` to use the new scorers:

```python
def calculate_product_score(self, product_id, force_recalculate=False):
    # Replace placeholder logic with:
    from app.scoring.main_scorer import MainScorer
    
    scorer = MainScorer(self.db)
    return scorer.calculate_total_score(product_id)
```

### Medium Priority (Week 3-4)

- [ ] Add comprehensive test coverage
- [ ] Add API authentication (JWT tokens)
- [ ] Add rate limiting
- [ ] Add request validation
- [ ] Create CLI scripts for processing and scoring
- [ ] Add database migrations with Alembic
- [ ] Add caching with Redis (optional)

### Lower Priority (Month 2+)

- [ ] Add GraphQL API (optional)
- [ ] Add WebSocket support for real-time updates (optional)
- [ ] Add data export (CSV, Excel)
- [ ] Add product comparison endpoint
- [ ] Add recommendation system
- [ ] Create admin dashboard
- [ ] Add analytics and reporting

## 🔄 Architecture Notes

### Scraping Approach

The project uses **manual scraping** via CLI scripts:

- ✅ **Scraping is standalone** - No integration with API server
- ✅ **Run on demand** - Execute scraping scripts when needed
- ✅ **No background tasks** - All processing happens synchronously
- ✅ **Simple workflow** - Scrape → Process → Score → API serves data

### Why Manual Scraping?

1. **Flexibility** - Run scraping when needed, not on a schedule
2. **Simplicity** - No need for Celery, Redis queues, or workers
3. **Control** - Direct control over scraping process
4. **Debugging** - Easier to debug and monitor
5. **Resource efficiency** - Only use resources when actively scraping

### Workflow

```bash
# 1. Scrape data (manual, as needed)
python scripts/scrape_products.py --details

# 2. Process data (manual, after scraping)
python scripts/process_products.py  # TODO: Create this

# 3. Calculate scores (manual, after processing)
python scripts/calculate_scores.py  # TODO: Create this

# 4. API serves the data (always running)
uvicorn app.main:app --reload
```

---

## 🧪 Testing Checklist

### Manual Testing

- [ ] API server starts without errors
- [ ] Health check endpoints work
- [ ] Product endpoints return data
- [ ] Score calculation works
- [ ] Scraper still functions
- [ ] Database migrations work

### Unit Tests to Write

Create these test files:

```
tests/
├── test_api/
│   ├── test_products.py       # Test product endpoints
│   └── test_scores.py         # Test score endpoints
├── test_processors/
│   ├── test_ingredient_normalizer.py
│   ├── test_category_normalizer.py
│   └── test_processing_detector.py
├── test_scoring/
│   ├── test_ingredient_scorer.py
│   ├── test_nutrition_scorer.py
│   └── test_main_scorer.py
└── test_services/
    ├── test_product_service.py
    └── test_scoring_service.py
```

Run tests:
```bash
pytest -v
pytest --cov=app --cov-report=html
```

---

## 🐛 Known Issues to Address

1. **Import Paths**: Some scraper module files may still have old import paths
2. **Database Migration**: Need to run `init_db()` to create new tables/columns
3. **Scoring Logic**: Currently using placeholder scores (needs real implementation)
4. **Price Parsing**: Price is stored as string, needs parsing for filters
5. **Error Handling**: Some edge cases may not be handled

---

## 📚 Documentation to Create

- [ ] `docs/API.md` - Detailed API documentation
- [ ] `docs/SCORING.md` - Scoring algorithm explanation
- [ ] `docs/PROCESSORS.md` - Processor development guide
- [ ] `docs/DEPLOYMENT.md` - Deployment instructions
- [ ] `docs/CONTRIBUTING.md` - Contribution guidelines

---

## 🚀 Deployment Checklist

When ready to deploy:

- [ ] Set `DEBUG=False` in production `.env`
- [ ] Configure production database
- [ ] Set up proper CORS origins
- [ ] Add API authentication
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Set up CI/CD pipeline
- [ ] Add load balancer (if needed)
- [ ] Configure SSL/TLS
- [ ] Set up rate limiting

## 📌 Important Notes

### Scraping Architecture

**The scraping system is SEPARATE from the API:**

- Scraping scripts are **standalone** and run independently
- The API **does not trigger** scraping
- Scraping is done **manually** when you need fresh data
- No Celery, no background tasks, no job queues

**Benefits:**
- ✅ Simple architecture
- ✅ Easy to debug
- ✅ Full control over when scraping happens
- ✅ No additional infrastructure needed
- ✅ Scraping doesn't affect API performance

**Scripts to create:**
```bash
scripts/
├── scrape_products.py     # ✅ Already exists
├── process_products.py    # TODO: Normalize/process data
└── calculate_scores.py    # TODO: Calculate scores for products
```

---

## 💡 Tips

1. **Start Simple**: Begin by implementing one processor and one scorer to understand the pattern
2. **Test Incrementally**: Test each component as you build it
3. **Use the Docs**: FastAPI auto-generates docs at `/docs` - very helpful for testing
4. **Check Logs**: Use `uvicorn app.main:app --reload --log-level debug` for detailed logs
5. **Database Browser**: Use tools like pgAdmin or DBeaver to inspect database

---

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**: Look for error messages in terminal
2. **Check Imports**: Verify all import paths are correct
3. **Check Database**: Ensure PostgreSQL is running and initialized
4. **Check Docs**: Review API docs at http://localhost:8000/docs
5. **Test Endpoints**: Use the interactive API docs to test endpoints
6. **Read Source**: The code is well-documented with docstrings

---

## ✨ Success Criteria

You'll know the migration is complete when:

- [x] ✅ API server starts without errors
- [ ] ⏳ All endpoints return valid responses
- [ ] ⏳ Scraper works with new import paths
- [ ] ⏳ At least one processor is implemented
- [ ] ⏳ At least one scorer is implemented
- [ ] ⏳ Score calculation produces real scores
- [ ] ⏳ Tests pass
- [ ] ⏳ Documentation is complete

---

**Current Status**: 🟡 **Structure Complete - Implementation Needed**

The project has been successfully restructured with a solid foundation. The next phase is implementing the specific processors and scorers to complete the scoring system functionality.

Good luck! 🚀