"""
Scraper module for the Dog Food Scoring API.

This module contains all scraping functionality including the main Chewy scraper,
monitoring utilities, work distribution, and data import/export tools.
"""

from app.scraper.chewy_scraper import ChewyScraperUCD

__all__ = [
    "ChewyScraperUCD",
]
