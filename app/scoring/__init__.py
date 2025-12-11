"""
Scoring module for the Dog Food Scoring API.

This module contains the scoring system that evaluates dog food products
based on multiple criteria including ingredients, nutrition, processing,
and price-value ratio.
"""

from app.scoring.base_scorer import BaseScorer

__all__ = [
    "BaseScorer",
]
