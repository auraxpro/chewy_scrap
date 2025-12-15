"""
Frontend API endpoints for the Dog Food Scoring API.

This module provides REST API endpoints specifically designed for frontend consumption:
- /products - Get all products from the products view
- /product/{product_id} - Get a single product from the products view
- /score - Calculate score with pet information and return detailed score breakdown
"""

from typing import TYPE_CHECKING, List

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

if TYPE_CHECKING:
    from app.models.product import ProcessedProduct
    from app.scoring.base_score_calculator import BaseScoreCalculator
    from app.schemas.score_calculation import MicroScore

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
    print('base_product:')
    print(base_product)
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
    from app.scoring.base_score_calculator import BaseScoreCalculator
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
    print('processed_base:')
    print(processed_base)
    
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
    
    # Calculate micro scores using BaseScoreCalculator logic
    base_calculator = BaseScoreCalculator(db)
    micro_score = _calculate_micro_scores(processed_base, base_calculator, score_result)
    
    return ScoreCalculationResponse(
        score=score_result["final_score"],
        classification=score_result["classification"],
        carb_percent=carb_percent,
        micro_score=micro_score,
    )


def _calculate_micro_scores(
    processed_product: "ProcessedProduct",
    base_calculator: "BaseScoreCalculator",
    score_result: dict,
) -> "MicroScore":
    """
    Calculate micro scores using BaseScoreCalculator logic.
    
    Args:
        processed_product: ProcessedProduct instance
        base_calculator: BaseScoreCalculator instance
        score_result: Result from dynamic score calculator containing deductions
        
    Returns:
        MicroScore with all components calculated
    """
    from app.schemas.score_calculation import MicroScore, MicroScoreComponent
    
    # Helper function to convert deduction to score (0-100)
    def deduction_to_score(deduction: float, max_deduction: float) -> float:
        """Convert deduction to score (100 - scaled deduction)."""
        if deduction is None:
            return 100.0  # Default to perfect score if deduction is None
        scaled_deduction = (deduction / max_deduction) * 100 if max_deduction > 0 else 0
        return max(0.0, min(100.0, 100.0 - scaled_deduction))
    
    # Helper function to convert bonus to score (0-100)
    def bonus_to_score(bonus: float, max_bonus: float) -> float:
        """Convert bonus to score (100 + scaled bonus, capped at 100)."""
        if bonus is None:
            return 100.0  # Default to perfect score if bonus is None
        scaled_bonus = (bonus / max_bonus) * 100 if max_bonus > 0 else 0
        return min(100.0, 100.0 + scaled_bonus)
    
    # 1. Food Category Score (max deduction:15)
    food_category_deduction = base_calculator._calculate_food_category_deduction(
        processed_product.food_category
    )
    food_score = deduction_to_score(food_category_deduction or 0, 15)
    
    print('food_category_deduction:')
    print(food_category_deduction)
    # 2. Sourcing Integrity Score (max deduction: 10)
    sourcing_deduction = base_calculator._calculate_sourcing_integrity_deduction(
        processed_product.sourcing_integrity
    )
    print('sourcing_deduction:')
    print(processed_product.sourcing_integrity)
    sourcing_score = deduction_to_score(sourcing_deduction or 0, 10)
    
    # 3. Processing Method Score (max deduction: 15)
    processing_deduction = base_calculator._calculate_processing_method_deduction(
        processed_product.processing_adulteration_method
    )
    processing_score = deduction_to_score(processing_deduction or 0, 15)
    
    # 4. Nutritionally Adequate Score (max deduction: 10)
    adequacy_deduction = base_calculator._calculate_nutritionally_adequate_deduction(
        processed_product.nutritionally_adequate
    )
    adequacy_score = deduction_to_score(adequacy_deduction or 0, 10)
    
    # 5. Starchy Carb Score (max deduction: 10)
    starchy_carb_deduction = base_calculator._calculate_starchy_carb_deduction(
        float(processed_product.starchy_carb_pct) if processed_product.starchy_carb_pct is not None else None
    )
    carb_score = deduction_to_score(starchy_carb_deduction or 0, 10)
    
    # 6. Ingredient Quality - Protein Score (max deduction: 5)
    protein_deduction = base_calculator._calculate_ingredient_quality_deduction(
        high_count=processed_product.protein_ingredients_high or 0,
        good_count=processed_product.protein_ingredients_good or 0,
        moderate_count=processed_product.protein_ingredients_moderate or 0,
        low_count=processed_product.protein_ingredients_low or 0,
        max_deduction=9,
    )
    protein_score = deduction_to_score(protein_deduction, 5)
    
    # 7. Ingredient Quality - Fat Score (max deduction: 5)
    fat_deduction = base_calculator._calculate_ingredient_quality_deduction(
        high_count=processed_product.fat_ingredients_high or 0,
        good_count=processed_product.fat_ingredients_good or 0,
        moderate_count=0,  # Fats don't have moderate tier
        low_count=processed_product.fat_ingredients_low or 0,
        max_deduction=5,
    )
    fat_score = deduction_to_score(fat_deduction, 5)
    
    # 8. Ingredient Quality - Carbohydrate Score (max deduction: 5)
    carb_ingredient_deduction = base_calculator._calculate_ingredient_quality_deduction(
        high_count=processed_product.carb_ingredients_high or 0,
        good_count=processed_product.carb_ingredients_good or 0,
        moderate_count=processed_product.carb_ingredients_moderate or 0,
        low_count=processed_product.carb_ingredients_low or 0,
        max_deduction=5,
    )
    carb_ingredient_score = deduction_to_score(carb_ingredient_deduction, 5)
    
    # 9. Ingredient Quality - Fiber Score (max deduction: 5)
    fiber_deduction = base_calculator._calculate_ingredient_quality_deduction(
        high_count=processed_product.fiber_ingredients_high or 0,
        good_count=processed_product.fiber_ingredients_good or 0,
        moderate_count=processed_product.fiber_ingredients_moderate or 0,
        low_count=processed_product.fiber_ingredients_low or 0,
        max_deduction=10,
    )
    fiber_score = deduction_to_score(fiber_deduction, 5)
    
    # 10. Dirty Dozen Score (max deduction: 10)
    dirty_dozen_deduction = base_calculator._calculate_dirty_dozen_deduction(
        processed_product.dirty_dozen_ingredients_count or 0
    )
    dirty_dozen_score = deduction_to_score(dirty_dozen_deduction, 10)
    
    # 11. Synthetic Nutrition Score (max deduction: 5)
    synthetic_deduction = base_calculator._calculate_synthetic_nutrition_deduction(
        processed_product.synthetic_nutrition_addition_count or 0
    )
    synthetic_score = deduction_to_score(synthetic_deduction, 5)
    
    # 12. Longevity Additives Score (max bonus: +5) - This is a bonus, so higher is better
    longevity_bonus = base_calculator._calculate_longevity_additives_bonus(
        processed_product.longevity_additives_count or 0
    )
    longevity_score = bonus_to_score(longevity_bonus, 5)
    
    # 13-15. Storage, Packaging, Shelf Life scores from dynamic calculator deductions
    deductions = score_result.get("deductions", {})
    
    # Storage score (max deduction: 5 points, but scaled to 0-100)
    storage_deduction = deductions.get("food_storage", 0)
    storage_score = max(0, 100 - (storage_deduction * (100 / 5)))  # Scale: 5 deduction = 0 score
    
    # Packaging score (max deduction: 5 points, but scaled to 0-100)
    packaging_deduction = deductions.get("packaging_size", 0)
    packaging_score = max(0, 100 - (packaging_deduction * (100 / 5)))  # Scale: 5 deduction = 0 score
    
    # Shelf life score (max deduction: 5 points, but scaled to 0-100)
    shelf_life_deduction = deductions.get("thawed_shelf_life", 0)
    shelf_life_score = max(0, 100 - (shelf_life_deduction * (100 / 5)))  # Scale: 5 deduction = 0 score
    
    return MicroScore(
        food=MicroScoreComponent(grade=_get_grade_from_score(food_score), score=int(food_score)),
        sourcing=MicroScoreComponent(grade=_get_grade_from_score(sourcing_score), score=int(sourcing_score)),
        processing=MicroScoreComponent(grade=_get_grade_from_score(processing_score), score=int(processing_score)),
        adequacy=MicroScoreComponent(grade=_get_grade_from_score(adequacy_score), score=int(adequacy_score)),
        carb=MicroScoreComponent(grade=_get_grade_from_score(carb_score), score=int(carb_score)),
        ingredient_quality_protein=MicroScoreComponent(grade=_get_grade_from_score(protein_score), score=int(protein_score)),
        ingredient_quality_fat=MicroScoreComponent(grade=_get_grade_from_score(fat_score), score=int(fat_score)),
        ingredient_quality_fiber=MicroScoreComponent(grade=_get_grade_from_score(fiber_score), score=int(fiber_score)),
        ingredient_quality_carbohydrate=MicroScoreComponent(grade=_get_grade_from_score(carb_ingredient_score), score=int(carb_ingredient_score)),
        dirty_dozen=MicroScoreComponent(grade=_get_grade_from_score(dirty_dozen_score), score=int(dirty_dozen_score)),
        synthetic=MicroScoreComponent(grade=_get_grade_from_score(synthetic_score), score=int(synthetic_score)),
        longevity=MicroScoreComponent(grade=_get_grade_from_score(longevity_score), score=int(longevity_score)),
        storage=MicroScoreComponent(grade=_get_grade_from_score(storage_score), score=int(storage_score)),
        packaging=MicroScoreComponent(grade=_get_grade_from_score(packaging_score), score=int(packaging_score)),
        shelf_life=MicroScoreComponent(grade=_get_grade_from_score(shelf_life_score), score=int(shelf_life_score)),
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

