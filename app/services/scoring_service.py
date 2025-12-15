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

from app.config import SCORING_VERSION
from app.models.product import ProcessedProduct, ProductList
from app.models.score import ProductScore, ScoreComponent
from app.scoring.base_score_calculator import BaseScoreCalculator


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
        self, product_id: int, force_recalculate: bool = False, ignore_existing_base_score: bool = False
    ) -> Optional[ProductScore]:
        """
        Calculate Base Score for a product using Phase 1 scoring system.
        
        This calculates the Base Score (intrinsic food quality) which is:
        - Calculated once and stored in the database
        - Never recalculated at runtime (unless force_recalculate=True or ignore_existing_base_score=True)
        - Based ONLY on food-intrinsic factors from processed_products table
        
        Args:
            product_id: Product ID
            force_recalculate: Force recalculation even if score exists
            ignore_existing_base_score: Ignore existing base_score in ProcessedProduct and recalculate

        Returns:
            ProductScore instance or None if calculation failed
        """
        # Get product with processed data
        product = (
            self.db.query(ProductList)
            .options(joinedload(ProductList.details))
            .filter(ProductList.id == product_id)
            .first()
        )

        if not product or not product.details:
            return None

        # Get ProcessedProduct - this is the only table we use for scoring
        processed_product = (
            self.db.query(ProcessedProduct)
            .filter(ProcessedProduct.product_detail_id == product.details.id)
            .first()
        )

        if not processed_product:
            return None

        # Calculate Base Score using BaseScoreCalculator
        base_score_calculator = BaseScoreCalculator(self.db)
        
        if ignore_existing_base_score:
            # Recalculate base_score regardless of existing value (for terminal commands)
            base_score = base_score_calculator.calculate_base_score(processed_product)
            
            # Update ProcessedProduct with new base_score
            if base_score is not None:
                processed_product.base_score = base_score
                self.db.add(processed_product)
                self.db.flush()
        else:
            # Use existing base_score if available, otherwise calculate
            if processed_product.base_score is not None:
                base_score = float(processed_product.base_score)
            else:
                base_score = base_score_calculator.calculate_base_score(processed_product)
                if base_score is not None:
                    processed_product.base_score = base_score
                    self.db.add(processed_product)
                    self.db.flush()

        if base_score is None:
            return None

        # Base Score is the total score for Phase 1
        # Phase 2 (dynamic handling deductions) is handled separately in the API
        total_score = base_score

        # Create component for base score breakdown
        components = []
        components.append(
            {
                "component_name": "base_score",
                "component_score": total_score,
                "weight": 1.0,
                "weighted_score": total_score,
                "confidence": 1.0,
                "details": json.dumps({
                    "food_category": processed_product.food_category.value if processed_product.food_category else None,
                    "sourcing_integrity": processed_product.sourcing_integrity.value if processed_product.sourcing_integrity else None,
                    "processing_method": processed_product.processing_adulteration_method.value if processed_product.processing_adulteration_method else None,
                    "nutritionally_adequate": processed_product.nutritionally_adequate,
                    "starchy_carb_pct": float(processed_product.starchy_carb_pct) if processed_product.starchy_carb_pct else None,
                }),
            }
        )

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
        ignore_existing_base_score: bool = False,
    ) -> Dict:
        """
        Calculate scores for multiple products.

        Args:
            product_ids: List of product IDs
            force_recalculate: Force recalculation even if scores exist
            ignore_existing_base_score: Ignore existing base_score and recalculate

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
                score = self.calculate_product_score(
                    product_id, 
                    force_recalculate=force_recalculate,
                    ignore_existing_base_score=ignore_existing_base_score
                )
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
