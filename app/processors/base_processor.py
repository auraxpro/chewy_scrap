"""
Base processor module for the Dog Food Scoring API.

This module provides an abstract base class for all data processors
that transform and normalize raw scraped data.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.product import ProductDetails, ProductList


class BaseProcessor(ABC):
    """
    Abstract base class for data processors.

    All processors should inherit from this class and implement the
    process() method to perform their specific data transformation.
    """

    def __init__(self, db: Session):
        """
        Initialize the processor.

        Args:
            db: Database session for accessing product data
        """
        self.db = db

    @abstractmethod
    def process(self, product: ProductList) -> Dict[str, Any]:
        """
        Process a product and return the processed data.

        This method must be implemented by all subclasses.

        Args:
            product: ProductList instance to process

        Returns:
            Dictionary containing processed data

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement process()")

    def can_process(self, product: ProductList) -> bool:
        """
        Check if the product can be processed.

        Default implementation checks if product has been scraped
        and has details available.

        Args:
            product: ProductList instance to check

        Returns:
            True if product can be processed, False otherwise
        """
        return product.scraped and not product.skipped and product.details is not None

    def process_batch(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Process multiple products in batch.

        Args:
            limit: Maximum number of products to process
            offset: Number of products to skip

        Returns:
            Dictionary containing batch processing results
        """
        query = (
            self.db.query(ProductList)
            .filter(ProductList.scraped == True)
            .filter(ProductList.skipped == False)
            .filter(ProductList.processed == False)
            .offset(offset)
        )

        if limit:
            query = query.limit(limit)

        products = query.all()

        results = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        for product in products:
            try:
                if self.can_process(product):
                    processed_data = self.process(product)
                    self._save_processed_data(product, processed_data)
                    results["successful"] += 1
                    results["total_processed"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"product_id": product.id, "error": str(e)})

        return results

    def _save_processed_data(
        self, product: ProductList, processed_data: Dict[str, Any]
    ) -> None:
        """
        Save processed data to the database.

        Args:
            product: ProductList instance
            processed_data: Dictionary of processed data to save
        """
        # Update product details with processed data
        if product.details:
            for key, value in processed_data.items():
                if hasattr(product.details, key):
                    setattr(product.details, key, value)

        # Mark product as processed
        product.processed = True
        self.db.commit()

    def get_name(self) -> str:
        """
        Get the processor name.

        Returns:
            Name of the processor
        """
        return self.__class__.__name__

    def get_description(self) -> str:
        """
        Get the processor description.

        Returns:
            Description of what the processor does
        """
        return self.__doc__ or "No description available"

    def validate_input(self, product: ProductList) -> bool:
        """
        Validate that the product has required data for processing.

        Args:
            product: ProductList instance to validate

        Returns:
            True if valid, False otherwise
        """
        if not product.details:
            return False

        # Check if product details exist
        if not product.details.product_name:
            return False

        return True

    def log_processing(self, product: ProductList, status: str, message: str) -> None:
        """
        Log processing information.

        Args:
            product: ProductList instance being processed
            status: Processing status (success, error, warning)
            message: Log message
        """
        print(
            f"[{self.get_name()}] Product ID {product.id} - {status.upper()}: {message}"
        )
