"""
Products API endpoints for the Dog Food Scoring API.

This module provides REST API endpoints for product-related operations
including retrieval, search, filtering, and statistics.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_database,
    get_pagination_params,
    get_product_service,
)
from app.schemas.product import (
    ProductDetailResponse,
    ProductListPaginatedResponse,
    ProductListResponse,
    ProductResponse,
    ProductSearchRequest,
    ProductStatsResponse,
)
from app.services.product_service import ProductService

router = APIRouter()


@router.get(
    "/",
    response_model=ProductListPaginatedResponse,
    summary="Get all products",
    description="Retrieve a paginated list of all products with optional filters.",
)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    scraped: Optional[bool] = Query(None, description="Filter by scraped status"),
    processed: Optional[bool] = Query(None, description="Filter by processed status"),
    scored: Optional[bool] = Query(None, description="Filter by scored status"),
    skipped: Optional[bool] = Query(None, description="Filter by skipped status"),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Get paginated list of products.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        scraped: Filter by scraped status
        processed: Filter by processed status
        scored: Filter by scored status
        skipped: Filter by skipped status
        product_service: Product service from dependency injection

    Returns:
        Paginated list of products
    """
    products, total = product_service.get_products(
        page=page,
        page_size=page_size,
        scraped=scraped,
        processed=processed,
        scored=scored,
        skipped=skipped,
    )

    total_pages = (total + page_size - 1) // page_size

    # Convert products to response format
    product_responses = []
    for product in products:
        score = None
        try:
            from app.models.score import ProductScore

            product_score = (
                product_service.db.query(ProductScore)
                .filter(ProductScore.product_id == product.id)
                .first()
            )
            if product_score:
                score = product_score.total_score
        except:
            pass

        product_response = ProductResponse(
            product=ProductListResponse.model_validate(product),
            details=ProductDetailResponse.model_validate(product.details)
            if product.details
            else None,
            score=score,
        )
        product_responses.append(product_response)

    return ProductListPaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        products=product_responses,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieve detailed information about a specific product.",
)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    """
    Get a product by its ID.

    Args:
        product_id: Product ID
        product_service: Product service from dependency injection

    Returns:
        Product information with details and score

    Raises:
        HTTPException: If product not found
    """
    product = product_service.get_product_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    score = None
    try:
        from app.models.score import ProductScore

        product_score = (
            product_service.db.query(ProductScore)
            .filter(ProductScore.product_id == product.id)
            .first()
        )
        if product_score:
            score = product_score.total_score
    except:
        pass

    return ProductResponse(
        product=ProductListResponse.model_validate(product),
        details=ProductDetailResponse.model_validate(product.details)
        if product.details
        else None,
        score=score,
    )


@router.post(
    "/search",
    response_model=ProductListPaginatedResponse,
    summary="Search products",
    description="Search and filter products with multiple criteria.",
)
async def search_products(
    search_request: ProductSearchRequest,
    product_service: ProductService = Depends(get_product_service),
):
    """
    Search products with filters.

    Args:
        search_request: Search request with filters
        product_service: Product service from dependency injection

    Returns:
        Paginated list of matching products
    """
    products, total = product_service.search_products(
        query=search_request.query,
        category=search_request.category,
        min_price=search_request.min_price,
        max_price=search_request.max_price,
        min_score=search_request.min_score,
        max_score=search_request.max_score,
        processing_level=search_request.processing_level,
        scraped=search_request.scraped,
        scored=search_request.scored,
        page=search_request.page,
        page_size=search_request.page_size,
    )

    total_pages = (total + search_request.page_size - 1) // search_request.page_size

    # Convert products to response format
    product_responses = []
    for product in products:
        score = None
        try:
            from app.models.score import ProductScore

            product_score = (
                product_service.db.query(ProductScore)
                .filter(ProductScore.product_id == product.id)
                .first()
            )
            if product_score:
                score = product_score.total_score
        except:
            pass

        product_response = ProductResponse(
            product=ProductListResponse.model_validate(product),
            details=ProductDetailResponse.model_validate(product.details)
            if product.details
            else None,
            score=score,
        )
        product_responses.append(product_response)

    return ProductListPaginatedResponse(
        total=total,
        page=search_request.page,
        page_size=search_request.page_size,
        total_pages=total_pages,
        products=product_responses,
    )


@router.get(
    "/category/{category}",
    response_model=ProductListPaginatedResponse,
    summary="Get products by category",
    description="Retrieve products filtered by category.",
)
async def get_products_by_category(
    category: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    product_service: ProductService = Depends(get_product_service),
):
    """
    Get products by category.

    Args:
        category: Category to filter by
        page: Page number (1-indexed)
        page_size: Number of items per page
        product_service: Product service from dependency injection

    Returns:
        Paginated list of products in the category
    """
    products, total = product_service.get_products_by_category(
        category=category,
        page=page,
        page_size=page_size,
    )

    total_pages = (total + page_size - 1) // page_size

    # Convert products to response format
    product_responses = []
    for product in products:
        score = None
        try:
            from app.models.score import ProductScore

            product_score = (
                product_service.db.query(ProductScore)
                .filter(ProductScore.product_id == product.id)
                .first()
            )
            if product_score:
                score = product_score.total_score
        except:
            pass

        product_response = ProductResponse(
            product=ProductListResponse.model_validate(product),
            details=ProductDetailResponse.model_validate(product.details)
            if product.details
            else None,
            score=score,
        )
        product_responses.append(product_response)

    return ProductListPaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        products=product_responses,
    )


@router.get(
    "/stats/overview",
    response_model=ProductStatsResponse,
    summary="Get product statistics",
    description="Retrieve overall statistics about products in the database.",
)
async def get_product_statistics(
    product_service: ProductService = Depends(get_product_service),
):
    """
    Get product statistics.

    Args:
        product_service: Product service from dependency injection

    Returns:
        Product statistics including counts and distributions
    """
    stats = product_service.get_product_statistics()
    return ProductStatsResponse(**stats)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Delete a product and all related data.",
)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    """
    Delete a product.

    Args:
        product_id: Product ID to delete
        product_service: Product service from dependency injection

    Raises:
        HTTPException: If product not found
    """
    success = product_service.delete_product(product_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    return None
