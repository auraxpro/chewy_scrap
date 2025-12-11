"""
Processors module for the Dog Food Scoring API.

This module contains data processing and normalization components that transform
raw scraped data into standardized, analysis-ready formats.
"""

from app.processors.base_processor import BaseProcessor

__all__ = [
    "BaseProcessor",
]
