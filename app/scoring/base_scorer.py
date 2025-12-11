"""
Base scorer module for the Dog Food Scoring API.

This module provides an abstract base class for all scoring components
that evaluate dog food products based on specific criteria.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.product import ProductDetails, ProductList
from app.models.score import ProductScore, ScoreComponent


class BaseScorer(ABC):
    """
    Abstract base class for scoring components.

    All scorers should inherit from this class and implement the
    calculate_score() method to perform their specific scoring logic.
    """

    def __init__(self, db: Session, weight: float = 0.25):
        """
        Initialize the scorer.

        Args:
            db: Database session for accessing product data
            weight: Weight of this scorer in the overall score (0.0-1.0)
        """
        self.db = db
        self.weight = weight
        self._validate_weight()

    def _validate_weight(self) -> None:
        """Validate that weight is between 0 and 1."""
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {self.weight}")

    @abstractmethod
    def calculate_score(self, product: ProductList) -> float:
        """
        Calculate the score for a product.

        This method must be implemented by all subclasses.

        Args:
            product: ProductList instance to score

        Returns:
            Score value between 0.0 and 100.0

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement calculate_score()")

    @abstractmethod
    def get_component_name(self) -> str:
        """
        Get the name of this scoring component.

        Returns:
            Component name (e.g., 'ingredient_quality', 'nutritional_value')
        """
        raise NotImplementedError("Subclasses must implement get_component_name()")

    def can_score(self, product: ProductList) -> bool:
        """
        Check if the product can be scored.

        Default implementation checks if product has been scraped,
        processed, and has details available.

        Args:
            product: ProductList instance to check

        Returns:
            True if product can be scored, False otherwise
        """
        return (
            product.scraped
            and not product.skipped
            and product.processed
            and product.details is not None
        )

    def get_score_details(self, product: ProductList) -> Optional[Dict[str, Any]]:
        """
        Get detailed breakdown of the score calculation.

        Subclasses can override this to provide detailed scoring information.

        Args:
            product: ProductList instance

        Returns:
            Dictionary with detailed scoring breakdown, or None
        """
        return None

    def get_confidence(self, product: ProductList) -> float:
        """
        Get confidence level for the score.

        Subclasses can override this to provide confidence metrics.

        Args:
            product: ProductList instance

        Returns:
            Confidence level between 0.0 and 1.0
        """
        return 1.0

    def calculate_weighted_score(self, product: ProductList) -> float:
        """
        Calculate the weighted score for a product.

        Args:
            product: ProductList instance to score

        Returns:
            Weighted score (score * weight)
        """
        score = self.calculate_score(product)
        return score * self.weight

    def validate_score(self, score: float) -> float:
        """
        Validate and clamp score to valid range.

        Args:
            score: Score to validate

        Returns:
            Validated score between 0.0 and 100.0
        """
        if score < 0.0:
            return 0.0
        if score > 100.0:
            return 100.0
        return score

    def score_batch(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Score multiple products in batch.

        Args:
            limit: Maximum number of products to score
            offset: Number of products to skip

        Returns:
            Dictionary containing batch scoring results
        """
        query = (
            self.db.query(ProductList)
            .filter(ProductList.scraped == True)
            .filter(ProductList.skipped == False)
            .filter(ProductList.processed == True)
            .offset(offset)
        )

        if limit:
            query = query.limit(limit)

        products = query.all()

        results = {
            "total_scored": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "average_score": 0.0,
        }

        total_score = 0.0

        for product in products:
            try:
                if self.can_score(product):
                    score = self.calculate_score(product)
                    total_score += score
                    results["successful"] += 1
                    results["total_scored"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"product_id": product.id, "error": str(e)})

        if results["successful"] > 0:
            results["average_score"] = total_score / results["successful"]

        return results

    def get_description(self) -> str:
        """
        Get the scorer description.

        Returns:
            Description of what the scorer evaluates
        """
        return self.__doc__ or "No description available"

    def validate_input(self, product: ProductList) -> bool:
        """
        Validate that the product has required data for scoring.

        Args:
            product: ProductList instance to validate

        Returns:
            True if valid, False otherwise
        """
        if not product.details:
            return False

        # Check if product details exist
        if not product.details.product_name:
            return False

        return True

    def log_scoring(
        self, product: ProductList, score: float, message: str = ""
    ) -> None:
        """
        Log scoring information.

        Args:
            product: ProductList instance being scored
            score: Calculated score
            message: Additional log message
        """
        component_name = self.get_component_name()
        msg = f"Product ID {product.id} - {component_name}: {score:.2f}"
        if message:
            msg += f" ({message})"
        print(f"[{self.__class__.__name__}] {msg}")

    def get_weight(self) -> float:
        """
        Get the weight of this scorer.

        Returns:
            Weight value
        """
        return self.weight

    def set_weight(self, weight: float) -> None:
        """
        Set the weight of this scorer.

        Args:
            weight: New weight value (0.0-1.0)

        Raises:
            ValueError: If weight is not between 0.0 and 1.0
        """
        self.weight = weight
        self._validate_weight()
