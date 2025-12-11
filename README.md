# Dog Food Scoring API

A comprehensive REST API system for scraping, processing, scoring, and serving dog food product data from Chewy.com.

## 🌟 Features

- **Web Scraping**: Automated scraping of dog food products from Chewy.com with anti-bot detection
- **Data Processing**: Normalize and analyze product information (ingredients, categories, processing methods)
- **Scoring System**: Multi-criteria scoring algorithm evaluating products on:
  - Ingredient Quality (35%)
  - Nutritional Value (30%)
  - Processing Method (20%)
  - Price-Value Ratio (15%)
- **REST API**: FastAPI-based endpoints for accessing products, scores, and statistics
- **Manual Scraping**: Standalone scraping scripts that can be run independently
- **Distributed Scraping**: Support for multi-computer parallel scraping
- **Production Ready**: Comprehensive error handling, logging, and health checks

## 📁 Project Structure

```
api/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   │
│   ├── models/                    # Database models (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── database.py            # Database setup & session management
│   │   ├── product.py             # ProductList & ProductDetails models
│   │   └── score.py               # ProductScore & ScoreComponent models
│   │
│   ├── schemas/                   # Pydantic schemas (API contracts)
│   │   ├── __init__.py
│   │   ├── product.py             # Product request/response schemas
│   │   └── score.py               # Score request/response schemas
│   │
│   ├── api/                       # REST API endpoints
│   │   ├── __init__.py
│   │   ├── dependencies.py        # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Main API router
│   │       ├── health.py          # Health check endpoints
│   │       ├── products.py        # Product endpoints
│   │       └── scores.py          # Score endpoints
│   │
│   ├── scraper/                   # Web scraping module
│   │   ├── __init__.py
│   │   ├── chewy_scraper.py       # Main Chewy scraper
│   │   ├── monitor.py             # Auto-restart monitor
│   │   ├── distribute_work.py     # Multi-computer distribution
│   │   ├── export_data.py         # Data export utility
│   │   └── import_data.py         # Data import utility
│   │
│   ├── processors/                # Data processing & normalization
│   │   ├── __init__.py
│   │   └── base_processor.py      # Abstract base processor
│   │       # TODO: Add specific processors:
│   │       # - processing_detector.py
│   │       # - ingredient_normalizer.py
│   │       # - category_normalizer.py
│   │       # - packaging_estimator.py
│   │
│   ├── scoring/                   # Scoring system
│   │   ├── __init__.py
│   │   └── base_scorer.py         # Abstract base scorer
│   │       # TODO: Add specific scorers:
│   │       # - ingredient_scorer.py
│   │       # - nutrition_scorer.py
│   │       # - processing_scorer.py
│   │       # - price_value_scorer.py
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── product_service.py     # Product CRUD & search
│   │   └── scoring_service.py     # Score calculation & retrieval
│   │
│   ├── core/                      # Core utilities
│   │   ├── __init__.py
│   │   └── # TODO: Add core utilities
│   │
│   └── utils/                     # Helper utilities
│       ├── __init__.py
│       └── # TODO: Add helper functions
│
├── scripts/                       # Standalone CLI scripts
│   ├── __init__.py
│   └── scrape_products.py         # Scraping script
│       # TODO: Add more scripts:
│       # - process_products.py
│       # - calculate_scores.py
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_api/
│   ├── test_processors/
│   ├── test_scoring/
│   └── test_services/
│
├── docs/                          # Documentation
│   └── # TODO: Add documentation
│
├── .env.example                   # Environment variables template
├── .gitignore
├── docker-compose.yml             # PostgreSQL container
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Chrome/Chromium browser (for scraping)

### 1. Clone and Setup

```bash
# Clone the repository
cd api

# Create virtual environment
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for scraping)
playwright install chromium
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (database credentials, API config, etc.)
nano .env
```

### 3. Start Database

```bash
# Start PostgreSQL container
docker-compose up -d

# Verify database is running
docker ps
```

### 4. Initialize Database

```bash
# Run FastAPI application (will auto-initialize database)
python -m uvicorn app.main:app --reload
```

### 5. Access API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 Usage

### 🎯 Unified CLI (Recommended)

The easiest way to run all operations is using the **unified CLI tool**:

```bash
# Using the convenient wrapper (recommended)
python cli.py --help

# Or via scripts directory
python scripts/main.py --help

