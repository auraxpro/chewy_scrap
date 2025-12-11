# CLI Usage Guide

## 🎯 Quick Start

The Dog Food Scoring API provides a unified CLI tool for all manual operations.

### Running Commands

You can run the CLI in two ways:

**Option 1: Direct wrapper (Recommended)**
```bash
python cli.py [command] [options]
```

**Option 2: Via scripts directory**
```bash
python scripts/main.py [command] [options]
```

Both methods work exactly the same way!

---

## 📋 Available Commands

### Show Help

```bash
python cli.py --help
```

Shows all available commands and options.

### Show Statistics

```bash
python cli.py --stats
```

Displays comprehensive statistics with progress bars:
- Total products
- Scraping progress
- Processing progress
- Scoring progress
- Score statistics (if available)

---

## 🕷️ Scraping Commands

### Scrape Product List

```bash
# Scrape all pages (1-138)
python cli.py --scrape

# Test mode (page 1 only)
python cli.py --scrape --test
```

### Scrape Product Details

```bash
# Scrape all unscraped products
python cli.py --scrape --details

# Scrape with limit
python cli.py --scrape --details --limit 100

# Scrape from offset
python cli.py --scrape --details --offset 500 --limit 100

# Test mode (first 5 products)
python cli.py --scrape --details --test

# Test single product by URL
python cli.py --scrape --details --test-url "https://www.chewy.com/product/dp/12345"
```

---

## 🔧 Processing Commands

### Process Products

```bash
# Process all unprocessed products
python cli.py --process

# Process with limit
python cli.py --process --limit 100

# Process from offset
python cli.py --process --offset 500 --limit 100

# Process single product by ID
python cli.py --process --product-id 123

# Force reprocess (even if already processed)
python cli.py --process --force --limit 50
```

**Note:** Specific processors are not fully implemented yet. Products will be marked as processed but actual normalization logic needs to be added.

---

## 📊 Scoring Commands

### Calculate Scores

```bash
# Score all unscored products
python cli.py --score

# Score with limit
python cli.py --score --limit 100

# Score from offset
python cli.py --score --offset 500 --limit 100

# Score single product by ID
python cli.py --score --product-id 123

# Force recalculate (even if already scored)
python cli.py --score --force --limit 50
```

**Note:** Currently using placeholder scoring logic. Implement specific scorers for real scores.

---

## 🚀 Complete Pipeline

### Run Everything

```bash
# Run complete pipeline: Scrape → Process → Score
python cli.py --all

# With limit (recommended for testing)
python cli.py --all --limit 10

# Test mode
python cli.py --all --test
```

The `--all` command will:
1. Scrape product details
2. Process the products
3. Calculate scores
4. Show final statistics

---

## 🎛️ Command Options

### Global Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--help` | `-h` | Show help message | `python cli.py --help` |
| `--limit N` | `-l N` | Limit to N items | `python cli.py --scrape --details --limit 100` |
| `--offset N` | `-o N` | Start from offset N | `python cli.py --process --offset 500 --limit 100` |
| `--force` | `-f` | Force re-processing/scoring | `python cli.py --score --force --limit 50` |
| `--test` | `-t` | Test mode (limited scope) | `python cli.py --scrape --details --test` |
| `--product-id N` | `-pid N` | Process/score single product | `python cli.py --score --product-id 123` |
| `--test-url URL` | `-tu URL` | Test scrape single URL | `python cli.py --scrape --details --test-url "..."` |

### Command Flags

| Command | Short | Description |
|---------|-------|-------------|
| `--scrape` | `-s` | Scrape product data |
| `--details` | `-d` | Scrape product details (use with --scrape) |
| `--process` | `-p` | Process and normalize data |
| `--score` | `-sc` | Calculate quality scores |
| `--all` | `-a` | Run complete pipeline |
| `--stats` | | Show statistics only |

---

## 📖 Common Scenarios

### Scenario 1: First Time Setup

```bash
# 1. Check current status
python cli.py --stats

# 2. Scrape product list
python cli.py --scrape

# 3. Scrape product details (in batches)
python cli.py --scrape --details --limit 500

# 4. Process products
python cli.py --process

# 5. Calculate scores
python cli.py --score

# 6. Check final status
python cli.py --stats
```

### Scenario 2: Quick Test

```bash
# Test with 5 products
python cli.py --scrape --details --test
python cli.py --process --limit 5
python cli.py --score --limit 5
python cli.py --stats
```

### Scenario 3: Update Existing Data

