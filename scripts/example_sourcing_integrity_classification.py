#!/usr/bin/env python3
"""
Example Script: Sourcing Integrity Classification

This script demonstrates how to use the Sourcing Integrity Classifier
to classify dog food products into sourcing integrity categories.

Usage:
    python scripts/example_sourcing_integrity_classification.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.processors.sourcing_integrity_classifier import (
    SourcingIntegrityClassifier,
    classify_sourcing_integrity,
)


def example_1_basic_classification():
    """Example 1: Basic classification using convenience function."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Classification")
    print("=" * 70)

    # Simple classification
    result = classify_sourcing_integrity(
        product_name="Organic Human Grade Chicken Recipe",
        specifications="USDA organic certified, made in human food facility",
        ingredient_list="Organic chicken, organic vegetables, certified organic",
    )

    print(f"\n✓ Sourcing Integrity: {result.sourcing_integrity.value}")
    print(f"✓ Confidence: {result.confidence:.2f}")
    print(f"✓ Matched Keywords: {', '.join(result.matched_keywords[:3])}")
    print(f"✓ Reason: {result.reason}")


def example_2_classifier_instance():
    """Example 2: Using classifier instance for multiple classifications."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multiple Classifications")
    print("=" * 70)

    # Create classifier instance once (efficient for multiple uses)
    classifier = SourcingIntegrityClassifier()

    test_products = [
        {
            "name": "Premium Organic Human Grade",
            "product_name": "Organic Human Grade Beef Formula",
            "specifications": "USDA organic, human grade ingredients",
            "ingredient_list": "Organic beef, organic vegetables",
        },
        {
            "name": "Human Grade Only",
            "product_name": "Human Grade Chicken Recipe",
            "specifications": "USDA inspected, human edible ingredients",
            "ingredient_list": "Human grade chicken, vegetables",
        },
        {
            "name": "Feed Grade",
            "product_name": "Complete Dog Food",
            "specifications": "Feed grade formula",
            "ingredient_list": "Meat meal, by-products, rendered meat",
        },
        {
            "name": "Standard Quality",
            "product_name": "Premium Dog Food",
            "specifications": "High quality ingredients",
            "ingredient_list": "Chicken, rice, vegetables",
        },
    ]

    print("\nClassifying products:")
    print("-" * 70)

    for product in test_products:
        result = classifier.classify(
            product_name=product["product_name"],
            specifications=product["specifications"],
            ingredient_list=product["ingredient_list"],
        )

        print(f"\n📦 {product['name']}")
        print(f"   Category: {result.sourcing_integrity.value}")
        print(f"   Confidence: {result.confidence:.2f}")
        if result.matched_keywords:
            print(f"   Keywords: {', '.join(result.matched_keywords[:2])}")


def example_3_batch_processing():
    """Example 3: Batch processing multiple products."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Batch Processing")
    print("=" * 70)

    classifier = SourcingIntegrityClassifier()

    products = [
        {
            "product_category": "Premium Dog Food",
            "product_name": "Organic Human Grade Salmon Recipe",
            "specifications": "USDA organic certified, human food facility",
            "ingredient_list": "Organic salmon, organic sweet potatoes",
        },
        {
            "product_category": "Dog Food",
            "product_name": "Human Grade Turkey Meal",
            "specifications": "Human edible, USDA inspected",
            "ingredient_list": "Human grade turkey, vegetables",
        },
        {
            "product_category": "Budget Dog Food",
            "product_name": "Complete Nutrition Formula",
            "specifications": "Feed grade ingredients",
            "ingredient_list": "Meat by-product meal, corn, wheat",
        },
    ]

    # Batch classify
    results = classifier.classify_batch(products)

    print(f"\nProcessed {len(results)} products:\n")

    # Summary by category
    from collections import Counter

    categories = Counter(r.sourcing_integrity.value for r in results)

    for category, count in categories.items():
        print(f"  {category:25} {count} product(s)")

    print("\nDetailed Results:")
    print("-" * 70)

    for i, (product, result) in enumerate(zip(products, results), 1):
        print(f"\n{i}. {product['product_name']}")
        print(f"   → {result.sourcing_integrity.value}")
        print(f"   → Confidence: {result.confidence:.2f}")


def example_4_database_integration():
    """Example 4: Database integration example (requires DB connection)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Database Integration (Demo)")
    print("=" * 70)

    print("\nTo process products from database:")
    print("-" * 70)

    print("""
from app.processors.sourcing_integrity_processor import SourcingIntegrityProcessor
from app.models.database import SessionLocal

# Create database session
db = SessionLocal()

try:
    # Create processor
    processor = SourcingIntegrityProcessor(db)

    # Process single product
    processed = processor.process_single(product_detail_id=1)
    print(f"Sourcing: {processed.sourcing_integrity}")

    # Process all unprocessed products
    results = processor.process_all(skip_existing=True, limit=100)
    print(f"Processed: {results['success']} products")

    # Print statistics
    processor.print_statistics()