# Show all available commands
python cli.py --help

# Scrape product list (pages 1-138)
python cli.py --scrape

# Scrape product details
python cli.py --scrape --details

# Scrape with limit
python cli.py --scrape --details --limit 100

# Test mode (first 5 products)
python cli.py --scrape --details --test

# Process products
python cli.py --process

# Calculate scores
python cli.py --score

# Run complete pipeline (scrape → process → score)
python cli.py --all

# Show statistics
python cli.py --stats

# Process single product
python cli.py --process --product-id 123

# Force recalculate scores
python cli.py --score --force --limit 50
```

**Note:** Use `python cli.py` (shorter) or `python scripts/main.py` (both work the same way)

### Running the API Server

The API server and manual operations are **separate processes**. You can run the API without scraping, and vice versa.

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Alternative: Individual Scripts

You can also use individual scripts if needed:

#### Scrape Product List (URLs)

```bash
# Scrape all pages (1-138)
python scripts/scrape_products.py

# Test mode (scrape only first page)
python scripts/scrape_products.py --test
```

#### Scrape Product Details

```bash
# Scrape all unscraped products
python scripts/scrape_products.py --details

# Limit number of products
python scripts/scrape_products.py --details --limit 100

# Start from offset
python scripts/scrape_products.py --details --offset 100 --limit 50

# Test single product
python scripts/scrape_products.py --details --test-url "https://www.chewy.com/product/dp/12345"
```

#### Auto-Restart Monitor (For Long Sessions)

```bash
# Monitor and auto-restart on errors
python app/scraper/monitor.py --details --limit 1000

# With custom restart limits
python app/scraper/monitor.py --details --max-restarts 20 --cooldown 10
```

### API Endpoints

#### Products

```bash
# Get all products (paginated)
GET /api/v1/products?page=1&page_size=50

# Get product by ID
GET /api/v1/products/{product_id}

# Search products
POST /api/v1/products/search
{
  "query": "salmon",
  "category": "dry_kibble",
  "min_score": 80,
  "page": 1,
  "page_size": 50
}

# Get products by category
GET /api/v1/products/category/dry_kibble?page=1&page_size=50

# Get product statistics
GET /api/v1/products/stats/overview
```

#### Scores

```bash
# Calculate score for a product
POST /api/v1/scores/calculate
{
  "product_id": 1,
  "force_recalculate": false
}

# Get score by product ID
GET /api/v1/scores/product/{product_id}

# Get top scored products
GET /api/v1/scores/top?limit=10&category=dry_kibble

# Get score statistics
GET /api/v1/scores/stats/overview

# Batch calculate scores
POST /api/v1/scores/calculate/batch
{
  "product_ids": [1, 2, 3, 4, 5],
  "force_recalculate": false
}
```

#### Health Checks

```bash
# Basic health check
GET /api/v1/health/

# Detailed health check (includes database)
GET /api/v1/health/detailed

# Kubernetes readiness probe
GET /api/v1/health/ready

# Kubernetes liveness probe
GET /api/v1/health/live
```

## 🔧 Development

### Adding New Processors

Create a new processor by inheriting from `BaseProcessor`:

```python
# app/processors/ingredient_normalizer.py
from app.processors.base_processor import BaseProcessor
from app.models.product import ProductList

class IngredientNormalizer(BaseProcessor):
    def process(self, product: ProductList) -> dict:
        """Normalize ingredient data"""
        if not product.details or not product.details.ingredients:
            return {}
        
        # Your normalization logic here
        normalized_ingredients = self._normalize_ingredients(
            product.details.ingredients
        )
        
        return {
            "normalized_ingredients": normalized_ingredients
        }
    
    def _normalize_ingredients(self, ingredients: str) -> str:
        # Implementation
        pass
```

### Adding New Scorers

Create a new scorer by inheriting from `BaseScorer`:

```python
# app/scoring/ingredient_scorer.py
from app.scoring.base_scorer import BaseScorer
from app.models.product import ProductList

class IngredientScorer(BaseScorer):
    def get_component_name(self) -> str:
        return "ingredient_quality"
    
    def calculate_score(self, product: ProductList) -> float:
        """Calculate ingredient quality score (0-100)"""
        if not product.details or not product.details.ingredients:
            return 0.0
        
        score = 0.0
        
        # Your scoring logic here
        # - Check for quality meat sources
        # - Check for whole food ingredients
        # - Penalize for fillers, by-products, etc.
        
        return self.validate_score(score)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_products.py

