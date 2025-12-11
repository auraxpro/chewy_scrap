# Getting Started with Dog Food Scoring API

Welcome! This guide will help you get up and running with the newly restructured Dog Food Scoring API.

## 🎉 What's New?

The project has been restructured from a simple scraper into a comprehensive REST API system:

- ✅ **FastAPI REST API** - Modern, fast, auto-documented API
- ✅ **Modular Architecture** - Clear separation of concerns
- ✅ **Service Layer** - Business logic separated from API
- ✅ **Base Classes** - Easy to extend with new processors and scorers
- ✅ **Type Safety** - Pydantic schemas for validation
- ✅ **Production Ready** - Error handling, health checks, CORS
- ✅ **Manual Scraping** - Independent scraping scripts (no background tasks needed)

## 🚀 Quick Start (5 Minutes)

### Option 1: Using the Start Script (Easiest)

```bash
# Make script executable
chmod +x start_api.sh

# Run it!
./start_api.sh
```

This will:
1. Check prerequisites
2. Create virtual environment
3. Install dependencies
4. Set up .env file
5. Start PostgreSQL
6. Initialize database
7. Start API server

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env if needed

# 4. Start database
docker-compose up -d

# 5. Initialize database
python3 -c "from app.models.database import init_db; init_db()"

# 6. Start API server
uvicorn app.main:app --reload
```

## 🌐 Access the API

Once running, visit:

- **📚 API Documentation**: http://localhost:8000/docs
- **📖 Alternative Docs**: http://localhost:8000/redoc
- **❤️ Health Check**: http://localhost:8000/health
- **📊 API Root**: http://localhost:8000/

## ✅ Verify Everything Works

### 1. Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Check Database Connection

```bash
curl http://localhost:8000/api/v1/health/detailed
```

Should show database status as "healthy".

### 3. Get Product Stats

```bash
curl http://localhost:8000/api/v1/products/stats/overview
```

This will show how many products are in your database.

## 📊 Using the API

### Interactive Documentation

The easiest way to explore the API is through the interactive docs:

1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Example API Calls

```bash
# Get all products (paginated)
curl "http://localhost:8000/api/v1/products?page=1&page_size=10"

# Get a specific product
curl "http://localhost:8000/api/v1/products/1"

# Search products
curl -X POST "http://localhost:8000/api/v1/products/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "salmon",
    "min_score": 70,
    "page": 1,
    "page_size": 50
  }'

# Calculate score for a product
curl -X POST "http://localhost:8000/api/v1/scores/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "force_recalculate": false
  }'

# Get top scored products
curl "http://localhost:8000/api/v1/scores/top?limit=10"
```

## 🎯 Running Manual Operations (Unified CLI)

**Important:** All manual operations (scraping, processing, scoring) are **independent** from the API server:
- The API serves data from the database
- Manual operations update the database when needed
- You can run the API without running manual operations, and vice versa

### Unified CLI Tool (Recommended)

Use the unified CLI for all operations:

```bash
# Show all available commands
python scripts/main.py --help

# Scrape product list (pages 1-138)
python scripts/main.py --scrape

# Scrape product details
python scripts/main.py --scrape --details

# Scrape with limit
python scripts/main.py --scrape --details --limit 100

# Test mode (first 5 products)
python scripts/main.py --scrape --details --test

# Process products
python scripts/main.py --process

# Calculate scores
python scripts/main.py --score

# Run complete pipeline (scrape → process → score)
python scripts/main.py --all

# Show statistics
python scripts/main.py --stats

# Process/score single product
python scripts/main.py --process --product-id 123
python scripts/main.py --score --product-id 123

# Force recalculate
python scripts/main.py --score --force --limit 50
```

### Alternative: Individual Scripts

You can also use individual scripts if needed:

```bash
# Scraping
python scripts/scrape_products.py --details

# Processing
python scripts/process_products.py

# Scoring
python scripts/calculate_scores.py

# Auto-restart monitor (for long scraping sessions)
python app/scraper/monitor.py --details --limit 1000
```

## 🔧 Checking for Issues

Run the import checker to verify everything is set up correctly:

```bash
python check_imports.py
```

This will:
- Check for old import paths
- Verify critical files
- Test module imports

## 📁 Project Structure Overview

```
api/
├── app/                    # Main application
│   ├── main.py            # FastAPI app entry point
│   ├── config.py          # Configuration
│   ├── models/            # Database models
│   ├── schemas/           # API schemas (Pydantic)
│   ├── api/               # REST API endpoints
│   │   └── v1/           # API version 1
│   ├── scraper/           # Scraping module
│   ├── processors/        # Data processors (TODO)
│   ├── scoring/           # Scoring system (TODO)
│   └── services/          # Business logic
│
├── scripts/               # CLI scripts
│   └── scrape_products.py
│
├── tests/                 # Test suite (TODO)
│
└── docs/                  # Documentation
```

## 🎯 Next Steps

### If You're a Developer

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read the Code**: Start with `app/main.py` and `app/api/v1/products.py`
3. **Implement Processors**: See `app/processors/base_processor.py`
4. **Implement Scorers**: See `app/scoring/base_scorer.py`
5. **Write Tests**: Add tests in `tests/`

### If You're Using the API

1. **Read API Docs**: http://localhost:8000/docs
2. **Test Endpoints**: Use the interactive docs
3. **Integrate**: Use the API endpoints in your frontend
4. **Monitor**: Check `/health` endpoint for status

## 📚 Important Files to Read

1. **`README.md`** - Comprehensive project documentation
2. **`MIGRATION_CHECKLIST.md`** - What's done and what's needed
3. **`docs/RESTRUCTURING_SUMMARY.md`** - Details about the restructuring
4. **`.env.example`** - All configuration options

## ⚙️ Configuration

Edit `.env` file to customize:

```env
# API Settings
API_TITLE=Dog Food Scoring API
API_VERSION=1.0.0
DEBUG=True

