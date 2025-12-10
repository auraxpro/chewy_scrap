# Chewy.com Dog Food Scraper

A Python project to scrape dog food product data from chewy.com and calculate scores. This project uses Playwright with human-like behavior to bypass anti-bot systems.

## Project Structure

```
api/
├── config.py              # Configuration settings
├── database.py            # Database models and setup
├── scraper.py             # Playwright scraper with human-like behavior
├── main.py                # Main entry point
├── monitor_scraper.py     # Auto-restart monitor script
├── distribute_work.py     # Work distribution script for multi-computer scraping
├── export_data.py         # Export scraped data to JSON
├── import_data.py         # Import/merge data from JSON exports
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # PostgreSQL Docker setup
└── README.md              # This file
```

## Prerequisites

- Python 3.10.12
- Docker and Docker Compose
- Virtual environment (venv)

## Setup Instructions

### 1. Create and activate virtual environment

```bash
python3.10 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browsers

```bash
playwright install chromium
```

### 4. Start PostgreSQL database

```bash
docker-compose up -d
```

This will start a PostgreSQL container on port 5432 with:
- Database: `chewy_db`
- User: `chewy_user`
- Password: `chewy_password`

### 5. (Optional) Create .env file

Create a `.env` file in the project root if you want to customize database settings:

```
DATABASE_URL=postgresql://chewy_user:chewy_password@localhost:5432/chewy_db
POSTGRES_USER=chewy_user
POSTGRES_PASSWORD=chewy_password
POSTGRES_DB=chewy_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Usage

### 1. Scrape Product List

Scrape product URLs from listing pages:

```bash
python main.py
```

This will:
1. Initialize the database tables
2. Scrape all dog food product pages (1-138) from chewy.com
3. Extract product URLs and image URLs
4. Save them to PostgreSQL database

**Test mode** (scrape only first page):
```bash
python main.py --test
# or
python main.py -t
```

### 2. Scrape Product Details

After scraping the product list, scrape detailed product information:

```bash
python main.py --details
# or
python main.py -d
```

This will scrape all products that haven't been scraped yet (`scraped=False`).

**Limit the number of products to scrape:**
```bash
python main.py --details --limit 10
# or
python main.py -d -l 10
```

**Test mode** (scrape a single product by URL):
```bash
python main.py --details --test-url "https://www.chewy.com/american-journey-grain-free-salmon/dp/108423"
# or
python main.py -d -tu "https://www.chewy.com/american-journey-grain-free-salmon/dp/108423"
```

### 3. Auto-Restart Monitor (Recommended for Long-Running Scrapes)

The `monitor_scraper.py` script automatically monitors the scraper output and restarts it when timeout errors are detected. This is especially useful for long-running scraping sessions.

**Basic usage:**
```bash
python monitor_scraper.py --details
```

**With limit:**
```bash
python monitor_scraper.py --details --limit 100
```

**Monitor options:**
```bash
python monitor_scraper.py --details --max-restarts 20 --cooldown 10
```

- `--max-restarts N`: Maximum number of automatic restarts (default: 10)
- `--cooldown N`: Seconds to wait before restarting (default: 5)

**Features:**
- ✅ Real-time output monitoring
- ✅ Automatic detection of timeout errors
- ✅ Graceful process termination and restart
- ✅ Configurable restart limits and cooldown periods
- ✅ Timestamped logging of all events
- ✅ Works on both Unix and Windows systems

**Example output:**
```
[2024-01-15 10:30:45] ℹ️ Starting scraper: python main.py --details
[2024-01-15 10:35:12] ❌ Timeout error detected: timeout: Timed out receiving message from renderer
[2024-01-15 10:35:12] 🔄 Restarting scraper (attempt 1/10)...
[2024-01-15 10:35:17] ℹ️ Starting scraper: python main.py --details
```

### 4. Multi-Computer Scraping

When scraping large datasets, you can distribute the work across multiple computers to speed up the process.

#### Step 1: Distribute Work

On the master computer (with the full product list database), run:

```bash
python distribute_work.py --computers 3 --chunk-size 1200
```

This will show you the work assignments for each computer:
```
🖥️  Computer 1:
   Offset: 0
   Limit: 1200
   Command: python main.py --details --offset 0 --limit 1200

🖥️  Computer 2:
   Offset: 1200
   Limit: 1200
   Command: python main.py --details --offset 1200 --limit 1200

🖥️  Computer 3:
   Offset: 2400
   Limit: 1200
   Command: python main.py --details --offset 2400 --limit 1200
```

#### Step 2: Set Up Each Computer

On each computer:

1. **Copy the project files** (scraper.py, main.py, database.py, config.py, etc.)
2. **Set up the database** (each computer can have its own local database or connect to a shared one)
3. **Copy the product list** - Ensure each computer has the same `products_list` table with all products

#### Step 3: Run Scraping on Each Computer

