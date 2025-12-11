"""
Scores API endpoints for the Dog Food Scoring API.

This module provides REST API endpoints for score-related operations
including score calculation, retrieval, filtering, and statistics.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_scoring_service
from app.schemas.score import (
    BatchCalculateScoreRequest,
    CalculateScoreRequest,
    ScoreResponse,
    ScoreStatsResponse,
    ScoreWithProductResponse,
    TopScoredProductsResponse,
)
from app.services.scoring_service import ScoringService

router = APIRouter()


@router.get(
    "/{score_id}",
    response_model=ScoreResponse,
    summary="Get score by ID",
    description="Retrieve detailed score information by score ID.",
)
async def get_score(
    score_id: int,
    scoring_service: ScoringService = Depends(get_scoring_service),
):
    """
    Get a score by its ID.

    Args:
        score_id: Score ID
        scoring_service: Scoring service from dependency injection

    Returns:
        Score information with component breakdown

    Raises:
        HTTPException: If score not found
    """
    score = scoring_service.get_score_by_id(score_id)

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score with ID {score_id} not found",
        )

    return ScoreResponse.model_validate(score)


@router.get(
    "/product/{product_id}",
    response_model=ScoreResponse,
    summary="Get score by product ID",
    description="Retrieve the latest score for a specific product.",
)
async def get_score_by_product(
    product_id: int,
    scoring_service: ScoringService = Depends(get_scoring_service),
):
    """
    Get the latest score for a product.

    Args:
        product_id: Product ID
        scoring_service: Scoring service from dependency injection

    Returns:
        Score information with component breakdown

    Raises:
        HTTPException: If score not found
    """
    score = scoring_service.get_score_by_product_id(product_id)

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No score found for product ID {product_id}",
        )

    return ScoreResponse.model_validate(score)


@router.post(
    "/calculate",
    response_model=ScoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate product score",
    description="Calculate or recalculate score for a specific product.",
)
async def calculate_score(
    request: CalculateScoreRequest,
    scoring_service: ScoringService = Depends(get_scoring_service),
):
    """
    Calculate score for a product.

    Args:
        request: Score calculation request
        scoring_service: Scoring service from dependency injection

    Returns:
        Calculated score with component breakdown

    Raises:
        HTTPException: If product not found or calculation fails
    """
    score = scoring_service.calculate_product_score(
        product_id=request.product_id,
        force_recalculate=request.force_recalculate,
    )

    if not score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to calculate score for product ID {request.product_id}. "
            "Product may not exist or may not have been scraped yet.",
        )

    return ScoreResponse.model_validate(score)


@router.post(
    "/calculate/batch",
    summary="Calculate scores for multiple products",
    description="Calculate or recalculate scores for multiple products in batch.",
)
async def calculate_batch_scores(
    request: BatchCalculateScoreRequest,
    scoring_service: ScoringService = Depends(get_scoring_service),
):
    """
    Calculate scores for multiple products.

    Args:
        request: Batch calculation request
        scoring_service: Scoring service from dependency injection

    Returns:
        Batch calculation results with success/failure counts
    """
    results = scoring_service.calculate_batch_scores(
        product_ids=request.product_ids,
        force_recalculate=request.force_recalculate,
    )

    return results


@router.get(
    "/",
    summary="Get all scores",
    description="Retrieve a paginated list of all scores with optional filters.",
)
async def get_scores(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum score"),
    max_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum score"),
    score_version: Optional[str] = Query(None, description="Filter by score version"),
    sort_by: str = Query("total_score", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    scoring_service: ScoringService = Depends(get_scoring_service),
):
    """
    Get paginated list of scores.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        min_score: Minimum score filter
        max_score: Maximum score filter
        score_version: Filter by score version
        sort_by: Field to sort by
        sort_order: Sort order
        scoring_service: Scoring service from dependency injection

    Returns:
        Paginated list of scores
    """
    scores, total = scoring_service.get_scores(
        page=page,
        page_size=page_size,
        min_score=min_score,
        max_score=max_score,
        score_version=score_version,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total_pages = (total + page_size - 1) // page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "scores": [ScoreResponse.model_validate(score) for score in scores],
    }


@router.get(
    "/stats/overview",
    response_model=ScoreStatsResponse,
    summary="Get score statistics",
    description="Retrieve overall statistics about scores in the database.",
)
async def get_score_statistics(
    scoring_service: ScoringService = Depends(get_scoring_service),
):
    """
    Get score statistics.

    Args:
        scoring_service: Scoring service from dependency injection

    Returns:
        Score statistics including averages and distributions
    """
    stats = scoring_service.get_score_statistics()
    return ScoreStatsResponse(**stats)


@router.get(
    "/top",
    response_model=TopScoredProductsResponse,
    summary="Get top scored products",
    description="Retrieve the highest scoring products, optionally filtered by category.",
)
async def get_top_scored_products(
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    scoring_service: ScoringService = Depends(get_scoring_service),
):
    """
    Get top scored products.

    Args:
        limit: Number of products to return
        category: Optional category filter
        scoring_service: Scoring service from dependency injection

    Returns:
        List of top scored products with their scores
    """
    top_scores = scoring_service.get_top_scored_products(
        limit=limit,
        category=category,
    )

    # Convert to response format
    top_products = []
    for score in top_scores:
        product = score.product
        details = product.details if product else None

        score_with_product = ScoreWithProductResponse(
            score=ScoreResponse.model_validate(score),
            product_name=details.product_name if details else "Unknown",
            product_url=product.product_url if product else "",
            product_image_url=product.product_image_url if product else None,
            category=details.normalized_category if details else None,
            price=details.price if details else None,
        )
        top_products.append(score_with_product)

    return TopScoredProductsResponse(
        top_products=top_products,
        category=category,
        limit=limit,
    )


@router.delete(
    "/{score_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete score",
    description="Delete a score and all related components.",
)
async def delete_score(
    score_id: int,
    scoring_service: ScoringService = Depends(get_scoring_service),
):
    """
    Delete a score.

    Args:
        score_id: Score ID to delete
        scoring_service: Scoring service from dependency injection

    Raises:
        HTTPException: If score not found
    """
    success = scoring_service.delete_score(score_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Score with ID {score_id} not found",
        )

    return None