# Database
DATABASE_URL=postgresql://chewy_user:chewy_password@localhost:5432/chewy_db

# Scoring Weights (must sum to 1.0)
SCORE_WEIGHT_INGREDIENTS=0.35
SCORE_WEIGHT_NUTRITION=0.30
SCORE_WEIGHT_PROCESSING=0.20
SCORE_WEIGHT_PRICE_VALUE=0.15

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 🐛 Troubleshooting

### "Module not found" errors

```bash
# Check imports
python check_imports.py

# Verify virtual environment is activated
which python  # Should show .venv/bin/python
```

### Database connection errors

```bash
# Check if PostgreSQL is running
docker ps

# Restart database
docker-compose restart

# Check logs
docker-compose logs
```

### API won't start

```bash
# Check for syntax errors
python -m py_compile app/main.py

# Run with debug logging
uvicorn app.main:app --reload --log-level debug
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process or use a different port
uvicorn app.main:app --reload --port 8001
```

## 📖 Learning Resources

### FastAPI
- Official Docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### SQLAlchemy
- Official Docs: https://docs.sqlalchemy.org/
- ORM Tutorial: https://docs.sqlalchemy.org/en/14/orm/tutorial.html

### Pydantic
- Official Docs: https://docs.pydantic.dev/

## 🎓 API Development Workflow

1. **Add a new endpoint**:
   - Define Pydantic schema in `app/schemas/`
   - Add business logic to service in `app/services/`
   - Create endpoint in `app/api/v1/`

2. **Add a processor**:
   - Create class inheriting from `BaseProcessor`
   - Implement `process()` method
   - Add to processing pipeline

3. **Add a scorer**:
   - Create class inheriting from `BaseScorer`
   - Implement `calculate_score()` method
   - Add to main scorer with weight

## 💡 Tips

- **Use the docs**: Interactive docs at `/docs` are your friend
- **Check examples**: Look at existing endpoints for patterns
- **Test as you go**: Use curl or the interactive docs to test
- **Read docstrings**: All classes and methods are documented
- **Check logs**: Run with `--log-level debug` for details

## 🆘 Getting Help

1. **Check documentation** in `docs/` folder
2. **Read code comments** - well documented
3. **Check logs** for error messages
4. **Use interactive docs** to test endpoints
5. **Review examples** in existing code

## ✨ Current Status

✅ **Working**:
- API server and endpoints
- Database models and relationships
- Product CRUD operations
- Search and filtering
- Health checks
- Auto-generated documentation

⏳ **In Progress**:
- Specific processor implementations
- Specific scorer implementations
- Comprehensive test suite

📝 **Planned**:
- Authentication/authorization
- Rate limiting
- Redis caching (optional)
- GraphQL API (optional)

## 🎉 You're Ready!

You now have a production-ready API framework for the dog food scoring system. The foundation is solid, and you can now focus on implementing the specific business logic (processors and scorers).

Visit http://localhost:8000/docs to start exploring! 🚀

## 🔄 Architecture: Manual Scraping

This project uses a **simple, manual scraping approach**:

### How It Works

1. **Scraping** - Run scripts manually when you need data
2. **Processing** - Run scripts to normalize data
3. **Scoring** - Run scripts to calculate scores
4. **API** - Serves the processed data to your frontend

### No Background Tasks

- ❌ No Celery
- ❌ No Redis queues
- ❌ No automatic scheduling
- ✅ Simple CLI scripts
- ✅ Full control
- ✅ Easy to debug

### Why This Approach?

- **Simplicity** - No complex infrastructure
- **Control** - You decide when to scrape
- **Debugging** - Easy to see what's happening
- **Flexibility** - Run scraping on demand
- **Resource Efficient** - Only use resources when needed

### Typical Workflow

**Option 1: Using Unified CLI (Easiest)**

```bash
# Run everything at once
python scripts/main.py --all

# Or step by step:
python scripts/main.py --scrape --details    # 1. Scrape data
python scripts/main.py --process              # 2. Process data  
python scripts/main.py --score                # 3. Calculate scores

# API is always running for frontend (separate terminal)
uvicorn app.main:app --reload
```

**Option 2: Using Individual Scripts**

```bash
# 1. Scrape when you need fresh data (manual)
python scripts/scrape_products.py --details --limit 100

# 2. Process the data (manual, after scraping)
python scripts/process_products.py

# 3. Calculate scores (manual, after processing)
python scripts/calculate_scores.py

# 4. API is always running for frontend
uvicorn app.main:app --reload
```

The API and manual operations are **completely independent**. This keeps the architecture simple and maintainable.

---

**Need help?** Check `MIGRATION_CHECKLIST.md` for detailed next steps or `README.md` for comprehensive documentation.

**Happy coding!** 🐕 ❤️