# Run specific test
pytest tests/test_api/test_products.py::test_get_product
```

### Code Quality

```bash
# Format code with black
black app/ scripts/ tests/

# Sort imports with isort
isort app/ scripts/ tests/

# Lint with flake8
flake8 app/ scripts/ tests/

# Type checking with mypy
mypy app/
```

## 🗄️ Database Schema

### ProductList
- Basic product information and scraping metadata
- Fields: `id`, `product_url`, `page_num`, `scraped`, `processed`, `scored`, `skipped`

### ProductDetails
- Detailed product information
- Fields: `product_name`, `price`, `size`, `ingredients`, `guaranteed_analysis`, etc.

### ProductScore
- Overall product scores
- Fields: `product_id`, `total_score`, `score_version`, `calculated_at`

### ScoreComponent
- Individual scoring components
- Fields: `score_id`, `component_name`, `component_score`, `weight`, `weighted_score`

## 🔐 Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Enable debug mode
- `CORS_ORIGINS`: Allowed CORS origins
- `SCORE_WEIGHT_*`: Scoring weights (must sum to 1.0)
- `SCRAPER_HEADLESS`: Run scraper in headless mode

## 📦 Multi-Computer Scraping

For large-scale scraping, distribute work across multiple computers:

```bash
# 1. On master computer, calculate work distribution
python app/scraper/distribute_work.py --computers 3 --chunk-size 1200

# 2. On each computer, run assigned range
# Computer 1:
python app/scraper/monitor.py --details --offset 0 --limit 1200

# Computer 2:
python app/scraper/monitor.py --details --offset 1200 --limit 1200

# 3. Export data from each computer
python app/scraper/export_data.py --output computer1_export.json

# 4. Import data on master computer
python app/scraper/import_data.py computer1_export.json
python app/scraper/import_data.py computer2_export.json
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📈 Performance Tips

1. **Database Indexing**: Ensure indexes on frequently queried fields
2. **Connection Pooling**: Configured in `app/models/database.py`
3. **Pagination**: Always use pagination for large datasets
4. **Caching**: Consider adding Redis for frequently accessed data
5. **Background Tasks**: Use Celery for long-running score calculations

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Run code quality checks
5. Submit a pull request

## 📝 TODO

### High Priority
- [ ] Implement specific processor classes (ingredient normalizer, category normalizer, etc.)
- [ ] Implement specific scorer classes (ingredient scorer, nutrition scorer, etc.)
- [ ] Add comprehensive test coverage
- [ ] Add API authentication/authorization
- [ ] Add rate limiting

### Medium Priority
- [ ] Add Celery for background tasks
- [ ] Add Redis for caching
- [ ] Add Alembic migrations
- [ ] Add API versioning documentation
- [ ] Add frontend integration guide

### Low Priority
- [ ] Add GraphQL API (optional)
- [ ] Add WebSocket support for real-time updates (optional)
- [ ] Add data export to CSV/Excel
- [ ] Add product comparison feature
- [ ] Add recommendation system

## 🔄 Workflow

### Typical Usage Flow

**Using Unified CLI (Easiest):**
```bash
# Run everything at once
python cli.py --all

# Or step by step:
python cli.py --scrape --details    # 1. Scrape data
python cli.py --process              # 2. Process data
python cli.py --score                # 3. Calculate scores
uvicorn app.main:app --reload        # 4. Start API
```

**Using Individual Scripts:**
```bash
# 1. Scraping (Manual, as needed)
python scripts/scrape_products.py --details

# 2. Processing (After scraping)
python scripts/process_products.py

# 3. Scoring (After processing)
python scripts/calculate_scores.py

# 4. API (Always running for frontend)
uvicorn app.main:app --reload
```

### Notes

- **API is independent**: The API serves existing data from the database
- **Scraping is manual**: Run scraping scripts when you need fresh data
- **No background tasks**: All processing happens through CLI scripts
- **Simple workflow**: Scrape → Process → Score → Serve via API

## 📄 License

[Add your license here]

## 📞 Support

For issues, questions, or contributions, please [open an issue](link-to-issues).

---

**Built with ❤️ for dog lovers and their furry friends! 🐕**