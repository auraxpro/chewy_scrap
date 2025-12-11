"""
Database configuration and session management.

This module provides the database engine, session factory, and base model class
for the Dog Food Scoring API.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency function to get database session.

    Yields:
        Database session

    Example:
        ```python
        from app.models.database import get_db

        def some_function(db: Session = Depends(get_db)):
            products = db.query(ProductList).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in SQLAlchemy models.
    Should be called on application startup.

    NOTE: Only creates base product tables. Score tables are optional
    and will be created when first used.
    """
    # Import all models here to ensure they are registered with Base
    from app.models.product import ProductDetails, ProductList

    # Only create product tables (score tables are optional)
    try:
        # Create only if they don't exist
        ProductList.__table__.create(bind=engine, checkfirst=True)
        ProductDetails.__table__.create(bind=engine, checkfirst=True)
        print("✅ Database tables initialized successfully!")
    except Exception as e:
        print(f"⚠️  Database tables may already exist: {e}")


def drop_all_tables() -> None:
    """
    Drop all tables from the database.

    WARNING: This will delete all data! Use with caution.
    Should only be used in development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped!")