```bash
# Scrape new products
python cli.py --scrape --details --limit 100

# Process them
python cli.py --process --limit 100

# Score them
python cli.py --score --limit 100
```

### Scenario 4: Recalculate Scores

```bash
# After updating scoring algorithm
python cli.py --score --force --limit 1000
```

### Scenario 5: Work on Single Product

```bash
# Scrape
python cli.py --scrape --details --test-url "https://www.chewy.com/product/dp/12345"

# Process
python cli.py --process --product-id 123

# Score
python cli.py --score --product-id 123
```

### Scenario 6: Complete Pipeline Test

```bash
# Run everything on limited dataset
python cli.py --all --test
```

---

## 🔍 Understanding Output

### Progress Indicators

```
📊 Found 100 product(s) to process

[1/100] Processing product 123
  📦 American Journey Grain-Free Salmon & Sweet Potato...
  ✅ Marked as processed

[2/100] Processing product 124
  📦 Blue Buffalo Life Protection Formula Adult Chicken...
  ✅ Marked as processed
```

### Progress Bars

```
Scraping Progress:   [████████████████████] 100.0%
Processing Progress: [████████████░░░░░░░░] 65.0%
Scoring Progress:    [████████░░░░░░░░░░░░] 40.0%
```

### Statistics Display

```
📊 Overall Statistics:
   Total products: 3500

   ├─ Scraped: 3500/3500
   │  └─ Unscraped: 0

   ├─ Processed: 2275/3500
   │  └─ Unprocessed: 1225

   └─ Scored: 1400/2275
      └─ Unscored: 875

   📈 Score Statistics:
      Average: 75.50/100
      Min: 35.00/100
      Max: 95.00/100
```

---

## ⚠️ Important Notes

### 1. API Independence

The CLI and API are **completely separate**:
- CLI operations write to the database
- API reads from the database
- You can run either independently
- No need to restart API after CLI operations

### 2. Processing Order

Follow this order for best results:
1. **Scrape** first (collect data)
2. **Process** second (normalize data)
3. **Score** third (calculate scores)

### 3. Using Limits

Always use `--limit` when testing:
```bash
# Good for testing
python cli.py --all --limit 10

# Be careful with full runs
python cli.py --all  # This will take a LONG time!
```

### 4. Force Flags

Use `--force` carefully:
```bash
# This will recalculate ALL scores (slow!)
python cli.py --score --force

# Better: limit the scope
python cli.py --score --force --limit 100
```

### 5. Error Handling

If a command fails:
1. Check the error message
2. Run `python cli.py --stats` to see current state
3. Use `--limit` to test on smaller dataset
4. Check individual product with `--product-id`

---

## 🐛 Troubleshooting

### Module Not Found Error

```bash
# Error: No module named 'app'

# Solution: Run from api/ directory
cd /path/to/api
python cli.py --help
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker ps

# Restart database
docker-compose restart

# Reinitialize
python3 -c "from app.models.database import init_db; init_db()"
```

### Import Errors in Scraper

```bash
# Run the import checker
python check_imports.py

# If issues found, the checker will show which files need updating
```

### Permission Denied

```bash
# Make sure you're in the right directory
pwd  # Should show /path/to/api

# Check Python environment
which python  # Should show .venv/bin/python if using venv
```

---

## 💡 Pro Tips

1. **Always check stats first**
   ```bash
   python cli.py --stats
   ```

2. **Test before full run**
   ```bash
   python cli.py --all --test
   ```

3. **Use limits for safety**
   ```bash
   python cli.py --scrape --details --limit 100
   ```

4. **Monitor long operations**
   - Use auto-restart monitor for long scraping sessions
   - Check logs for errors
   - Run `--stats` periodically to see progress

5. **Batch operations**
   ```bash
   # Process in batches of 500
   python cli.py --process --offset 0 --limit 500
   python cli.py --process --offset 500 --limit 500
   python cli.py --process --offset 1000 --limit 500
   ```

---

## 🔗 Related Documentation

- **QUICK_REFERENCE.md** - Quick command reference
- **README.md** - Full project documentation
- **GETTING_STARTED.md** - Setup guide
- **WORKFLOW.md** - Complete workflow guide

---

## 🎯 Summary

```bash
# Most common commands:

# Check status
python cli.py --stats

# Scrape data
python cli.py --scrape --details --limit 100

# Process data
python cli.py --process

# Calculate scores
python cli.py --score

# Do everything
python cli.py --all --test

# Get help
python cli.py --help
```

**Remember:** All CLI operations are independent from the API server! 🚀