# Dog Food Scoring API - Workflow Documentation

This document explains the complete workflow for the Dog Food Scoring API, from data collection to serving results.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Complete Workflow](#complete-workflow)
- [Manual Scraping Approach](#manual-scraping-approach)
- [Step-by-Step Guide](#step-by-step-guide)
- [Common Scenarios](#common-scenarios)
- [Best Practices](#best-practices)

## Overview

The Dog Food Scoring API uses a **simple, manual workflow** with four main stages:

1. **Scraping** - Collect product data from Chewy.com
2. **Processing** - Normalize and enhance the data
3. **Scoring** - Calculate quality scores
4. **API** - Serve data to frontend applications

Each stage is independent and runs as a separate CLI script.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Manual Workflow                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. SCRAPING                                                      │
│     ├─ scrape_products.py (CLI)                                  │
│     ├─ Collects product URLs                                     │
│     └─ Scrapes product details                                   │
│                        ↓                                          │
│                   [PostgreSQL]                                    │
│                        ↓                                          │
│  2. PROCESSING                                                    │
│     ├─ process_products.py (CLI)                                 │
│     ├─ Normalizes ingredients                                    │
│     ├─ Categorizes products                                      │
│     └─ Detects processing methods                                │
│                        ↓                                          │
│                   [PostgreSQL]                                    │
│                        ↓                                          │
│  3. SCORING                                                       │
│     ├─ calculate_scores.py (CLI)                                 │
│     ├─ Evaluates ingredient quality                              │
│     ├─ Assesses nutritional value                                │
│     ├─ Scores processing method                                  │
│     └─ Calculates price-value ratio                              │
│                        ↓                                          │
│                   [PostgreSQL]                                    │
│                        ↓                                          │
│  4. API (Always Running)                                          │
│     ├─ FastAPI Server                                             │
│     ├─ Serves product data                                        │
│     ├─ Provides scores                                            │
│     └─ Offers search/filtering                                    │
│                        ↓                                          │
│                   [Frontend]                                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Complete Workflow

### Stage 1: Scraping (Manual)

**Purpose:** Collect raw product data from Chewy.com

**When to run:** When you need fresh product data

**Commands:**
```bash
# Scrape product URLs (pages 1-138)
python scripts/scrape_products.py

# Scrape product details
python scripts/scrape_products.py --details
```

**Database Changes:**
- Creates records in `products_list` table
- Creates records in `product_details` table
- Sets `scraped = true` flag

### Stage 2: Processing (Manual)

**Purpose:** Normalize and enhance scraped data

**When to run:** After scraping new products

**Commands:**
```bash
# Process all unprocessed products
python scripts/process_products.py

# Process specific number
python scripts/process_products.py --limit 100
```

**Database Changes:**
- Updates `product_details` with normalized data
- Sets `processed = true` flag on `products_list`

**Processing Steps:**
1. Normalize ingredients list
2. Standardize category names
3. Detect processing method
4. Estimate package size

### Stage 3: Scoring (Manual)

**Purpose:** Calculate quality scores for products

**When to run:** After processing new products

**Commands:**
```bash
# Score all unscored products
python scripts/calculate_scores.py

# Score specific number
python scripts/calculate_scores.py --limit 100
```

**Database Changes:**
- Creates records in `product_scores` table
- Creates records in `score_components` table
- Sets `scored = true` flag on `products_list`

**Scoring Components:**
- Ingredient Quality (35%)
- Nutritional Value (30%)
- Processing Method (20%)
- Price-Value Ratio (15%)

### Stage 4: API (Always Running)

**Purpose:** Serve data to frontend applications

**When to run:** Always running (independent of scraping)

**Command:**
```bash
# Start API server
uvicorn app.main:app --reload
```

**Endpoints:**
- `GET /api/v1/products/` - List products
- `GET /api/v1/products/{id}` - Get product
- `POST /api/v1/products/search` - Search products
- `GET /api/v1/scores/top` - Top scored products
- `GET /api/v1/scores/stats/overview` - Statistics

## Manual Scraping Approach

### Why Manual?

1. **Simplicity** - No background job infrastructure needed
2. **Control** - You decide when to scrape
3. **Flexibility** - Easy to run specific portions
4. **Debugging** - Transparent and easy to troubleshoot
5. **Resource Efficient** - Only uses resources when needed

### No Background Tasks

This project **does NOT use**:
- ❌ Celery
- ❌ Redis queues
- ❌ Cron jobs
- ❌ Scheduled tasks
- ❌ Message brokers

Instead, it uses:
- ✅ Simple CLI scripts
- ✅ Manual execution
- ✅ Direct database access
- ✅ Transparent operations

### Independence of Components

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Scraping   │────▶│ Processing  │────▶│   Scoring   │────▶│     API     │
│   (CLI)     │     │    (CLI)    │     │    (CLI)    │     │  (Server)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      ▲                    ▲                    ▲                    │
      │                    │                    │                    │
      └────────────────────┴────────────────────┴────────────────────┘
                            PostgreSQL
```

Each component:
- Reads from and writes to the database
- Can run independently
- Doesn't require other components to be running
- Can be executed on demand

## Step-by-Step Guide

### Initial Setup (One Time)

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env

# 4. Start database
docker-compose up -d

# 5. Initialize database
python3 -c "from app.models.database import init_db; init_db()"
```

### First-Time Data Collection

```bash
# Step 1: Scrape product URLs (takes ~30 minutes)
python scripts/scrape_products.py

# Step 2: Scrape product details (takes several hours)
python scripts/scrape_products.py --details

# Or use auto-restart monitor for reliability
python app/scraper/monitor.py --details
```

### Daily Operations

```bash
# Check for new products (run occasionally)
python scripts/scrape_products.py --details --limit 50

# Process new products
python scripts/process_products.py

# Calculate scores
python scripts/calculate_scores.py

# API is always running for frontend
uvicorn app.main:app --reload
```

### Updating Existing Data

```bash
# Re-scrape specific products (force refresh)
python scripts/scrape_products.py --details --product-id 123

# Reprocess products (e.g., after algorithm update)
python scripts/process_products.py --force --limit 100

# Recalculate scores (e.g., after weight changes)
python scripts/calculate_scores.py --force --limit 100
```

## Common Scenarios

### Scenario 1: Fresh Start

**Goal:** Set up everything from scratch

```bash
# 1. Set up environment
./start_api.sh  # Or manual setup

# 2. Scrape all data (takes time)
python scripts/scrape_products.py
python scripts/scrape_products.py --details

# 3. Process data
python scripts/process_products.py

# 4. Calculate scores
python scripts/calculate_scores.py

# 5. Start API (in separate terminal)
uvicorn app.main:app --reload

# 6. Access API
open http://localhost:8000/docs
```

### Scenario 2: Add New Products

**Goal:** Scrape only new products that were added to Chewy

```bash
# 1. Check current status
python scripts/process_products.py  # Shows stats

# 2. Scrape with limit (safety)
python scripts/scrape_products.py --details --limit 50

# 3. Process new products
python scripts/process_products.py

# 4. Calculate scores
python scripts/calculate_scores.py

# API automatically serves new data
```

### Scenario 3: Update Scoring Algorithm

**Goal:** Recalculate scores with new algorithm

```bash
# 1. Update scoring code in app/scoring/

# 2. Update weights in .env if needed
nano .env  # Edit SCORE_WEIGHT_*

# 3. Recalculate all scores
python scripts/calculate_scores.py --force

# API automatically serves updated scores
```

### Scenario 4: Fix Data Issues

**Goal:** Reprocess products with improved processors

```bash
# 1. Update processor code in app/processors/

# 2. Reprocess products
python scripts/process_products.py --force --limit 1000

# 3. Recalculate scores (depends on processing)
python scripts/calculate_scores.py --force --limit 1000
```

### Scenario 5: Multi-Computer Scraping

**Goal:** Distribute scraping across multiple computers

```bash
# On master computer: Calculate work distribution
python app/scraper/distribute_work.py --computers 3 --chunk-size 1000

# On Computer 1:
python app/scraper/monitor.py --details --offset 0 --limit 1000

# On Computer 2:
python app/scraper/monitor.py --details --offset 1000 --limit 1000

# On Computer 3:
python app/scraper/monitor.py --details --offset 2000 --limit 1000

# After all complete, process and score
python scripts/process_products.py
python scripts/calculate_scores.py
```

## Best Practices

### 1. Scraping

✅ **DO:**
- Use the monitor script for long sessions
- Start with small limits when testing
- Run during off-peak hours
- Check for errors in the logs

❌ **DON'T:**
- Run multiple scrapers simultaneously on same data
- Scrape too aggressively (respect rate limits)
- Ignore error messages

### 2. Processing

✅ **DO:**
- Process products soon after scraping
- Use `--limit` to test new processors
- Back up database before reprocessing all
- Review processed data for quality

❌ **DON'T:**
- Skip processing step
- Process before scraping completes
- Ignore processing errors

### 3. Scoring

✅ **DO:**
- Ensure products are processed first
- Review score distribution
- Test scoring changes on subset first
- Document scoring algorithm changes

❌ **DON'T:**
- Score unprocessed products
- Change weights without testing
- Skip validation of results

### 4. API

✅ **DO:**
- Keep API running continuously
- Monitor health endpoints
- Use proper error handling in frontend
- Implement pagination for large datasets

❌ **DON'T:**
- Restart API frequently (affects frontend)
- Run scraping through API endpoints
- Expose API without proper security

## Monitoring Progress

### Check Status

```bash
# Product scraping status
python -c "from app.models.database import SessionLocal; \
from app.models.product import ProductList; \
db = SessionLocal(); \
total = db.query(ProductList).count(); \
scraped = db.query(ProductList).filter_by(scraped=True).count(); \
print(f'Products: {scraped}/{total} scraped'); \
db.close()"

# Processing status
python scripts/process_products.py  # Shows statistics

# Scoring status
python scripts/calculate_scores.py  # Shows statistics
```

### Via API

```bash
# Product statistics
curl http://localhost:8000/api/v1/products/stats/overview

# Score statistics
curl http://localhost:8000/api/v1/scores/stats/overview
```

## Troubleshooting

### Issue: Scraper Times Out

**Solution:**
```bash
# Use monitor script for auto-restart
python app/scraper/monitor.py --details --max-restarts 20
```

### Issue: Processing Fails

**Solution:**
```bash
# Check product has details
# Process single product for debugging
python scripts/process_products.py --product-id 123
```

### Issue: Scoring Returns 0

**Solution:**
```bash
# Ensure product is processed
# Check if scorers are implemented
# Verify database has required data
```

### Issue: API Shows Old Data

**Solution:**
```bash
# API reads from database in real-time
# Just refresh the request
# No need to restart API
```

## Summary

This workflow provides a **simple, maintainable approach** to scraping, processing, scoring, and serving dog food product data:

1. **Scrape** manually when needed
2. **Process** to normalize data
3. **Score** to evaluate quality
4. **Serve** via API to frontend

Each step is independent, transparent, and easy to debug. No complex infrastructure required.