finally:
    db.close()
""")


def example_5_detailed_analysis():
    """Example 5: Detailed analysis of classification results."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Detailed Classification Analysis")
    print("=" * 70)

    classifier = SourcingIntegrityClassifier()

    # Analyze a complex product
    result = classifier.classify(
        product_category="Premium Organic Dog Food",
        product_name="Organic Human Grade Chicken & Vegetable Recipe",
        specifications="USDA organic certified, made in human food facility, "
        "human grade ingredients, small batch organic",
        ingredient_list="Organic chicken, organic sweet potatoes, organic carrots, "
        "organic peas, USDA organic certified",
    )

    print("\n📊 Classification Report:")
    print("-" * 70)
    print(f"Sourcing Integrity: {result.sourcing_integrity.value}")
    print(f"Confidence Score: {result.confidence:.2f}")

    # Confidence interpretation
    if result.confidence >= 0.8:
        confidence_level = "HIGH ✓"
    elif result.confidence >= 0.5:
        confidence_level = "MEDIUM ~"
    else:
        confidence_level = "LOW ⚠"

    print(f"Confidence Level: {confidence_level}")

    print(f"\nMatched Keywords ({len(result.matched_keywords)}):")
    for i, keyword in enumerate(result.matched_keywords, 1):
        print(f"  {i}. {keyword}")

    print(f"\nClassification Reason:")
    print(f"  {result.reason}")


def example_6_edge_cases():
    """Example 6: Handle edge cases and unusual inputs."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Edge Cases")
    print("=" * 70)

    classifier = SourcingIntegrityClassifier()

    edge_cases = [
        {
            "description": "Empty input",
            "data": {"product_name": None, "specifications": None},
        },
        {
            "description": "Only organic (no human grade)",
            "data": {
                "product_name": "Organic Dog Food",
                "specifications": "USDA organic certified",
                "ingredient_list": "Organic chicken meal",
            },
        },
        {
            "description": "Mixed signals",
            "data": {
                "product_name": "Premium Recipe",
                "specifications": "Human grade chicken, with meat meal",
                "ingredient_list": "Human edible chicken, feed grade corn",
            },
        },
        {
            "description": "Very short text",
            "data": {"product_name": "Dog Food"},
        },
    ]

    print("\nTesting edge cases:")
    print("-" * 70)

    for case in edge_cases:
        result = classifier.classify(**case["data"])
        print(f"\n{case['description']}:")
        print(f"  Result: {result.sourcing_integrity.value}")
        print(f"  Confidence: {result.confidence:.2f}")


def example_7_confidence_filtering():
    """Example 7: Filter results by confidence threshold."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Confidence-Based Filtering")
    print("=" * 70)

    classifier = SourcingIntegrityClassifier()

    products = [
        {
            "product_name": "Organic Human Grade Formula",
            "specifications": "USDA organic, human food facility",
        },
        {
            "product_name": "Natural Recipe",
            "specifications": "Premium ingredients",
        },
        {
            "product_name": "Feed Grade Mix",
            "specifications": "Animal feed quality",
        },
    ]

    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.5

    high_confidence_results = []
    medium_confidence_results = []
    low_confidence_results = []

    for product in products:
        result = classifier.classify(**product)

        if result.confidence >= HIGH_CONFIDENCE:
            high_confidence_results.append((product, result))
        elif result.confidence >= MEDIUM_CONFIDENCE:
            medium_confidence_results.append((product, result))
        else:
            low_confidence_results.append((product, result))

    print(f"\n✓ High Confidence ({HIGH_CONFIDENCE}+): {len(high_confidence_results)}")
    for product, result in high_confidence_results:
        print(f"  - {product['product_name']}: {result.sourcing_integrity.value}")

    print(
        f"\n~ Medium Confidence ({MEDIUM_CONFIDENCE}-{HIGH_CONFIDENCE}): {len(medium_confidence_results)}"
    )
    for product, result in medium_confidence_results:
        print(f"  - {product['product_name']}: {result.sourcing_integrity.value}")

    print(f"\n⚠ Low Confidence (<{MEDIUM_CONFIDENCE}): {len(low_confidence_results)}")
    for product, result in low_confidence_results:
        print(f"  - {product['product_name']}: {result.sourcing_integrity.value}")


def run_all_examples():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("SOURCING INTEGRITY CLASSIFICATION - EXAMPLES")
    print("*" * 70)

    examples = [
        example_1_basic_classification,
        example_2_classifier_instance,
        example_3_batch_processing,
        example_4_database_integration,
        example_5_detailed_analysis,
        example_6_edge_cases,
        example_7_confidence_filtering,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n⚠️  Error in {example.__name__}: {e}")

    print("\n" + "*" * 70)
    print("ALL EXAMPLES COMPLETE")
    print("*" * 70)


if __name__ == "__main__":
    run_all_examples()
