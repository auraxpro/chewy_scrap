"""
Configuration module for the Dog Food Scoring API.

This module loads and manages all configuration settings from environment
variables with sensible defaults for development.
"""

import os
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# API Settings
# ============================================================================

API_TITLE = os.getenv("API_TITLE", "Dog Food Scoring API")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
API_DESCRIPTION = """
A comprehensive API for scraping, processing, scoring, and serving dog food product data.

## Features

* **Product Management**: Access detailed dog food product information
* **Scoring System**: Get quality scores based on multiple criteria
* **Search & Filter**: Find products by category, ingredients, price, etc.
* **Scraping Tools**: Built-in web scraping for data collection
* **Processing Pipeline**: Data normalization and analysis tools

## Scoring Criteria

Products are scored based on:
- Ingredient Quality (meat content, whole foods, etc.)
- Nutritional Value (protein, fat, vitamins, minerals)
- Processing Method (raw, freeze-dried, kibble, etc.)
- Price-Value Ratio (cost per serving vs. quality)
"""

DEBUG_MODE = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ============================================================================
# Database Settings
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://chewy_user:chewy_password@localhost:5432/chewy_db",
)

POSTGRES_USER = os.getenv("POSTGRES_USER", "chewy_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "chewy_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "chewy_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# ============================================================================
# CORS Settings
# ============================================================================

CORS_ORIGINS_STR = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:8000",
)
CORS_ORIGINS: List[str] = [origin.strip() for origin in CORS_ORIGINS_STR.split(",")]

# ============================================================================
# Scoring Settings
# ============================================================================

# Scoring weights (should sum to 1.0)
SCORE_WEIGHT_INGREDIENTS = float(os.getenv("SCORE_WEIGHT_INGREDIENTS", "0.35"))
SCORE_WEIGHT_NUTRITION = float(os.getenv("SCORE_WEIGHT_NUTRITION", "0.30"))
SCORE_WEIGHT_PROCESSING = float(os.getenv("SCORE_WEIGHT_PROCESSING", "0.20"))
SCORE_WEIGHT_PRICE_VALUE = float(os.getenv("SCORE_WEIGHT_PRICE_VALUE", "0.15"))

SCORING_VERSION = os.getenv("SCORING_VERSION", "1.0.0")

# ============================================================================
# Scraper Settings
# ============================================================================

SCRAPER_BASE_URL = os.getenv("SCRAPER_BASE_URL", "https://www.chewy.com/b/food-332")
SCRAPER_USER_AGENT = os.getenv(
    "SCRAPER_USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
)
SCRAPER_HEADLESS = os.getenv("SCRAPER_HEADLESS", "False").lower() in (
    "true",
    "1",
    "yes",
)
SCRAPER_TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "30"))

# ============================================================================
# Pagination Settings
# ============================================================================

DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))

# ============================================================================
# Logging Settings
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv(
    "LOG_FORMAT",
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