On Computer 1:
```bash
python monitor_scraper.py --details --offset 0 --limit 1200
```

On Computer 2:
```bash
python monitor_scraper.py --details --offset 1200 --limit 1200
```

On Computer 3:
```bash
python monitor_scraper.py --details --offset 2400 --limit 1200
```

#### Step 4: Export Data from Each Computer

After scraping completes on each computer, export the data:

```bash
python export_data.py --output computer1_export.json
```

This creates a JSON file with all scraped products and their details.

#### Step 5: Import Data into Master Database

On the master computer, import data from each computer:

```bash
# Import from Computer 1
python import_data.py computer1_export.json

# Import from Computer 2
python import_data.py computer2_export.json

# Import from Computer 3
python import_data.py computer3_export.json
```

The import script will:
- ✅ Skip duplicate products (based on product_url)
- ✅ Update scraped flags
- ✅ Handle foreign key relationships correctly
- ✅ Show detailed import statistics

**Dry run (preview without importing):**
```bash
python import_data.py computer1_export.json --dry-run
```

#### Alternative: Shared Database Approach

If all computers can access the same database:

1. **Set up shared database** (PostgreSQL on a server accessible by all computers)
2. **Update config.py** on each computer to point to the shared database
3. **Run scraping with offsets** - Each computer scrapes different ranges
4. **No import needed** - Data is automatically in the shared database

**Advantages:**
- ✅ No need to export/import
- ✅ Real-time progress visibility
- ✅ Automatic conflict resolution

**Disadvantages:**
- ⚠️ Requires network access to shared database
- ⚠️ Potential database connection issues
- ⚠️ All computers must be online

### Database Schema

#### `products_list` table:
- `id`: Primary key (auto-increment)
- `product_url`: Product detail page URL (unique)
- `page_num`: Page number where the product was found
- `scraped`: Boolean flag indicating if product details have been scraped (default: False)
- `product_image_url`: URL of the product image

#### `product_details` table:
- `id`: Primary key (auto-increment)
- `product_id`: Foreign key to `products_list.id` (unique)
- `product_category`: Product category from breadcrumbs
- `product_name`: Product name
- `img_link`: Image URL (copied from product list)
- `product_url`: Product URL (copied from product list)
- `price`: Product price
- `size`: Product size
- `details`: Key benefits/details (text)
- `more_details`: Additional details including specifications (text)
- `ingredients`: Ingredients list (text)
- `caloric_content`: Caloric content information (text)
- `guaranteed_analysis`: Guaranteed analysis table (text)
- `feeding_instructions`: Feeding instructions (text)
- `transition_instructions`: Transition instructions (text)

### Check database

You can connect to the database to verify the data:

```bash
docker exec -it chewy_scraper_db psql -U chewy_user -d chewy_db
```

Then run SQL queries:
```sql
-- Check product list
SELECT COUNT(*) FROM products_list;
SELECT * FROM products_list LIMIT 10;

-- Check product details
SELECT COUNT(*) FROM product_details;
SELECT * FROM product_details LIMIT 10;

-- Check unscraped products
SELECT COUNT(*) FROM products_list WHERE scraped = false;

-- Join product list with details
SELECT pl.product_url, pd.product_name, pd.price, pd.size
FROM products_list pl
LEFT JOIN product_details pd ON pl.id = pd.product_id
LIMIT 10;
```

## Features

- **Human-like behavior**: Random delays, scrolling patterns, and realistic browser settings
- **Anti-bot bypass**: Uses Playwright with automation detection disabled
- **Duplicate prevention**: Checks for existing products before inserting
- **Error handling**: Continues scraping even if individual products fail
- **Progress tracking**: Prints progress information during scraping

## Notes

- The scraper runs with `headless=False` by default to better mimic human behavior. You can change this in `scraper.py` if needed.
- Scraping all 138 pages may take a significant amount of time due to human-like delays.
- Make sure Docker is running before starting the scraper.

## Product Detail Scraping

The product detail scraper extracts the following information from each product page:

1. **Product Category**: Extracted from breadcrumbs (third level)
2. **Product Name**: From the product title heading
3. **Image Link**: Copied from the product list
4. **Product URL**: Copied from the product list
5. **Price**: Current Chewy price
6. **Size**: Selected product size
7. **Details**: Key benefits and features (bullet points)
8. **More Details**: Product description and specifications table
9. **Ingredients**: Full ingredients list
10. **Caloric Content**: Calorie information per kg and cup
11. **Guaranteed Analysis**: Nutritional analysis table
12. **Feeding Instructions**: Feeding guide table and additional notes
13. **Transition Instructions**: Instructions for transitioning to this food

After successfully scraping a product, the `scraped` flag in `products_list` is automatically set to `true`.

## Next Steps

After scraping product details, you can:
1. Process data for scoring system
2. Calculate scores for each product
3. Analyze nutritional information
4. Generate reports

