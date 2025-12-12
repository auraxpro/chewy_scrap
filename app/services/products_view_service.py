"""
Products View service for querying the final products view.

This service handles queries to the products view that combines
data from product_details and processed_products tables.
"""

from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.product import ProcessedProduct, ProductDetails, ProductList


class ProductsViewService:
    """Service for querying the products view."""

    def __init__(self, db: Session):
        """
        Initialize the products view service.

        Args:
            db: Database session
        """
        self.db = db

    def get_all_products(self) -> List[dict]:
        """
        Get all products from the products view.

        Returns:
            List of product dictionaries matching the products view schema
        """
        # Try to query the view directly, if it exists
        try:
            result = self.db.execute(text("SELECT * FROM products"))
            columns = result.keys()
            products = []
            for row in result:
                product_dict = dict(zip(columns, row))
                products.append(product_dict)
            return products
        except Exception:
            # If view doesn't exist, create a query that joins the tables
            return self._get_products_from_join()

    def get_product_by_id(self, product_id: int) -> Optional[dict]:
        """
        Get a single product by ID from the products view.

        Args:
            product_id: Product ID

        Returns:
            Product dictionary or None if not found
        """
        # Try to query the view directly
        try:
            result = self.db.execute(
                text("SELECT * FROM products WHERE \"Product ID\" = :product_id"),
                {"product_id": product_id}
            )
            row = result.first()
            if row:
                columns = result.keys()
                return dict(zip(columns, row))
            return None
        except Exception:
            # If view doesn't exist, query from joined tables
            return self._get_product_from_join(product_id)

    def _get_products_from_join(self) -> List[dict]:
        """
        Get products by joining product_details and processed_products.

        Returns:
            List of product dictionaries
        """
        query = (
            self.db.query(
                ProductList.id.label("Product ID"),
                ProductList.product_url.label("Brand Website"),
                ProductDetails.product_url.label("Product Detail Page"),
                ProductDetails.product_name.label("Product Name"),
                ProcessedProduct.flavor.label("Flavors/Recipe"),
                ProcessedProduct.food_category.label("Food Category"),
                ProcessedProduct.sourcing_integrity.label("Sourcing Integrity"),
                ProcessedProduct.processing_method_1.label("Processing Method 1"),
                ProcessedProduct.processing_method_2.label("Processing Method 2"),
                ProcessedProduct.processing_adulteration_method.label("Processing/Adulteration Method"),
                ProcessedProduct.guaranteed_analysis_crude_protein_pct.label("Guaranteed Analysis - Crude Protein %"),
                ProcessedProduct.guaranteed_analysis_crude_fat_pct.label("Guaranteed Analysis - Crude Fat %"),
                ProcessedProduct.guaranteed_analysis_crude_fiber_pct.label("Guaranteed Analysis - Crude Fiber %"),
                ProcessedProduct.guaranteed_analysis_crude_moisture_pct.label("Guaranteed Analysis - Crude Moisture %"),
                ProcessedProduct.guaranteed_analysis_crude_ash_pct.label("Guaranteed Analysis - Crude Ash %"),
                ProcessedProduct.starchy_carb_pct.label("Starchy Carb %"),
                ProcessedProduct.nutritionally_adequate.label("Nutritionally Adequate"),
                ProcessedProduct.ingredients_all.label("Ingredients (All)"),
                ProcessedProduct.protein_ingredients_all.label("Protein Ingredients (All)"),
                ProcessedProduct.protein_ingredients_high.label("Protein Ingredients (High)"),
                ProcessedProduct.protein_ingredients_good.label("Protein Ingredients (Good)"),
                ProcessedProduct.protein_ingredients_moderate.label("Protein Ingredients (Moderate)"),
                ProcessedProduct.protein_ingredients_low.label("Protein Ingredients (Low)"),
                ProcessedProduct.protein_quality_class.label("Protein Quality Class"),
                ProcessedProduct.fat_ingredients_all.label("Fat Ingredients (All)"),
                ProcessedProduct.fat_ingredients_high.label("Fat Ingredients (High)"),
                ProcessedProduct.fat_ingredients_good.label("Fat Ingredients (Good)"),
                ProcessedProduct.fat_ingredients_low.label("Fat Ingredients (Low)"),
                ProcessedProduct.fat_quality_class.label("Fat Quality Class"),
                ProcessedProduct.carb_ingredients_all.label("Carb Ingredients (All)"),
                ProcessedProduct.carb_ingredients_high.label("Carb Ingredients (High)"),
                ProcessedProduct.carb_ingredients_good.label("Carb Ingredients (Good)"),
                ProcessedProduct.carb_ingredients_moderate.label("Carb Ingredients (Moderate)"),
                ProcessedProduct.carb_ingredients_low.label("Carb Ingredients (Low)"),
                ProcessedProduct.carb_quality_class.label("Carb Quality Class"),
                ProcessedProduct.fiber_ingredients_all.label("Fiber Ingredients (All)"),
                ProcessedProduct.fiber_ingredients_high.label("Fiber Ingredients (High)"),
                ProcessedProduct.fiber_ingredients_good.label("Fiber Ingredients (Good)"),
                ProcessedProduct.fiber_ingredients_moderate.label("Fiber Ingredients (Moderate)"),
                ProcessedProduct.fiber_ingredients_low.label("Fiber Ingredients (Low)"),
                ProcessedProduct.fiber_quality_class.label("Fiber Quality Class"),
                ProcessedProduct.dirty_dozen_ingredients.label("Dirty Dozen Ingredients"),
                ProcessedProduct.dirty_dozen_ingredients_count.label("Dirty Dozen Ingredients Count"),
                ProcessedProduct.synthetic_nutrition_addition.label("Synthetic Nutrition Addition"),
                ProcessedProduct.synthetic_nutrition_addition_count.label("Synthetic Nutrition Addition Count"),
                ProcessedProduct.longevity_additives.label("Longevity Additives"),
                ProcessedProduct.longevity_additives_count.label("Longevity Additives Count"),
                ProcessedProduct.food_storage.label("Food Storage"),
                ProcessedProduct.packaging_size.label("Packaging Size"),
                ProcessedProduct.shelf_life_thawed.label("Shelf Life (Thawed)"),
            )
            .join(ProductDetails, ProductList.id == ProductDetails.product_id)
            .outerjoin(ProcessedProduct, ProductDetails.id == ProcessedProduct.product_detail_id)
        )

        results = query.all()
        products = []
        for row in results:
            product_dict = {}
            for column, value in row._mapping.items():
                # Convert enum values to strings
                if hasattr(value, 'value'):
                    product_dict[column] = value.value
                else:
                    product_dict[column] = value
            products.append(product_dict)

        return products

    def _get_product_from_join(self, product_id: int) -> Optional[dict]:
        """
        Get a single product by ID from joined tables.

        Args:
            product_id: Product ID

        Returns:
            Product dictionary or None if not found
        """
        query = (
            self.db.query(
                ProductList.id.label("Product ID"),
                ProductList.product_url.label("Brand Website"),
                ProductDetails.product_url.label("Product Detail Page"),
                ProductDetails.product_name.label("Product Name"),
                ProcessedProduct.flavor.label("Flavors/Recipe"),
                ProcessedProduct.food_category.label("Food Category"),
                ProcessedProduct.sourcing_integrity.label("Sourcing Integrity"),
                ProcessedProduct.processing_method_1.label("Processing Method 1"),
                ProcessedProduct.processing_method_2.label("Processing Method 2"),
                ProcessedProduct.processing_adulteration_method.label("Processing/Adulteration Method"),
                ProcessedProduct.guaranteed_analysis_crude_protein_pct.label("Guaranteed Analysis - Crude Protein %"),
                ProcessedProduct.guaranteed_analysis_crude_fat_pct.label("Guaranteed Analysis - Crude Fat %"),
                ProcessedProduct.guaranteed_analysis_crude_fiber_pct.label("Guaranteed Analysis - Crude Fiber %"),
                ProcessedProduct.guaranteed_analysis_crude_moisture_pct.label("Guaranteed Analysis - Crude Moisture %"),
                ProcessedProduct.guaranteed_analysis_crude_ash_pct.label("Guaranteed Analysis - Crude Ash %"),
                ProcessedProduct.starchy_carb_pct.label("Starchy Carb %"),
                ProcessedProduct.nutritionally_adequate.label("Nutritionally Adequate"),
                ProcessedProduct.ingredients_all.label("Ingredients (All)"),
                ProcessedProduct.protein_ingredients_all.label("Protein Ingredients (All)"),
                ProcessedProduct.protein_ingredients_high.label("Protein Ingredients (High)"),
                ProcessedProduct.protein_ingredients_good.label("Protein Ingredients (Good)"),
                ProcessedProduct.protein_ingredients_moderate.label("Protein Ingredients (Moderate)"),
                ProcessedProduct.protein_ingredients_low.label("Protein Ingredients (Low)"),
                ProcessedProduct.protein_quality_class.label("Protein Quality Class"),
                ProcessedProduct.fat_ingredients_all.label("Fat Ingredients (All)"),
                ProcessedProduct.fat_ingredients_high.label("Fat Ingredients (High)"),
                ProcessedProduct.fat_ingredients_good.label("Fat Ingredients (Good)"),
                ProcessedProduct.fat_ingredients_low.label("Fat Ingredients (Low)"),
                ProcessedProduct.fat_quality_class.label("Fat Quality Class"),
                ProcessedProduct.carb_ingredients_all.label("Carb Ingredients (All)"),
                ProcessedProduct.carb_ingredients_high.label("Carb Ingredients (High)"),
                ProcessedProduct.carb_ingredients_good.label("Carb Ingredients (Good)"),
                ProcessedProduct.carb_ingredients_moderate.label("Carb Ingredients (Moderate)"),
                ProcessedProduct.carb_ingredients_low.label("Carb Ingredients (Low)"),
                ProcessedProduct.carb_quality_class.label("Carb Quality Class"),
                ProcessedProduct.fiber_ingredients_all.label("Fiber Ingredients (All)"),
                ProcessedProduct.fiber_ingredients_high.label("Fiber Ingredients (High)"),
                ProcessedProduct.fiber_ingredients_good.label("Fiber Ingredients (Good)"),
                ProcessedProduct.fiber_ingredients_moderate.label("Fiber Ingredients (Moderate)"),
                ProcessedProduct.fiber_ingredients_low.label("Fiber Ingredients (Low)"),
                ProcessedProduct.fiber_quality_class.label("Fiber Quality Class"),
                ProcessedProduct.dirty_dozen_ingredients.label("Dirty Dozen Ingredients"),
                ProcessedProduct.dirty_dozen_ingredients_count.label("Dirty Dozen Ingredients Count"),
                ProcessedProduct.synthetic_nutrition_addition.label("Synthetic Nutrition Addition"),
                ProcessedProduct.synthetic_nutrition_addition_count.label("Synthetic Nutrition Addition Count"),
                ProcessedProduct.longevity_additives.label("Longevity Additives"),
                ProcessedProduct.longevity_additives_count.label("Longevity Additives Count"),
                ProcessedProduct.food_storage.label("Food Storage"),
                ProcessedProduct.packaging_size.label("Packaging Size"),
                ProcessedProduct.shelf_life_thawed.label("Shelf Life (Thawed)"),
            )
            .join(ProductDetails, ProductList.id == ProductDetails.product_id)
            .outerjoin(ProcessedProduct, ProductDetails.id == ProcessedProduct.product_detail_id)
            .filter(ProductList.id == product_id)
        )

        row = query.first()
        if row:
            product_dict = {}
            for column, value in row._mapping.items():
                # Convert enum values to strings
                if hasattr(value, 'value'):
                    product_dict[column] = value.value
                else:
                    product_dict[column] = value
            return product_dict
        return None

