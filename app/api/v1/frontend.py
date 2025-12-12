"""
Frontend API endpoints for the Dog Food Scoring API.

This module provides REST API endpoints specifically designed for frontend consumption:
- /products - Get all products from the products view
- /product/{product_id} - Get a single product from the products view
- /score - Calculate score with pet information and return detailed score breakdown
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.schemas.products_view import ProductListItemResponse, ProductViewResponse
from app.schemas.score_calculation import (
    ScoreCalculationRequest,
    ScoreCalculationResponse,
)
from app.services.products_view_service import ProductsViewService

router = APIRouter()


def get_products_view_service(db: Session = Depends(get_database)) -> ProductsViewService:
    """Get products view service dependency."""
    return ProductsViewService(db)


@router.get(
    "/products",
    response_model=List[ProductListItemResponse],
    summary="Get all products",
    description="Retrieve all products with only id and name from the final products view.",
)
async def get_products(
    products_view_service: ProductsViewService = Depends(get_products_view_service),
):
    """
    Get all products from the products view (id and name only).

    Returns:
        List of products with only id and name
    """
    products = products_view_service.get_all_products()
    result = []
    for product in products:
        # Extract id and name from the product dictionary
        product_id = product.get("Product ID") or product.get("product_id")
        product_name = product.get("Product Name") or product.get("product_name") or ""
        
        if product_id is not None:
            result.append(ProductListItemResponse(
                id=product_id,
                name=product_name
            ))
    return result


@router.get(
    "/product/{product_id}",
    response_model=ProductViewResponse,
    summary="Get product by ID",
    description="Retrieve a single product from the products view by ID.",
)
async def get_product(
    product_id: int,
    products_view_service: ProductsViewService = Depends(get_products_view_service),
):
    """
    Get a single product by ID from the products view.

    Args:
        product_id: Product ID

    Returns:
        Product information matching the products view schema

    Raises:
        HTTPException: If product not found
    """
    product = products_view_service.get_product_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    return ProductViewResponse.from_dict(product)


@router.post(
    "/score",
    response_model=ScoreCalculationResponse,
    summary="Calculate score",
    description="Calculate score for base and topper products with pet information and return detailed score breakdown.",
)
async def calculate_score(
    request: ScoreCalculationRequest,
    db: Session = Depends(get_database),
    products_view_service: ProductsViewService = Depends(get_products_view_service),
):
    """
    Calculate score for products with pet information.

    Args:
        request: Score calculation request with product IDs, pet info, and storage details
        db: Database session
        products_view_service: Products view service

    Returns:
        Score calculation response with total score, classification, carb percent, and micro scores

    Raises:
        HTTPException: If products not found or calculation fails
    """
    # Get base product
    base_product = products_view_service.get_product_by_id(request.base_products)
    if not base_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Base product with ID {request.base_products} not found",
        )

    # Get topper product if provided
    topper_product = None
    if request.topper_products:
        topper_product = products_view_service.get_product_by_id(request.topper_products)
        if not topper_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topper product with ID {request.topper_products} not found",
            )

    # TODO: Implement actual score calculation logic
    # For now, return a placeholder response structure
    # The user mentioned they will provide the calculation logic
    
    # Placeholder calculation - this should be replaced with actual scoring logic
    from app.services.scoring_service import ScoringService
    scoring_service = ScoringService(db)
    
    # Calculate base product score
    base_score_result = scoring_service.calculate_product_score(request.base_products)
    
    # Calculate topper product score if provided
    topper_score_result = None
    if request.topper_products:
        topper_score_result = scoring_service.calculate_product_score(request.topper_products)
    
    # Get carb percent from base product
    carb_percent = float(base_product.get("Starchy Carb %") or base_product.get("starchy_carb_pct") or 0.0)
    
    # Calculate total score (simplified - should be replaced with actual logic)
    total_score = base_score_result.total_score if base_score_result else 0.0
    if topper_score_result:
        # Combine scores (simplified - actual logic needed)
        total_score = (total_score + topper_score_result.total_score) / 2
    
    # Determine classification based on score
    if total_score >= 90:
        classification = "Excellent"
    elif total_score >= 80:
        classification = "Very Good"
    elif total_score >= 70:
        classification = "Good"
    elif total_score >= 60:
        classification = "Fair"
    else:
        classification = "Poor"
    
    # Build micro score components
    # This is a placeholder - actual calculation should use the scoring service components
    # and apply deductions based on storage, packaging, shelf_life, etc.
    
    from app.schemas.score_calculation import MicroScore, MicroScoreComponent
    
    # Placeholder micro scores - these should be calculated from actual scoring logic
    micro_score = MicroScore(
        food=MicroScoreComponent(grade="A", score=90),
        sourcing=MicroScoreComponent(grade="A", score=88),
        processing=MicroScoreComponent(grade="B", score=82),
        adequacy=MicroScoreComponent(grade="A", score=95),
        carb=MicroScoreComponent(grade="B", score=80),
        ingredient_quality_protein=MicroScoreComponent(grade="A", score=92),
        ingredient_quality_fat=MicroScoreComponent(grade="A", score=85),
        ingredient_quality_fiber=MicroScoreComponent(grade="B", score=78),
        ingredient_quality_carbohydrate=MicroScoreComponent(grade="B", score=75),
        dirty_dozen=MicroScoreComponent(grade="A", score=100),
        synthetic=MicroScoreComponent(grade="B", score=80),
        longevity=MicroScoreComponent(grade="A", score=90),
        storage=MicroScoreComponent(grade="A", score=88),
        packaging=MicroScoreComponent(grade="B", score=82),
        shelf_life=MicroScoreComponent(grade="A", score=90),
    )
    
    return ScoreCalculationResponse(
        score=total_score,
        classification=classification,
        carb_percent=carb_percent,
        micro_score=micro_score,
    )

