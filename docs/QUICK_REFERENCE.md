# Dog Food Scoring API - Quick Reference

## 🚀 Getting Started (5 Minutes)

```bash
# Quick start
chmod +x start_api.sh
./start_api.sh

# Or manual
pip install -r requirements.txt
docker-compose up -d
python3 -c "from app.models.database import init_db; init_db()"
uvicorn app.main:app --reload
```

**Access:** http://localhost:8000/docs

---

## 🎯 Unified CLI Commands

### Basic Usage

```bash
# Show help
python scripts/main.py --help

# Show statistics
python scripts/main.py --stats

# Run everything
python scripts/main.py --all
```

### Scraping

```bash
# Scrape product list (pages 1-138)
python scripts/main.py --scrape

# Scrape product details
python scripts/main.py --scrape --details

# Test mode (5 products)
python scripts/main.py --scrape --details --test

# With limit
python scripts/main.py --scrape --details --limit 100

# From offset
python scripts/main.py --scrape --details --offset 500 --limit 100
```

### Processing

```bash
# Process all unprocessed products
python scripts/main.py --process

# Process with limit
python scripts/main.py --process --limit 100

# Process single product
python scripts/main.py --process --product-id 123

# Force reprocess
python scripts/main.py --process --force --limit 50
```

### Scoring

```bash
# Score all unscored products
python scripts/main.py --score

# Score with limit
python scripts/main.py --score --limit 100

# Score single product
python scripts/main.py --score --product-id 123

# Force recalculate
python scripts/main.py --score --force --limit 50
```

### Complete Pipeline

```bash
# Run: Scrape → Process → Score
python scripts/main.py --all

# With limit (test mode)
python scripts/main.py --all --limit 10
```

---

## 🌐 API Server

### Start Server

```bash
# Development (auto-reload)
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Endpoints

**Documentation:**
- Interactive: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Products:**
```bash
GET  /api/v1/products/                    # List products
GET  /api/v1/products/{id}                # Get product
POST /api/v1/products/search              # Search products
GET  /api/v1/products/category/{category} # By category
GET  /api/v1/products/stats/overview      # Statistics
```

**Scores:**
```bash
POST /api/v1/scores/calculate             # Calculate score
GET  /api/v1/scores/product/{id}          # Get product score
GET  /api/v1/scores/top                   # Top products
GET  /api/v1/scores/stats/overview        # Statistics
```

**Health:**
```bash
GET /api/v1/health/                       # Basic check
GET /api/v1/health/detailed               # With database
GET /api/v1/health/ready                  # Readiness probe
GET /api/v1/health/live                   # Liveness probe
```

---

## 📊 Common Tasks

### Check Status

```bash
# Show comprehensive stats
python scripts/main.py --stats

# Via API
curl http://localhost:8000/api/v1/products/stats/overview
curl http://localhost:8000/api/v1/scores/stats/overview
```

### Fresh Data Collection

```bash
# 1. Scrape new products
python scripts/main.py --scrape --details --limit 50

# 2. Process them
python scripts/main.py --process

# 3. Calculate scores
python scripts/main.py --score

# Or all at once
python scripts/main.py --all --limit 50
```

### Update Existing Data

```bash
# Reprocess products
python scripts/main.py --process --force --limit 100

# Recalculate scores
python scripts/main.py --score --force --limit 100
```

### Test Single Product

```bash
# Scrape
python scripts/main.py --scrape --details --test-url "https://www.chewy.com/..."

# Process
python scripts/main.py --process --product-id 123

# Score
python scripts/main.py --score --product-id 123
```

---

## 🐛 Troubleshooting

### Database Issues

```bash
# Check if running
docker ps

# Restart
docker-compose restart

# Reinitialize
python3 -c "from app.models.database import init_db; init_db()"
```

### Import Errors

```bash
# Check imports
python check_imports.py

# Verify environment
which python  # Should show .venv/bin/python
source .venv/bin/activate
```

### Port Already in Use

```bash
# Find process
lsof -i :8000

# Use different port
uvicorn app.main:app --reload --port 8001
```

---

## 📁 Project Structure

```
api/
├── app/                      # Main application
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── api/v1/              # REST API endpoints
│   ├── scraper/             # Scraping module
│   ├── processors/          # Data processors
│   ├── scoring/             # Scoring system
│   └── services/            # Business logic
├── scripts/
│   └── main.py              # 🎯 Unified CLI tool
├── tests/                   # Test suite
└── docs/                    # Documentation
```

---

## ⚙️ Configuration

Edit `.env` file:

```env
# Database
DATABASE_URL=postgresql://chewy_user:chewy_password@localhost:5432/chewy_db

# API
DEBUG=True
API_VERSION=1.0.0

# Scoring Weights (must sum to 1.0)
SCORE_WEIGHT_INGREDIENTS=0.35
SCORE_WEIGHT_NUTRITION=0.30
SCORE_WEIGHT_PROCESSING=0.20
SCORE_WEIGHT_PRICE_VALUE=0.15

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## 📚 Documentation

- **README.md** - Full documentation
- **GETTING_STARTED.md** - Setup guide
- **WORKFLOW.md** - Complete workflow
- **MIGRATION_CHECKLIST.md** - Implementation tasks
- **QUICK_REFERENCE.md** - This file

---

## 🔄 Typical Workflow

```bash
# 1. Start API server (always running)
uvicorn app.main:app --reload &

# 2. Scrape data (when needed)
python scripts/main.py --scrape --details

# 3. Process data (after scraping)
python scripts/main.py --process

# 4. Calculate scores (after processing)
python scripts/main.py --score

# 5. View via API
open http://localhost:8000/docs
```

---

## 💡 Pro Tips

- Use `--test` flag when trying new things
- Always check `--stats` to see progress
- Use `--limit` to process in batches
- Keep API running, run manual ops separately
- Use unified CLI for all operations

---

## 🆘 Need Help?

```bash
# Show help
python scripts/main.py --help

# Check status
python scripts/main.py --stats

# Verify imports
python check_imports.py

# Read docs
cat docs/WORKFLOW.md
```

---

**Quick Links:**
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- GitHub Issues: [Your repo URL]

**Remember:** API and manual operations are separate! 🚀