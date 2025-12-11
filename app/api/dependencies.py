"""
API dependencies for the Dog Food Scoring API.

This module provides dependency injection functions for FastAPI endpoints.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.product_service import ProductService
from app.services.scoring_service import ScoringService

# ============================================================================
# Database Dependencies
# ============================================================================


def get_database() -> Generator[Session, None, None]:
    """
    Get database session dependency.

    Yields:
        Database session

    Example:
        ```python
        @app.get("/products")
        def get_products(db: Session = Depends(get_database)):
            return db.query(Product).all()
        ```
    """
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Service Dependencies
# ============================================================================


def get_product_service(db: Session = Depends(get_database)) -> ProductService:
    """
    Get product service dependency.

    Args:
        db: Database session from dependency injection

    Returns:
        ProductService instance

    Example:
        ```python
        @app.get("/products/{product_id}")
        def get_product(
            product_id: int,
            product_service: ProductService = Depends(get_product_service)
        ):
            return product_service.get_product_by_id(product_id)
        ```
    """
    return ProductService(db)


def get_scoring_service(db: Session = Depends(get_database)) -> ScoringService:
    """
    Get scoring service dependency.

    Args:
        db: Database session from dependency injection

    Returns:
        ScoringService instance

    Example:
        ```python
        @app.post("/scores/calculate")
        def calculate_score(
            product_id: int,
            scoring_service: ScoringService = Depends(get_scoring_service)
        ):
            return scoring_service.calculate_product_score(product_id)
        ```
    """
    return ScoringService(db)


# ============================================================================
# Pagination Dependencies
# ============================================================================


def get_pagination_params(
    page: int = 1,
    page_size: int = 50,
) -> dict:
    """
    Get pagination parameters with validation.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Dictionary with validated pagination parameters

    Raises:
        HTTPException: If pagination parameters are invalid

    Example:
        ```python
        @app.get("/products")
        def get_products(
            pagination: dict = Depends(get_pagination_params)
        ):
            page = pagination["page"]
            page_size = pagination["page_size"]
            # ... use pagination
        ```
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be greater than 0",
        )

    if page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be greater than 0",
        )

    if page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size cannot exceed 100",
        )

    return {"page": page, "page_size": page_size}
