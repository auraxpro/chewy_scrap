"""
Product schemas for the Dog Food Scoring API.

This module contains Pydantic schemas for product-related API requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

# ============================================================================
# Base Schemas
# ============================================================================


class ProductBase(BaseModel):
    """Base schema for product data."""

    product_url: str = Field(..., description="URL of the product on Chewy.com")
    product_image_url: Optional[str] = Field(
        None, description="URL of the product image"
    )


class ProductDetailsBase(BaseModel):
    """Base schema for product details."""

    product_category: Optional[str] = Field(None, description="Product category")
    product_name: str = Field(..., description="Name of the product")
    img_link: Optional[str] = Field(None, description="Image URL")
    price: Optional[str] = Field(None, description="Product price")
    size: Optional[str] = Field(None, description="Product size/package size")


# ============================================================================
# Response Schemas
# ============================================================================


class ProductListResponse(BaseModel):
    """Schema for product list item response."""

    id: int = Field(..., description="Product ID")
    product_url: str = Field(..., description="Product URL")
    page_num: int = Field(..., description="Page number where product was found")
    product_image_url: Optional[str] = Field(None, description="Product image URL")
    scraped: bool = Field(..., description="Whether product details have been scraped")
    skipped: bool = Field(
        ..., description="Whether product was skipped during scraping"
    )
    processed: bool = Field(..., description="Whether product has been processed")
    scored: bool = Field(..., description="Whether product has been scored")
    created_at: datetime = Field(..., description="Timestamp when product was created")
    updated_at: datetime = Field(
        ..., description="Timestamp when product was last updated"
    )
    scraped_at: Optional[datetime] = Field(
        None, description="Timestamp when product was scraped"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_url": "https://www.chewy.com/american-journey-grain-free-salmon/dp/108423",
                "page_num": 1,
                "product_image_url": "https://img.chewy.com/is/image/catalog/108423_MAIN._AC_SL1500_.jpg",
                "scraped": True,
                "skipped": False,
                "processed": True,
                "scored": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T11:30:00",
                "scraped_at": "2024-01-15T10:35:00",
            }
        }


class ProductDetailResponse(BaseModel):
    """Schema for detailed product information response."""

    id: int = Field(..., description="Product details ID")
    product_id: int = Field(..., description="Reference to product list ID")
    product_category: Optional[str] = Field(None, description="Product category")
    product_name: str = Field(..., description="Product name")
    img_link: Optional[str] = Field(None, description="Image URL")
    product_url: Optional[str] = Field(None, description="Product URL")
    price: Optional[str] = Field(None, description="Product price")
    size: Optional[str] = Field(None, description="Product size")
    details: Optional[str] = Field(None, description="Key benefits and features")
    more_details: Optional[str] = Field(None, description="Additional product details")
    specifications: Optional[str] = Field(None, description="Product specifications")
    ingredients: Optional[str] = Field(None, description="Ingredients list")
    caloric_content: Optional[str] = Field(
        None, description="Caloric content information"
    )
    guaranteed_analysis: Optional[str] = Field(None, description="Guaranteed analysis")
    feeding_instructions: Optional[str] = Field(
        None, description="Feeding instructions"
    )
    transition_instructions: Optional[str] = Field(
        None, description="Transition instructions"
    )
    normalized_ingredients: Optional[str] = Field(
        None, description="Normalized ingredients (JSON)"
    )
    normalized_category: Optional[str] = Field(None, description="Normalized category")
    processing_level: Optional[str] = Field(
        None, description="Processing level (raw, kibble, etc.)"
    )
    estimated_package_size_kg: Optional[str] = Field(
        None, description="Estimated package size in kg"
    )
    created_at: datetime = Field(..., description="Timestamp when details were created")
    updated_at: datetime = Field(
        ..., description="Timestamp when details were last updated"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_id": 1,
                "product_category": "Dog/Food/Dry Food",
                "product_name": "American Journey Grain-Free Salmon & Sweet Potato Recipe",
                "img_link": "https://img.chewy.com/is/image/catalog/108423_MAIN._AC_SL1500_.jpg",
                "product_url": "https://www.chewy.com/american-journey-grain-free-salmon/dp/108423",
                "price": "$49.99",
                "size": "24 lb",
                "details": "Real salmon is the first ingredient...",
                "ingredients": "Salmon, Sweet Potatoes, Peas...",
                "normalized_category": "dry_kibble",
                "processing_level": "kibble",
                "created_at": "2024-01-15T10:35:00",
                "updated_at": "2024-01-15T11:00:00",
            }
        }


class ProductResponse(BaseModel):
    """Schema for complete product response (list + details)."""

    product: ProductListResponse = Field(..., description="Product list information")
    details: Optional[ProductDetailResponse] = Field(
        None, description="Product details (if available)"
    )
    score: Optional[float] = Field(None, description="Product score (if calculated)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "product": {
                    "id": 1,
                    "product_url": "https://www.chewy.com/american-journey-grain-free-salmon/dp/108423",
                    "page_num": 1,
                    "product_image_url": "https://img.chewy.com/is/image/catalog/108423_MAIN._AC_SL1500_.jpg",
                    "scraped": True,
                    "skipped": False,
                    "processed": True,
                    "scored": True,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T11:30:00",
                    "scraped_at": "2024-01-15T10:35:00",
                },
                "details": {
                    "id": 1,
                    "product_id": 1,
                    "product_name": "American Journey Grain-Free Salmon",
                    "price": "$49.99",
                    "size": "24 lb",
                },
                "score": 85.5,
            }
        }


# ============================================================================
# Request Schemas
# ============================================================================


class ProductSearchRequest(BaseModel):
    """Schema for product search request."""

    query: Optional[str] = Field(
        None, description="Search query for product name or ingredients"
    )
    category: Optional[str] = Field(None, description="Filter by category")
    min_price: Optional[float] = Field(None, description="Minimum price filter")
    max_price: Optional[float] = Field(None, description="Maximum price filter")
    min_score: Optional[float] = Field(None, description="Minimum score filter")
    max_score: Optional[float] = Field(None, description="Maximum score filter")
    processing_level: Optional[str] = Field(
        None, description="Filter by processing level"
    )
    scraped: Optional[bool] = Field(None, description="Filter by scraped status")
    scored: Optional[bool] = Field(None, description="Filter by scored status")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "salmon",
                "category": "dry_kibble",
                "min_score": 70.0,
                "max_score": 100.0,
                "scraped": True,
                "scored": True,
                "page": 1,
                "page_size": 50,
            }
        }


class ProductListPaginatedResponse(BaseModel):
    """Schema for paginated product list response."""

    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    products: list[ProductResponse] = Field(..., description="List of products")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 1234,
                "page": 1,
                "page_size": 50,
                "total_pages": 25,
                "products": [],
            }
        }


# ============================================================================
# Statistics Schemas
# ============================================================================


class ProductStatsResponse(BaseModel):
    """Schema for product statistics response."""

    total_products: int = Field(..., description="Total number of products")
    scraped_products: int = Field(
        ..., description="Number of products with details scraped"
    )
    processed_products: int = Field(..., description="Number of processed products")
    scored_products: int = Field(..., description="Number of scored products")
    categories: dict[str, int] = Field(..., description="Product count by category")
    average_score: Optional[float] = Field(None, description="Average product score")
    score_distribution: dict[str, int] = Field(
        ..., description="Score distribution by range"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_products": 1234,
                "scraped_products": 1200,
                "processed_products": 1100,
                "scored_products": 1000,
                "categories": {
                    "dry_kibble": 800,
                    "wet_food": 300,
                    "raw": 100,
                    "freeze_dried": 34,
                },
                "average_score": 75.5,
                "score_distribution": {
                    "0-20": 50,
                    "20-40": 150,
                    "40-60": 300,
                    "60-80": 400,
                    "80-100": 100,
                },
            }
        }
