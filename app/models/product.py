"""
Product models for the Dog Food Scoring API.

This module contains SQLAlchemy ORM models for products and their details.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import relationship

from app.models.database import Base


# Enums for ProcessedProduct
class FoodCategoryEnum(str, enum.Enum):
    RAW = "Raw"
    FRESH = "Fresh"
    DRY = "Dry"
    WET = "Wet"
    SOFT = "Soft"
    OTHER = "Other"


class SourcingIntegrityEnum(str, enum.Enum):
    HUMAN_GRADE_ORGANIC = "Human Grade (organic)"
    HUMAN_GRADE = "Human Grade"
    FEED_GRADE = "Feed Grade"
    OTHER = "Other"


class ProcessingMethodEnum(str, enum.Enum):
    UNCOOKED_NOT_FROZEN = "Uncooked (Not Frozen)"
    UNCOOKED_FLASH_FROZEN = "Uncooked (Flash Frozen)"
    UNCOOKED_FROZEN = "Uncooked (Frozen)"
    LIGHTLY_COOKED_NOT_FROZEN = "Lightly Cooked (Not Frozen)"
    LIGHTLY_COOKED_FROZEN = "Lightly Cooked (Frozen)"
    FREEZE_DRIED = "Freeze Dried"
    AIR_DRIED = "Air Dried"
    DEHYDRATED = "Dehydrated"
    BAKED = "Baked"
    EXTRUDED = "Extruded"
    RETORTED = "Retorted"
    OTHER = "Other"


class NutritionallyAdequateEnum(str, enum.Enum):
    YES = "Yes"
    NO = "No"


class QualityClassEnum(str, enum.Enum):
    HIGH = "High"
    GOOD = "Good"
    MODERATE = "Moderate"
    LOW = "Low"
    OTHER = "Other"


class FoodStorageEnum(str, enum.Enum):
    FREEZER = "Freezer"
    REFRIGERATOR = "Refrigerator"
    COOL_DRY_AWAY = "Cool Dry Space (Away from moisture)"
    COOL_DRY_NOT_AWAY = "Cool Dry Space (Not away from moisture)"


class PackagingSizeEnum(str, enum.Enum):
    ONE_MONTH = "a month"
    TWO_MONTH = "2 month"
    THREE_PLUS_MONTH = "3+ month"


class ShelfLifeEnum(str, enum.Enum):
    SEVEN_DAY = "7Day"
    EIGHT_TO_FOURTEEN_DAY = "8-14 Day"
    FIFTEEN_PLUS_DAY = "15+Day"
    OTHER = "Other"


def _enum_value(x):
    import enum as _py_enum

    return x.value if isinstance(x, _py_enum.Enum) else x


class ProductList(Base):
    """
    Product list model representing scraped product URLs.

    This table stores basic product information collected during the
    initial scraping phase, including URLs and scraping status.
    """

    __tablename__ = "products_list"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Product URL (unique identifier)
    product_url = Column(String, unique=True, nullable=False, index=True)

    # Source information
    page_num = Column(Integer, nullable=False, index=True)
    product_image_url = Column(String, nullable=True)

    # Status flags
    scraped = Column(Boolean, default=False, nullable=False)
    skipped = Column(Boolean, default=False, nullable=False)

    # Relationships
    details = relationship(
        "ProductDetails",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<ProductList(id={self.id}, url={self.product_url[:50]}..., "
            f"page={self.page_num}, scraped={self.scraped})>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "product_url": self.product_url,
            "page_num": self.page_num,
            "product_image_url": self.product_image_url,
            "scraped": self.scraped,
            "skipped": self.skipped,
        }


class ProductDetails(Base):
    """
    Product details model containing comprehensive product information.

    This table stores detailed information about each product including
    pricing, ingredients, nutritional information, and more.
    """

    __tablename__ = "product_details"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to ProductList
    product_id = Column(
        Integer,
        ForeignKey("products_list.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Basic information
    product_category = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    img_link = Column(String, nullable=True)
    product_url = Column(String, nullable=True)

    # Pricing and size
    price = Column(String, nullable=True)
    size = Column(String, nullable=True)

    # Product descriptions
    details = Column(Text, nullable=True)  # Key benefits/features
    more_details = Column(Text, nullable=True)  # Additional details
    specifications = Column(Text, nullable=True)  # Technical specifications

    # Ingredients and nutrition
    ingredients = Column(Text, nullable=True)
    caloric_content = Column(Text, nullable=True)
    guaranteed_analysis = Column(Text, nullable=True)

    # Feeding information
    feeding_instructions = Column(Text, nullable=True)
    transition_instructions = Column(Text, nullable=True)

    # Relationships
    product = relationship("ProductList", back_populates="details")

    def __repr__(self):
        return (
            f"<ProductDetails(id={self.id}, product_id={self.product_id}, "
            f"name={self.product_name[:30] if self.product_name else 'N/A'}...)>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_category": self.product_category,
            "product_name": self.product_name,
            "img_link": self.img_link,
            "product_url": self.product_url,
            "price": self.price,
            "size": self.size,
            "details": self.details,
            "more_details": self.more_details,
            "specifications": self.specifications,
            "ingredients": self.ingredients,
            "caloric_content": self.caloric_content,
            "guaranteed_analysis": self.guaranteed_analysis,
            "feeding_instructions": self.feeding_instructions,
            "transition_instructions": self.transition_instructions,
        }


class ProcessedProduct(Base):
    """
    Processed product model containing analyzed and normalized dog food data.

    This table stores comprehensive assessments of dog food products including
    sourcing, processing methods, nutritional analysis, ingredient quality,
    and storage information.
    """

    __tablename__ = "processed_products"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to ProductDetails
    product_detail_id = Column(
        Integer,
        ForeignKey("product_details.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Basic Information
    flavor = Column(Text, nullable=True)

    # Food Category
    food_category = Column(
        PGEnum(
            FoodCategoryEnum,
            values_callable=lambda x: [e.value for e in x],
            name="foodcategoryenum",
            create_type=False,
        ),
        nullable=True,
    )
    category_reason = Column(Text, nullable=True)

    # Sourcing Integrity
    sourcing_integrity = Column(
        PGEnum(
            SourcingIntegrityEnum,
            values_callable=lambda x: [e.value for e in x],
            name="sourcingintegrityenum",
            create_type=False,
        ),
        nullable=True,
    )
    sourcing_integrity_reason = Column(Text, nullable=True)

    # Processing Methods
    processing_method_1 = Column(
        PGEnum(
            ProcessingMethodEnum,
            values_callable=lambda x: [e.value for e in x],
            name="processingmethodenum",
            create_type=False,
        ),
        nullable=True,
    )
    processing_method_2 = Column(
        PGEnum(
            ProcessingMethodEnum,
            values_callable=lambda x: [e.value for e in x],
            name="processingmethodenum",
            create_type=False,
        ),
        nullable=True,
    )
    processing_adulteration_method = Column(
        PGEnum(
            ProcessingMethodEnum,
            values_callable=lambda x: [e.value for e in x],
            name="processingmethodenum",
            create_type=False,
        ),
        nullable=True,
    )
    processing_adulteration_method_reason = Column(Text, nullable=True)

    # Guaranteed Analysis
    guaranteed_analysis_crude_protein_pct = Column(Numeric(5, 2), nullable=True)
    guaranteed_analysis_crude_fat_pct = Column(Numeric(5, 2), nullable=True)
    guaranteed_analysis_crude_fiber_pct = Column(Numeric(5, 2), nullable=True)
    guaranteed_analysis_crude_moisture_pct = Column(Numeric(5, 2), nullable=True)
    guaranteed_analysis_crude_ash_pct = Column(Numeric(5, 2), nullable=True)
    starchy_carb_pct = Column(Numeric(5, 2), nullable=True)

    # Nutritional Adequacy
    nutritionally_adequate = Column(
        PGEnum(
            NutritionallyAdequateEnum,
            values_callable=lambda x: [e.value for e in x],
            name="nutritionallyadequateenum",
            create_type=False,
        ),
        nullable=True,
    )
    nutritionally_adequate_reason = Column(Text, nullable=True)

    # Ingredients - All
    ingredients_all = Column(Text, nullable=True)

    # Protein Ingredients
    protein_ingredients_all = Column(Text, nullable=True)
    protein_ingredients_high = Column(Integer, nullable=True)
    protein_ingredients_good = Column(Integer, nullable=True)
    protein_ingredients_moderate = Column(Integer, nullable=True)
    protein_ingredients_low = Column(Integer, nullable=True)
    protein_ingredients_other = Column(Text, nullable=True)
    protein_quality_class = Column(
        PGEnum(
            QualityClassEnum,
            values_callable=lambda x: [e.value for e in x],
            name="qualityclassenum",
            create_type=False,
        ),
        nullable=True,
    )

    # Fat Ingredients
    fat_ingredients_all = Column(Text, nullable=True)
    fat_ingredients_high = Column(Integer, nullable=True)
    fat_ingredients_good = Column(Integer, nullable=True)
    fat_ingredients_low = Column(Integer, nullable=True)
    fat_ingredients_other = Column(Text, nullable=True)
    fat_quality_class = Column(
        PGEnum(
            QualityClassEnum,
            values_callable=lambda x: [e.value for e in x],
            name="qualityclassenum",
            create_type=False,
        ),
        nullable=True,
    )

    # Carb Ingredients
    carb_ingredients_all = Column(Text, nullable=True)
    carb_ingredients_high = Column(Integer, nullable=True)
    carb_ingredients_good = Column(Integer, nullable=True)
    carb_ingredients_moderate = Column(Integer, nullable=True)
    carb_ingredients_low = Column(Integer, nullable=True)
    carb_ingredients_other = Column(Text, nullable=True)
    carb_quality_class = Column(
        PGEnum(
            QualityClassEnum,
            values_callable=lambda x: [e.value for e in x],
            name="qualityclassenum",
            create_type=False,
        ),
        nullable=True,
    )

    # Fiber Ingredients
    fiber_ingredients_all = Column(Text, nullable=True)
    fiber_ingredients_high = Column(Integer, nullable=True)
    fiber_ingredients_good = Column(Integer, nullable=True)
    fiber_ingredients_moderate = Column(Integer, nullable=True)
    fiber_ingredients_low = Column(Integer, nullable=True)
    fiber_ingredients_other = Column(Text, nullable=True)
    fiber_quality_class = Column(
        PGEnum(
            QualityClassEnum,
            values_callable=lambda x: [e.value for e in x],
            name="qualityclassenum",
            create_type=False,
        ),
        nullable=True,
    )

    # Dirty Dozen and Additives
    dirty_dozen_ingredients = Column(Text, nullable=True)
    dirty_dozen_ingredients_count = Column(Integer, nullable=True)
    synthetic_nutrition_addition = Column(Text, nullable=True)
    synthetic_nutrition_addition_count = Column(Integer, nullable=True)
    longevity_additives = Column(Text, nullable=True)
    longevity_additives_count = Column(Integer, nullable=True)

    # Storage and Shelf Life
    food_storage = Column(
        PGEnum(
            FoodStorageEnum,
            values_callable=lambda x: [e.value for e in x],
            name="foodstorageenum",
            create_type=False,
        ),
        nullable=True,
    )
    food_storage_reason = Column(Text, nullable=True)
    packaging_size = Column(
        PGEnum(
            PackagingSizeEnum,
            values_callable=lambda x: [e.value for e in x],
            name="packagingsizeenum",
            create_type=False,
        ),
        nullable=True,
    )
    shelf_life_thawed = Column(
        PGEnum(
            ShelfLifeEnum,
            values_callable=lambda x: [e.value for e in x],
            name="shelflifeenum",
            create_type=False,
        ),
        nullable=True,
    )

    # Metadata
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    processor_version = Column(String(50), nullable=True)

    # Relationships
    product_detail = relationship("ProductDetails", backref="processed_data")

    def __repr__(self):
        return (
            f"<ProcessedProduct(id={self.id}, product_detail_id={self.product_detail_id}, "
            f"food_category={self.food_category})>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "product_detail_id": self.product_detail_id,
            "flavor": self.flavor,
            "food_category": _enum_value(self.food_category)
            if self.food_category
            else None,
            "category_reason": self.category_reason,
            "sourcing_integrity": _enum_value(self.sourcing_integrity)
            if self.sourcing_integrity
            else None,
            "sourcing_integrity_reason": self.sourcing_integrity_reason,
            "processing_method_1": _enum_value(self.processing_method_1)
            if self.processing_method_1
            else None,
            "processing_method_2": _enum_value(self.processing_method_2)
            if self.processing_method_2
            else None,
            "processing_adulteration_method": _enum_value(
                self.processing_adulteration_method
            )
            if self.processing_adulteration_method
            else None,
            "processing_adulteration_method_reason": self.processing_adulteration_method_reason,
            "guaranteed_analysis_crude_protein_pct": float(
                self.guaranteed_analysis_crude_protein_pct
            )
            if self.guaranteed_analysis_crude_protein_pct
            else None,
            "guaranteed_analysis_crude_fat_pct": float(
                self.guaranteed_analysis_crude_fat_pct
            )
            if self.guaranteed_analysis_crude_fat_pct
            else None,
            "guaranteed_analysis_crude_fiber_pct": float(
                self.guaranteed_analysis_crude_fiber_pct
            )
            if self.guaranteed_analysis_crude_fiber_pct
            else None,
            "guaranteed_analysis_crude_moisture_pct": float(
                self.guaranteed_analysis_crude_moisture_pct
            )
            if self.guaranteed_analysis_crude_moisture_pct
            else None,
            "guaranteed_analysis_crude_ash_pct": float(
                self.guaranteed_analysis_crude_ash_pct
            )
            if self.guaranteed_analysis_crude_ash_pct
            else None,
            "starchy_carb_pct": float(self.starchy_carb_pct)
            if self.starchy_carb_pct
            else None,
            "nutritionally_adequate": _enum_value(self.nutritionally_adequate)
            if self.nutritionally_adequate
            else None,
            "nutritionally_adequate_reason": self.nutritionally_adequate_reason,
            "ingredients_all": self.ingredients_all,
            "protein_ingredients_all": self.protein_ingredients_all,
            "protein_ingredients_high": self.protein_ingredients_high,
            "protein_ingredients_good": self.protein_ingredients_good,
            "protein_ingredients_moderate": self.protein_ingredients_moderate,
            "protein_ingredients_low": self.protein_ingredients_low,
            "protein_ingredients_other": self.protein_ingredients_other,
            "protein_quality_class": _enum_value(self.protein_quality_class)
            if self.protein_quality_class
            else None,
            "fat_ingredients_all": self.fat_ingredients_all,
            "fat_ingredients_high": self.fat_ingredients_high,
            "fat_ingredients_good": self.fat_ingredients_good,
            "fat_ingredients_low": self.fat_ingredients_low,
            "fat_ingredients_other": self.fat_ingredients_other,
            "fat_quality_class": _enum_value(self.fat_quality_class)
            if self.fat_quality_class
            else None,
            "carb_ingredients_all": self.carb_ingredients_all,
            "carb_ingredients_high": self.carb_ingredients_high,
            "carb_ingredients_good": self.carb_ingredients_good,
            "carb_ingredients_moderate": self.carb_ingredients_moderate,
            "carb_ingredients_low": self.carb_ingredients_low,
            "carb_ingredients_other": self.carb_ingredients_other,
            "carb_quality_class": _enum_value(self.carb_quality_class)
            if self.carb_quality_class
            else None,
            "fiber_ingredients_all": self.fiber_ingredients_all,
            "fiber_ingredients_high": self.fiber_ingredients_high,
            "fiber_ingredients_good": self.fiber_ingredients_good,
            "fiber_ingredients_moderate": self.fiber_ingredients_moderate,
            "fiber_ingredients_low": self.fiber_ingredients_low,
            "fiber_ingredients_other": self.fiber_ingredients_other,
            "fiber_quality_class": _enum_value(self.fiber_quality_class)
            if self.fiber_quality_class
            else None,
            "dirty_dozen_ingredients": self.dirty_dozen_ingredients,
            "dirty_dozen_ingredients_count": self.dirty_dozen_ingredients_count,
            "synthetic_nutrition_addition": self.synthetic_nutrition_addition,
            "synthetic_nutrition_addition_count": self.synthetic_nutrition_addition_count,
            "longevity_additives": self.longevity_additives,
            "longevity_additives_count": self.longevity_additives_count,
            "food_storage": _enum_value(self.food_storage)
            if self.food_storage
            else None,
            "food_storage_reason": self.food_storage_reason,
            "packaging_size": _enum_value(self.packaging_size)
            if self.packaging_size
            else None,
            "shelf_life_thawed": _enum_value(self.shelf_life_thawed)
            if self.shelf_life_thawed
            else None,
            "processed_at": self.processed_at.isoformat()
            if self.processed_at
            else None,
            "processor_version": self.processor_version,
        }
