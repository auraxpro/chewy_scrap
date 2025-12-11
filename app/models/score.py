"""
Score models for the Dog Food Scoring API.

This module contains SQLAlchemy ORM models for product scores and their components.

NOTE: These tables are optional and will be created when first used.
They are not required for basic scraping functionality.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.database import Base


class ProductScore(Base):
    """
    Product score model representing the overall score for a product.

    This table stores the final calculated score for each product along with
    metadata about when and how the score was calculated.

    NOTE: This table is optional and only created when scoring features are used.
    """

    __tablename__ = "product_scores"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to ProductList
    product_id = Column(
        Integer,
        ForeignKey("products_list.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Overall score (0-100)
    total_score = Column(Float, nullable=False, index=True)

    # Score version (for tracking scoring algorithm changes)
    score_version = Column(String, nullable=False, default="1.0.0")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships - backref for optional relationship
    components = relationship(
        "ScoreComponent",
        back_populates="product_score",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<ProductScore(id={self.id}, product_id={self.product_id}, "
            f"total_score={self.total_score:.2f})>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "total_score": self.total_score,
            "score_version": self.score_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "calculated_at": self.calculated_at.isoformat()
            if self.calculated_at
            else None,
            "components": [component.to_dict() for component in self.components]
            if self.components
            else [],
        }


class ScoreComponent(Base):
    """
    Score component model representing individual scoring factors.

    This table stores the breakdown of scores for each scoring dimension
    (e.g., ingredient quality, nutritional value, processing method, price-value).

    NOTE: This table is optional and only created when scoring features are used.
    """

    __tablename__ = "score_components"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to ProductScore
    score_id = Column(
        Integer,
        ForeignKey("product_scores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Component details
    component_name = Column(String, nullable=False, index=True)
    component_score = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)  # Weight in overall score calculation
    weighted_score = Column(Float, nullable=False)  # component_score * weight

    # Additional metadata
    details = Column(Text, nullable=True)  # JSON string with detailed breakdown
    confidence = Column(Float, nullable=True)  # Confidence level (0-1)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product_score = relationship("ProductScore", back_populates="components")

    def __repr__(self):
        return (
            f"<ScoreComponent(id={self.id}, score_id={self.score_id}, "
            f"name={self.component_name}, score={self.component_score:.2f})>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "score_id": self.score_id,
            "component_name": self.component_name,
            "component_score": self.component_score,
            "weight": self.weight,
            "weighted_score": self.weighted_score,
            "details": self.details,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
