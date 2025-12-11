"""
Scoring service module for the Dog Food Scoring API.

This module provides business logic for scoring-related operations including
score calculation, retrieval, and statistics.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.config import (
    SCORE_WEIGHT_INGREDIENTS,
    SCORE_WEIGHT_NUTRITION,
    SCORE_WEIGHT_PRICE_VALUE,
    SCORE_WEIGHT_PROCESSING,
    SCORING_VERSION,
)
from app.models.product import ProductList
from app.models.score import ProductScore, ScoreComponent


class ScoringService:
    """
    Service class for scoring-related business logic.

    This class handles all scoring operations including score calculation,
    retrieval, filtering, and statistics generation.
    """

    def __init__(self, db: Session):
        """
        Initialize the scoring service.

        Args:
            db: Database session
        """
        self.db = db

    def get_score_by_id(self, score_id: int) -> Optional[ProductScore]:
        """
        Get a score by its ID.

        Args:
            score_id: Score ID

        Returns:
            ProductScore instance or None if not found
        """
        return (
            self.db.query(ProductScore)
            .options(joinedload(ProductScore.components))
            .filter(ProductScore.id == score_id)
            .first()
        )

    def get_score_by_product_id(self, product_id: int) -> Optional[ProductScore]:
        """
        Get the latest score for a product.

        Args:
            product_id: Product ID

        Returns:
            ProductScore instance or None if not found
        """
        return (
            self.db.query(ProductScore)
            .options(joinedload(ProductScore.components))
            .filter(ProductScore.product_id == product_id)
            .order_by(ProductScore.calculated_at.desc())
            .first()
        )

    def get_scores(
        self,
        page: int = 1,
        page_size: int = 50,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        score_version: Optional[str] = None,
        sort_by: str = "total_score",
        sort_order: str = "desc",
    ) -> Tuple[List[ProductScore], int]:
        """
        Get paginated list of scores with optional filters.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            min_score: Minimum score filter
            max_score: Maximum score filter
            score_version: Filter by score version
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Tuple of (list of scores, total count)
        """
        query = self.db.query(ProductScore).options(
            joinedload(ProductScore.components),
            joinedload(ProductScore.product),
        )

        # Apply filters
        if min_score is not None:
            query = query.filter(ProductScore.total_score >= min_score)
        if max_score is not None:
            query = query.filter(ProductScore.total_score <= max_score)
        if score_version:
            query = query.filter(ProductScore.score_version == score_version)

        # Apply sorting
        if hasattr(ProductScore, sort_by):
            sort_column = getattr(ProductScore, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        scores = query.offset(offset).limit(page_size).all()

        return scores, total

    def calculate_product_score(
        self, product_id: int, force_recalculate: bool = False
    ) -> Optional[ProductScore]:
        """
        Calculate or retrieve score for a product.

        Args:
            product_id: Product ID
            force_recalculate: Force recalculation even if score exists

        Returns:
            ProductScore instance or None if calculation failed
        """
        # Check if score already exists
        existing_score = self.get_score_by_product_id(product_id)
        if existing_score and not force_recalculate:
            return existing_score

        # Get product
        product = (
            self.db.query(ProductList)
            .options(joinedload(ProductList.details))
            .filter(ProductList.id == product_id)
            .first()
        )

        if not product or not product.details:
            return None

        # TODO: Implement actual scoring logic using scorer classes
        # For now, create a placeholder score
        total_score = 0.0
        components = []

        # Ingredient Quality Score
        from app.scoring.ingredient_quality_scorer import IngredientQualityScorer
        
        ingredient_scorer = IngredientQualityScorer(self.db, weight=SCORE_WEIGHT_INGREDIENTS)
        ingredient_score = ingredient_scorer.calculate_score(product)
        ingredient_details = ingredient_scorer.get_score_details(product)
        
        components.append(
            {
                "component_name": "ingredient_quality",
                "component_score": ingredient_score,
                "weight": SCORE_WEIGHT_INGREDIENTS,
                "weighted_score": ingredient_score * SCORE_WEIGHT_INGREDIENTS,
                "confidence": ingredient_scorer.get_confidence(product),
                "details": json.dumps(ingredient_details) if ingredient_details else None,
            }
        )
        total_score += ingredient_score * SCORE_WEIGHT_INGREDIENTS

        # Nutritional Value Score (placeholder)
        nutrition_score = self._calculate_nutrition_score(product)
        components.append(
            {
                "component_name": "nutritional_value",
                "component_score": nutrition_score,
                "weight": SCORE_WEIGHT_NUTRITION,
                "weighted_score": nutrition_score * SCORE_WEIGHT_NUTRITION,
                "confidence": 0.85,
            }
        )
        total_score += nutrition_score * SCORE_WEIGHT_NUTRITION

        # Processing Method Score (placeholder)
        processing_score = self._calculate_processing_score(product)
        components.append(
            {
                "component_name": "processing_method",
                "component_score": processing_score,
                "weight": SCORE_WEIGHT_PROCESSING,
                "weighted_score": processing_score * SCORE_WEIGHT_PROCESSING,
                "confidence": 0.75,
            }
        )
        total_score += processing_score * SCORE_WEIGHT_PROCESSING

        # Price-Value Score (placeholder)
        price_value_score = self._calculate_price_value_score(product)
        components.append(
            {
                "component_name": "price_value",
                "component_score": price_value_score,
                "weight": SCORE_WEIGHT_PRICE_VALUE,
                "weighted_score": price_value_score * SCORE_WEIGHT_PRICE_VALUE,
                "confidence": 0.70,
            }
        )
        total_score += price_value_score * SCORE_WEIGHT_PRICE_VALUE

        # Create or update score
        if existing_score and force_recalculate:
            # Update existing score
            existing_score.total_score = total_score
            existing_score.score_version = SCORING_VERSION
            existing_score.calculated_at = datetime.utcnow()
            existing_score.updated_at = datetime.utcnow()

            # Delete old components
            self.db.query(ScoreComponent).filter(
                ScoreComponent.score_id == existing_score.id
            ).delete()

            # Create new components
            for comp_data in components:
                component = ScoreComponent(score_id=existing_score.id, **comp_data)
                self.db.add(component)

            product_score = existing_score
        else:
            # Create new score
            product_score = ProductScore(
                product_id=product_id,
                total_score=total_score,
                score_version=SCORING_VERSION,
                calculated_at=datetime.utcnow(),
            )
            self.db.add(product_score)
            self.db.flush()

            # Create components
            for comp_data in components:
                component = ScoreComponent(score_id=product_score.id, **comp_data)
                self.db.add(component)

        # Commit changes
        self.db.commit()
        self.db.refresh(product_score)

        return product_score

    def calculate_batch_scores(
        self,
        product_ids: List[int],
        force_recalculate: bool = False,
    ) -> Dict:
        """
        Calculate scores for multiple products.

        Args:
            product_ids: List of product IDs
            force_recalculate: Force recalculation even if scores exist

        Returns:
            Dictionary with calculation results
        """
        results = {
            "total": len(product_ids),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        for product_id in product_ids:
            try:
                score = self.calculate_product_score(product_id, force_recalculate)
                if score:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(
                        {"product_id": product_id, "error": "Score calculation failed"}
                    )
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"product_id": product_id, "error": str(e)})

        return results

    def get_score_statistics(self) -> Dict:
        """
        Get scoring statistics.

        Returns:
            Dictionary containing various statistics
        """
        total_scored = self.db.query(ProductScore).count()

        if total_scored == 0:
            return {
                "total_scored_products": 0,
                "average_score": 0.0,
                "median_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0,
                "score_distribution": {},
                "component_averages": {},
                "latest_score_version": SCORING_VERSION,
            }

        # Average, min, max scores
        stats = self.db.query(
            func.avg(ProductScore.total_score),
            func.min(ProductScore.total_score),
            func.max(ProductScore.total_score),
        ).first()

        average_score = float(stats[0]) if stats[0] else 0.0
        min_score = float(stats[1]) if stats[1] else 0.0
        max_score = float(stats[2]) if stats[2] else 0.0

        # Median score (approximate)
        median_score = average_score  # Simplified

        # Score distribution
        score_ranges = [
            ("0-20", 0, 20),
            ("20-40", 20, 40),
            ("40-60", 40, 60),
            ("60-80", 60, 80),
            ("80-100", 80, 100),
        ]
        score_distribution = {}
        for range_name, min_val, max_val in score_ranges:
            count = (
                self.db.query(ProductScore)
                .filter(ProductScore.total_score >= min_val)
                .filter(
                    ProductScore.total_score < max_val
                    if max_val < 100
                    else ProductScore.total_score <= max_val
                )
                .count()
            )
            score_distribution[range_name] = count

        # Component averages
        component_averages = {}
        component_stats = (
            self.db.query(
                ScoreComponent.component_name,
                func.avg(ScoreComponent.component_score),
            )
            .group_by(ScoreComponent.component_name)
            .all()
        )
        for comp_name, avg_score in component_stats:
            component_averages[comp_name] = float(avg_score) if avg_score else 0.0

        return {
            "total_scored_products": total_scored,
            "average_score": average_score,
            "median_score": median_score,
            "min_score": min_score,
            "max_score": max_score,
            "score_distribution": score_distribution,
            "component_averages": component_averages,
            "latest_score_version": SCORING_VERSION,
        }

    def get_top_scored_products(
        self, limit: int = 10, category: Optional[str] = None
    ) -> List[ProductScore]:
        """
        Get top scored products.

        Args:
            limit: Number of products to return
            category: Optional category filter

        Returns:
            List of ProductScore instances
        """
        query = (
            self.db.query(ProductScore)
            .options(
                joinedload(ProductScore.product).joinedload(ProductList.details),
                joinedload(ProductScore.components),
            )
            .order_by(ProductScore.total_score.desc())
        )

        if category:
            from app.models.product import ProductDetails

            query = (
                query.join(ProductList)
                .join(ProductDetails)
                .filter(ProductDetails.normalized_category == category)
            )

        return query.limit(limit).all()

    # Placeholder scoring methods (to be replaced with actual scorer classes)

    def _calculate_ingredient_score(self, product: ProductList) -> float:
        """Placeholder for ingredient quality scoring."""
        # TODO: Implement actual ingredient scoring logic
        return 75.0

    def _calculate_nutrition_score(self, product: ProductList) -> float:
        """Placeholder for nutritional value scoring."""
        # TODO: Implement actual nutrition scoring logic
        return 80.0

    def _calculate_processing_score(self, product: ProductList) -> float:
        """Placeholder for processing method scoring."""
        # TODO: Implement actual processing scoring logic
        return 70.0

    def _calculate_price_value_score(self, product: ProductList) -> float:
        """Placeholder for price-value scoring."""
        # TODO: Implement actual price-value scoring logic
        return 72.0

    def delete_score(self, score_id: int) -> bool:
        """
        Delete a score and all related components.

        Args:
            score_id: Score ID

        Returns:
            True if successful, False otherwise
        """
        score = self.get_score_by_id(score_id)
        if score:
            self.db.delete(score)
            self.db.commit()
            return True
        return False
