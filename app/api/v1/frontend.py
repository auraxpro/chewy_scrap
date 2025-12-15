"""
Frontend API endpoints for the Dog Food Scoring API.

This module provides REST API endpoints specifically designed for frontend consumption:
- /products - Get all products from the products view
- /product/{product_id} - Get a single product from the products view
- /score - Calculate score with pet information and return detailed score breakdown
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.models.product import FoodStorageEnum, PackagingSizeEnum, ShelfLifeEnum
from app.schemas.products_view import ProductListItemResponse, ProductViewResponse
from app.schemas.score_calculation import (
    ScoreCalculationRequest,
    ScoreCalculationResponse,
)
from app.services.products_view_service import ProductsViewService

router = APIRouter()


# Enum response schemas
class EnumValueResponse(BaseModel):
    """Schema for enum value response."""
    value: str = Field(..., description="Enum value")
    label: str = Field(..., description="Human-readable label")


class EnumListResponse(BaseModel):
    """Schema for enum list response."""
    enum_name: str = Field(..., description="Name of the enum")
    values: List[EnumValueResponse] = Field(..., description="List of enum values")


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
        # Extract id, name, brand, category, and image URL from the product dictionary
        product_id = product.get("Product ID") or product.get("product_id")
        product_name = product.get("Product Name") or product.get("product_name") or ""
        brand = product.get("Brand") or product.get("brand") or ""
        category = product.get("Food Category") or product.get("food_category")
        # Prefer ProductDetails.img_link, fallback to ProductList.product_image_url
        product_img_url = (
            product.get("Product Image") 
            or product.get("product_image")
            or product.get("Product Image URL")
            or product.get("product_image_url")
        )
        
        if product_id is not None:
            result.append(ProductListItemResponse(
                id=product_id,
                name=product_name,
                brand=brand,
                category=category,
                product_img_url=product_img_url
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

    # Get processed product data for base product
    from app.models.product import ProcessedProduct, ProductDetails, ProductList
    from app.scoring.dynamic_score_calculator import DynamicScoreCalculator
    from app.models.product import FoodStorageEnum, PackagingSizeEnum, ShelfLifeEnum
    
    # Get ProductList first (request.base_products is ProductList.id)
    base_product_list = db.query(ProductList).filter(ProductList.id == request.base_products).first()
    
    if not base_product_list or not base_product_list.details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product details not found for base product ID {request.base_products}",
        )
    
    # Get processed product record using ProductDetails.id
    processed_base = (
        db.query(ProcessedProduct)
        .filter(ProcessedProduct.product_detail_id == base_product_list.details.id)
        .first()
    )
    
    if not processed_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Processed product data not found for base product ID {request.base_products}. Please run --process-all to process this product.",
        )
    
    # Get base score (Phase 1 - pre-calculated)
    base_score = float(processed_base.base_score) if processed_base.base_score is not None else None
    
    if base_score is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Base score not available for product ID {request.base_products}. Please run --process-all to calculate base scores.",
        )
    
    # Map API request strings to enum values
    def map_storage_to_enum(storage_str: str) -> FoodStorageEnum:
        """Map storage string to FoodStorageEnum."""
        mapping = {
            "Freezer": FoodStorageEnum.FREEZER,
            "Refrigerator": FoodStorageEnum.REFRIGERATOR,
            "Cool Dry Space (Away from moisture)": FoodStorageEnum.COOL_DRY_AWAY,
            "Cool Dry Space (Not away from moisture)": FoodStorageEnum.COOL_DRY_NOT_AWAY,
        }
        return mapping.get(storage_str, FoodStorageEnum.FREEZER)
    
    def map_packaging_to_enum(packaging_str: str) -> PackagingSizeEnum:
        """Map packaging size string to PackagingSizeEnum."""
        mapping = {
            "a month": PackagingSizeEnum.ONE_MONTH,
            "1 month": PackagingSizeEnum.ONE_MONTH,
            "2 month": PackagingSizeEnum.TWO_MONTH,
            "3+ month": PackagingSizeEnum.THREE_PLUS_MONTH,
        }
        return mapping.get(packaging_str, PackagingSizeEnum.ONE_MONTH)
    
    def map_shelf_life_to_enum(shelf_life_str: str) -> ShelfLifeEnum:
        """Map shelf life string to ShelfLifeEnum."""
        mapping = {
            "7Day": ShelfLifeEnum.SEVEN_DAY,
            "7 day": ShelfLifeEnum.SEVEN_DAY,
            "8-14 Day": ShelfLifeEnum.EIGHT_TO_FOURTEEN_DAY,
            "8-14 day": ShelfLifeEnum.EIGHT_TO_FOURTEEN_DAY,
            "15+Day": ShelfLifeEnum.FIFTEEN_PLUS_DAY,
            "15+ day": ShelfLifeEnum.FIFTEEN_PLUS_DAY,
        }
        return mapping.get(shelf_life_str, ShelfLifeEnum.SEVEN_DAY)
    
    # Convert request strings to enums
    food_storage_enum = map_storage_to_enum(request.storage) if request.storage else None
    packaging_size_enum = map_packaging_to_enum(request.packaging_size) if request.packaging_size else None
    shelf_life_enum = map_shelf_life_to_enum(request.shelf_life) if request.shelf_life else None
    
    # Calculate final score using dynamic score calculator (Phase 2)
    dynamic_calculator = DynamicScoreCalculator()
    score_result = dynamic_calculator.calculate_final_score(
        base_score=base_score,
        food_category=processed_base.food_category,
        processing_method=processed_base.processing_adulteration_method,
        food_storage=food_storage_enum,
        packaging_size=packaging_size_enum,
        shelf_life=shelf_life_enum,
    )
    
    if score_result.get("error"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=score_result["error"],
        )
    
    # Get carb percent from base product
    carb_percent = float(base_product.get("Starchy Carb %") or base_product.get("starchy_carb_pct") or 0.0)
    
    # Build micro score components
    from app.schemas.score_calculation import MicroScore, MicroScoreComponent
    
    # Calculate micro scores based on deductions
    # Note: These are simplified - actual implementation may need more detailed breakdown
    deductions = score_result.get("deductions", {})
    
    # Calculate storage score (100 - deduction)
    storage_deduction = deductions.get("food_storage", 0)
    storage_score = max(0, 100 - (storage_deduction * 25))  # Scale to 0-100
    
    # Calculate packaging score (100 - deduction)
    packaging_deduction = deductions.get("packaging_size", 0)
    packaging_score = max(0, 100 - (packaging_deduction * 14))  # Scale to 0-100
    
    # Calculate shelf life score (100 - deduction)
    shelf_life_deduction = deductions.get("thawed_shelf_life", 0)
    shelf_life_score = max(0, 100 - (shelf_life_deduction * 17))  # Scale to 0-100
    
    # Placeholder for other micro scores (these would need to be calculated from base score breakdown)
    # For now, using simplified values
    micro_score = MicroScore(
        food=MicroScoreComponent(grade="A", score=90),  # Placeholder
        sourcing=MicroScoreComponent(grade="A", score=88),  # Placeholder
        processing=MicroScoreComponent(grade="B", score=82),  # Placeholder
        adequacy=MicroScoreComponent(grade="A", score=95),  # Placeholder
        carb=MicroScoreComponent(grade="B", score=80),  # Placeholder
        ingredient_quality_protein=MicroScoreComponent(grade="A", score=92),  # Placeholder
        ingredient_quality_fat=MicroScoreComponent(grade="A", score=85),  # Placeholder
        ingredient_quality_fiber=MicroScoreComponent(grade="B", score=78),  # Placeholder
        ingredient_quality_carbohydrate=MicroScoreComponent(grade="B", score=75),  # Placeholder
        dirty_dozen=MicroScoreComponent(grade="A", score=100),  # Placeholder
        synthetic=MicroScoreComponent(grade="B", score=80),  # Placeholder
        longevity=MicroScoreComponent(grade="A", score=90),  # Placeholder
        storage=MicroScoreComponent(grade=_get_grade_from_score(storage_score), score=int(storage_score)),
        packaging=MicroScoreComponent(grade=_get_grade_from_score(packaging_score), score=int(packaging_score)),
        shelf_life=MicroScoreComponent(grade=_get_grade_from_score(shelf_life_score), score=int(shelf_life_score)),
    )
    
    return ScoreCalculationResponse(
        score=score_result["final_score"],
        classification=score_result["classification"],
        carb_percent=carb_percent,
        micro_score=micro_score,
    )


def _get_grade_from_score(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


@router.get(
    "/enums/storage",
    response_model=EnumListResponse,
    summary="Get food storage enum values",
    description="Retrieve all available food storage enum values from the database.",
)
async def get_storage_enums():
    """
    Get all food storage enum values.

    Returns:
        EnumListResponse containing all food storage enum values
    """
    values = [
        EnumValueResponse(value=enum.value, label=enum.value)
        for enum in FoodStorageEnum
    ]
    return EnumListResponse(enum_name="FoodStorageEnum", values=values)


@router.get(
    "/enums/packaging",
    response_model=EnumListResponse,
    summary="Get packaging size enum values",
    description="Retrieve all available packaging size enum values from the database.",
)
async def get_packaging_enums():
    """
    Get all packaging size enum values.

    Returns:
        EnumListResponse containing all packaging size enum values
    """
    values = [
        EnumValueResponse(value=enum.value, label=enum.value)
        for enum in PackagingSizeEnum
    ]
    return EnumListResponse(enum_name="PackagingSizeEnum", values=values)


@router.get(
    "/enums/shelf-life",
    response_model=EnumListResponse,
    summary="Get shelf life enum values",
    description="Retrieve all available shelf life enum values from the database.",
)
async def get_shelf_life_enums():
    """
    Get all shelf life enum values.

    Returns:
        EnumListResponse containing all shelf life enum values
    """
    values = [
        EnumValueResponse(value=enum.value, label=enum.value)
        for enum in ShelfLifeEnum
    ]
    return EnumListResponse(enum_name="ShelfLifeEnum", values=values)


@router.get(
    "/enums/all",
    summary="Get all enum values",
    description="Retrieve all available enum values (storage, packaging, shelf-life) in a single response.",
)
async def get_all_enums():
    """
    Get all enum values (storage, packaging, shelf-life).

    Returns:
        Dictionary containing all enum lists
    """
    storage_values = [
        EnumValueResponse(value=enum.value, label=enum.value)
        for enum in FoodStorageEnum
    ]
    packaging_values = [
        EnumValueResponse(value=enum.value, label=enum.value)
        for enum in PackagingSizeEnum
    ]
    shelf_life_values = [
        EnumValueResponse(value=enum.value, label=enum.value)
        for enum in ShelfLifeEnum
    ]

    return {
        "storage": EnumListResponse(enum_name="FoodStorageEnum", values=storage_values).model_dump(),
        "packaging": EnumListResponse(enum_name="PackagingSizeEnum", values=packaging_values).model_dump(),
        "shelf_life": EnumListResponse(enum_name="ShelfLifeEnum", values=shelf_life_values).model_dump(),
    }

