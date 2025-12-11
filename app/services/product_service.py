"""
Product service module for the Dog Food Scoring API.

This module provides business logic for product-related operations including
CRUD operations, search, filtering, and statistics.
"""

from typing import Dict, List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.product import ProductDetails, ProductList
from app.models.score import ProductScore


class ProductService:
    """
    Service class for product-related business logic.

    This class handles all product operations including retrieval,
    search, filtering, and statistics generation.
    """

    def __init__(self, db: Session):
        """
        Initialize the product service.

        Args:
            db: Database session
        """
        self.db = db

    def get_product_by_id(self, product_id: int) -> Optional[ProductList]:
        """
        Get a product by its ID.

        Args:
            product_id: Product ID

        Returns:
            ProductList instance or None if not found
        """
        return (
            self.db.query(ProductList)
            .options(joinedload(ProductList.details))
            .filter(ProductList.id == product_id)
            .first()
        )

    def get_product_by_url(self, product_url: str) -> Optional[ProductList]:
        """
        Get a product by its URL.

        Args:
            product_url: Product URL

        Returns:
            ProductList instance or None if not found
        """
        return (
            self.db.query(ProductList)
            .options(joinedload(ProductList.details))
            .filter(ProductList.product_url == product_url)
            .first()
        )

    def get_products(
        self,
        page: int = 1,
        page_size: int = 50,
        scraped: Optional[bool] = None,
        processed: Optional[bool] = None,
        scored: Optional[bool] = None,
        skipped: Optional[bool] = None,
    ) -> Tuple[List[ProductList], int]:
        """
        Get paginated list of products with optional filters.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            scraped: Filter by scraped status
            processed: Filter by processed status
            scored: Filter by scored status
            skipped: Filter by skipped status

        Returns:
            Tuple of (list of products, total count)
        """
        query = self.db.query(ProductList).options(joinedload(ProductList.details))

        # Apply filters
        if scraped is not None:
            query = query.filter(ProductList.scraped == scraped)
        if processed is not None:
            if processed:
                # Has details = processed
                query = query.join(ProductDetails)
            else:
                # No details = not processed
                query = query.outerjoin(ProductDetails).filter(
                    ProductDetails.id == None
                )
        if scored is not None:
            try:
                from app.models.score import ProductScore

                if scored:
                    query = query.join(ProductScore)
                else:
                    query = query.outerjoin(ProductScore).filter(
                        ProductScore.id == None
                    )
            except:
                pass
        if skipped is not None:
            query = query.filter(ProductList.skipped == skipped)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()

        return products, total

    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        processing_level: Optional[str] = None,
        scraped: Optional[bool] = None,
        scored: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[ProductList], int]:
        """
        Search and filter products with multiple criteria.

        Args:
            query: Search query for product name or ingredients
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_score: Minimum score filter
            max_score: Maximum score filter
            processing_level: Filter by processing level
            scraped: Filter by scraped status
            scored: Filter by scored status
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (list of products, total count)
        """
        base_query = self.db.query(ProductList).options(joinedload(ProductList.details))

        # Text search on product name and ingredients
        if query:
            search_filter = or_(
                ProductDetails.product_name.ilike(f"%{query}%"),
                ProductDetails.ingredients.ilike(f"%{query}%"),
            )
            base_query = base_query.join(ProductDetails).filter(search_filter)

        # Category filter
        if category:
            if not query:  # Only join if not already joined
                base_query = base_query.join(ProductDetails)
            base_query = base_query.filter(
                or_(
                    ProductDetails.product_category.ilike(f"%{category}%"),
                    ProductDetails.normalized_category == category,
                )
            )

        # Processing level filter
        if processing_level:
            if not query and not category:  # Only join if not already joined
                base_query = base_query.join(ProductDetails)
            base_query = base_query.filter(
                ProductDetails.processing_level == processing_level
            )

        # Price filter (note: price is stored as string, need to parse)
        if min_price is not None or max_price is not None:
            if not query and not category and not processing_level:
                base_query = base_query.join(ProductDetails)
            # This is a simple filter - in production, you'd want to parse the price string
            if min_price is not None:
                base_query = base_query.filter(ProductDetails.price.isnot(None))
            if max_price is not None:
                base_query = base_query.filter(ProductDetails.price.isnot(None))

        # Score filter
        if min_score is not None or max_score is not None:
            try:
                from app.models.score import ProductScore

                base_query = base_query.join(ProductScore)
                if min_score is not None:
                    base_query = base_query.filter(
                        ProductScore.total_score >= min_score
                    )
                if max_score is not None:
                    base_query = base_query.filter(
                        ProductScore.total_score <= max_score
                    )
            except:
                # If score tables don't exist, return empty result
                return [], 0

        # Status filters
        if scraped is not None:
            base_query = base_query.filter(ProductList.scraped == scraped)
        if scored is not None:
            try:
                from app.models.score import ProductScore

                if scored:
                    base_query = base_query.join(ProductScore)
                else:
                    base_query = base_query.outerjoin(ProductScore).filter(
                        ProductScore.id == None
                    )
            except:
                pass

        # Get total count
        total = base_query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        products = base_query.offset(offset).limit(page_size).all()

        return products, total

    def get_product_statistics(self) -> Dict:
        """
        Get overall product statistics.

        Returns:
            Dictionary containing various statistics
        """
        total_products = self.db.query(ProductList).count()
        scraped_products = (
            self.db.query(ProductList).filter(ProductList.scraped == True).count()
        )

        # Count products with details as "processed"
        processed_products = (
            self.db.query(ProductList)
            .join(ProductDetails)
            .filter(ProductList.scraped == True)
            .count()
        )

        # Count products with scores
        try:
            from app.models.score import ProductScore

            scored_products = self.db.query(ProductList).join(ProductScore).count()
        except:
            scored_products = 0

        # Category distribution
        category_stats = (
            self.db.query(
                ProductDetails.normalized_category, func.count(ProductDetails.id)
            )
            .filter(ProductDetails.normalized_category.isnot(None))
            .group_by(ProductDetails.normalized_category)
            .all()
        )
        categories = {cat: count for cat, count in category_stats if cat}

        # Average score
        avg_score_result = self.db.query(func.avg(ProductScore.total_score)).scalar()
        average_score = float(avg_score_result) if avg_score_result else None

        # Score distribution
        score_ranges = [
            ("0-20", 0, 20),
            ("20-40", 20, 40),
            ("40-60", 40, 60),
            ("60-80", 60, 80),
            ("80-100", 80, 100),
        ]
        score_distribution = {}
        try:
            from app.models.score import ProductScore

            for range_name, min_score, max_score in score_ranges:
                count = (
                    self.db.query(ProductScore)
                    .filter(ProductScore.total_score >= min_score)
                    .filter(
                        ProductScore.total_score < max_score
                        if max_score < 100
                        else ProductScore.total_score <= max_score
                    )
                    .count()
                )
                score_distribution[range_name] = count
        except:
            score_distribution = {range_name: 0 for range_name, _, _ in score_ranges}

        return {
            "total_products": total_products,
            "scraped_products": scraped_products,
            "processed_products": processed_products,
            "scored_products": scored_products,
            "categories": categories,
            "average_score": average_score,
            "score_distribution": score_distribution,
        }

    def get_unscraped_products(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[ProductList]:
        """
        Get products that haven't been scraped yet.

        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip

        Returns:
            List of unscraped products
        """
        query = (
            self.db.query(ProductList)
            .filter(ProductList.scraped == False)
            .filter(ProductList.skipped == False)
            .offset(offset)
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_unprocessed_products(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[ProductList]:
        """
        Get products that have been scraped but not processed.

        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip

        Returns:
            List of unprocessed products
        """
        # Get products that are scraped but don't have details yet
        query = (
            self.db.query(ProductList)
            .outerjoin(ProductDetails)
            .filter(ProductList.scraped == True)
            .filter(ProductDetails.id == None)
            .filter(ProductList.skipped == False)
            .offset(offset)
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_unscored_products(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[ProductList]:
        """
        Get products that have been processed but not scored.

        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip

        Returns:
            List of unscored products
        """
        # Get products with details but no scores
        try:
            from app.models.score import ProductScore

            query = (
                self.db.query(ProductList)
                .join(ProductDetails)
                .outerjoin(ProductScore)
                .filter(ProductList.scraped == True)
                .filter(ProductScore.id == None)
                .filter(ProductList.skipped == False)
                .offset(offset)
            )
        except:
            # If score tables don't exist, return empty
            return []

        if limit:
            query = query.limit(limit)

        return query.all()

    def mark_product_scraped(self, product_id: int) -> bool:
        """
        Mark a product as scraped.

        Args:
            product_id: Product ID

        Returns:
            True if successful, False otherwise
        """
        product = self.get_product_by_id(product_id)
        if product:
            product.scraped = True
            self.db.commit()
            return True
        return False

    def mark_product_processed(self, product_id: int) -> bool:
        """
        Mark a product as processed (kept for compatibility).

        NOTE: In current database structure, a product is considered
        "processed" if it has details.

        Args:
            product_id: Product ID

        Returns:
            True if product has details, False otherwise
        """
        product = self.get_product_by_id(product_id)
        if product and product.details:
            return True
        return False

    def mark_product_scored(self, product_id: int) -> bool:
        """
        Mark a product as scored (kept for compatibility).

        NOTE: In current database structure, a product is considered
        "scored" if it has a ProductScore record.

        Args:
            product_id: Product ID

        Returns:
            True if product has a score, False otherwise
        """
        try:
            from app.models.score import ProductScore

            product = self.get_product_by_id(product_id)
            if product:
                score = (
                    self.db.query(ProductScore)
                    .filter(ProductScore.product_id == product_id)
                    .first()
                )
                return score is not None
        except:
            pass
        return False

    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product and all related data.

        Args:
            product_id: Product ID

        Returns:
            True if successful, False otherwise
        """
        product = self.get_product_by_id(product_id)
        if product:
            self.db.delete(product)
            self.db.commit()
            return True
        return False

    def get_products_by_category(
        self, category: str, page: int = 1, page_size: int = 50
    ) -> Tuple[List[ProductList], int]:
        """
        Get products by category.

        Args:
            category: Category to filter by
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (list of products, total count)
        """
        query = (
            self.db.query(ProductList)
            .join(ProductDetails)
            .filter(ProductDetails.product_category.ilike(f"%{category}%"))
            .options(joinedload(ProductList.details))
        )

        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()

        return products, total
