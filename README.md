# Chewy.com Dog Food Scraper

A Python project to scrape dog food product data from chewy.com and calculate scores. This project uses Playwright with human-like behavior to bypass anti-bot systems.

## Project Structure

```
api/
├── config.py              # Configuration settings
├── database.py            # Database models and setup
├── scraper.py             # Playwright scraper with human-like behavior
├── main.py                # Main entry point
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

### Run the scraper

```bash
python main.py
```

This will:
1. Initialize the database tables
2. Scrape all dog food product pages (1-138) from chewy.com
3. Extract product URLs and image URLs
4. Save them to PostgreSQL database

### Database Schema

The `products` table has the following columns:
- `id`: Primary key (auto-increment)
- `product_url`: Product detail page URL (unique)
- `page_num`: Page number where the product was found
- `scraped`: Boolean flag indicating if product details have been scraped (default: False)
- `product_image_url`: URL of the product image

### Check database

You can connect to the database to verify the data:

```bash
docker exec -it chewy_scraper_db psql -U chewy_user -d chewy_db
```

Then run SQL queries:
```sql
SELECT COUNT(*) FROM products;
SELECT * FROM products LIMIT 10;
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

## Next Steps

After detecting and saving the product list, you can:
1. Scrape individual product details
2. Process data for scoring system
3. Calculate scores for each product

