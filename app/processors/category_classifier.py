"""
Food Category Classifier for Dog Food Products.

This module classifies dog food products into categories (Raw, Fresh, Dry, Wet, Other)
based on keyword matching with product_category, product_name, and specifications.

Strategy:
1. Exact match on main keywords (highest confidence)
2. Phrase match on supporting keywords (medium confidence)
3. Partial match on supporting keywords (lower confidence)
4. Fallback to "Other" if no matches
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class FoodCategory(str, Enum):
    """Food category classifications."""

    RAW = "Raw"
    FRESH = "Fresh"
    DRY = "Dry"
    WET = "Wet"
    OTHER = "Other"


@dataclass
class CategoryKeywords:
    """Keywords for a specific food category."""

    main: List[str]
    supporting: List[str]


# Keyword definitions with priority
CATEGORY_KEYWORDS: Dict[FoodCategory, CategoryKeywords] = {
    FoodCategory.RAW: CategoryKeywords(
        main=["raw"],
        supporting=[
            "raw food",
            "raw frozen",
            "raw patties",
            "raw nuggets",
            "uncooked",
            "minimally processed",
            "primal raw",
            "nature's variety instinct raw",
            "raw meal",
            "raw recipe",
            "raw medallions",
            "frozen raw dog food",
            "raw blend",
            "raw coated",
            "raw bites",
            "raw infused",
            "raw bones",
            "raw mix-ins",
            "raw meat formula",
            "raw beef blend",
            "BARF diet",
            "biologically appropriate raw food",
        ],
    ),
    FoodCategory.FRESH: CategoryKeywords(
        main=["fresh"],
        supporting=[
            "fresh food",
            "gently cooked",
            "lightly cooked",
            "refrigerated",
            "homemade style",
            "fresh frozen",
            "fresh meals",
            "human grade meals",
            "cooked fresh",
            "fresh pet food",
            "whole food diet",
            "fridge-stored",
            "fresh delivery",
            "real food for dogs",
            "refrigerated dog food",
            "made fresh weekly",
            "freshly prepared",
            "gently prepared",
            "made fresh",
            "home-style dog food",
            "cooked to order",
            "fresh from our kitchen",
        ],
    ),
    FoodCategory.DRY: CategoryKeywords(
        main=["kibble"],
        supporting=[
            "kibble",
            "dry food",
            "dry kibble",
            "crunchy bites",
            "oven-baked dry",
            "extruded",
            "dry formula",
            "premium dry",
            "grain-free kibble",
            "dry dog formula",
            "dehydrated nuggets",
            "dry meal",
            "dry blend",
            "baked kibble",
            "shelf-stable kibble",
            "complete dry food",
            "balanced dry food",
            "oven-baked bites",
            "dry protein blend",
            "everyday kibble",
            "traditional kibble",
            "premium dry dog food",
            "dry crunch",
            "vet recommended kibble",
            "hard dog food",
            "biscuit-style food",
        ],
    ),
    FoodCategory.WET: CategoryKeywords(
        main=["wet", "canned"],
        supporting=[
            "wet food",
            "canned food",
            "moist food",
            "slow-cooked in gravy",
            "shelf-stable pouch",
            "stew-like consistency",
            "gently cooked and sealed",
            "cooked in the can",
            "retort pouch",
            "cooked for safety",
            "moisture rich food",
            "stewed",
            "loaf",
            "pate",
            "pâté",
            "broth",
            "gravy",
            "chunk in gravy",
            "shredded in broth",
            "homestyle stew",
            "meat chunks in jelly",
            "pouch food",
            "pull-tab can",
            "shelf-stable wet food",
            "slow cooked",
            "canned entrée",
            "meat loaf style",
            "toppers in gravy",
            "wet entree",
            "classic canned dog food",
            "gravy-rich",
            "soft dog food",
            "tender chunks",
            "loaf-style",
            "meaty stew",
            "canned recipe",
            "hydrated meals",
            "slow-cooked wet food",
            "premium canned dog food",
            "savory wet meal",
            "juicy dog food",
            "ready-to-serve wet",
            "broth-infused",
            "vet-recommended wet food",
            "complete wet food",
        ],
    ),
}


@dataclass
class ClassificationResult:
    """Result of category classification."""

    category: FoodCategory
    confidence: float  # 0.0 to 1.0
    matched_keywords: List[str]
    reason: str


class FoodCategoryClassifier:
    """
    Classifier for determining food category based on keyword matching.

    Uses a weighted scoring system:
    - Main keyword exact match: 1.0 confidence
    - Supporting keyword phrase match: 0.8 confidence
    - Supporting keyword partial match: 0.5 confidence
    """

    def __init__(self):
        """Initialize the classifier."""
        self.keywords = CATEGORY_KEYWORDS

    def classify(
        self,
        product_category: Optional[str] = None,
        product_name: Optional[str] = None,
        specifications: Optional[str] = None,
    ) -> ClassificationResult:
        """
        Classify a product into a food category.

        Args:
            product_category: Product category from scraped data
            product_name: Product name from scraped data
            specifications: Product specifications from scraped data

        Returns:
            ClassificationResult with category, confidence, and reasoning
        """
        # Combine all text fields
        combined_text = self._combine_text(
            product_category, product_name, specifications
        )

        if not combined_text:
            return ClassificationResult(
                category=FoodCategory.OTHER,
                confidence=1.0,
                matched_keywords=[],
                reason="No text available for classification",
            )

        # Normalize text
        normalized_text = self._normalize_text(combined_text)

        # Try to classify
        scores = {}
        matched_keywords_by_category = {}

        for category, keywords in self.keywords.items():
            score, matches = self._calculate_score(normalized_text, keywords)
            scores[category] = score
            matched_keywords_by_category[category] = matches

        # Get best match
        if scores:
            best_category = max(scores, key=scores.get)
            best_score = scores[best_category]

            if best_score > 0:
                return ClassificationResult(
                    category=best_category,
                    confidence=min(best_score, 1.0),
                    matched_keywords=matched_keywords_by_category[best_category],
                    reason=self._generate_reason(
                        best_category,
                        matched_keywords_by_category[best_category],
                        best_score,
                    ),
                )

        # No match found
        return ClassificationResult(
            category=FoodCategory.OTHER,
            confidence=0.8,
            matched_keywords=[],
            reason="No category keywords detected in product information",
        )

    def _combine_text(self, *fields: Optional[str]) -> str:
        """Combine multiple text fields into one."""
        combined = []
        for field in fields:
            if field and isinstance(field, str) and field.strip():
                combined.append(field.strip())
        return " | ".join(combined)

    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching (lowercase, clean whitespace)."""
        # Lowercase
        text = text.lower()
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        # Remove special characters but keep hyphens and apostrophes
        text = re.sub(r"[^\w\s\-\']", " ", text)
        # Clean up
        text = text.strip()
        return text

    def _calculate_score(
        self, text: str, keywords: CategoryKeywords
    ) -> Tuple[float, List[str]]:
        """
        Calculate confidence score for a category.

        Scoring:
        - Main keyword exact match: 1.0
        - Supporting phrase match: 0.8
        - Supporting partial match: 0.5

        Returns:
            (score, matched_keywords)
        """
        score = 0.0
        matched = []

        # Check main keywords (highest priority)
        for main_keyword in keywords.main:
            main_normalized = self._normalize_text(main_keyword)

            # Exact word match (word boundaries)
            pattern = r"\b" + re.escape(main_normalized) + r"\b"
            if re.search(pattern, text):
                score = max(score, 1.0)
                matched.append(main_keyword)

        # Check supporting keywords
        for support_keyword in keywords.supporting:
            support_normalized = self._normalize_text(support_keyword)

            # Multi-word phrase - check for exact phrase
            if len(support_normalized.split()) > 1:
                # Exact phrase match
                if support_normalized in text:
                    score = max(score, 0.8)
                    matched.append(support_keyword)
                # Partial phrase match (all words present)
                elif all(word in text for word in support_normalized.split()):
                    score = max(score, 0.6)
                    matched.append(f"{support_keyword} (partial)")
            else:
                # Single word - check with word boundaries
                pattern = r"\b" + re.escape(support_normalized) + r"\b"
                if re.search(pattern, text):
                    score = max(score, 0.7)
                    matched.append(support_keyword)

        return score, matched

    def _generate_reason(
        self, category: FoodCategory, matched_keywords: List[str], score: float
    ) -> str:
        """Generate human-readable reason for classification."""
        if not matched_keywords:
            return f"Classified as '{category.value}' with low confidence"

        confidence_level = (
            "high" if score >= 0.8 else "medium" if score >= 0.5 else "low"
        )

        # Limit to top 3 keywords for readability
        top_keywords = matched_keywords[:3]
        keywords_str = ", ".join(f"'{kw}'" for kw in top_keywords)

        if len(matched_keywords) > 3:
            keywords_str += f" (and {len(matched_keywords) - 3} more)"

        return (
            f"Classified as '{category.value}' with {confidence_level} confidence "
            f"based on keywords: {keywords_str}"
        )

    def classify_batch(
        self, products: List[Dict[str, Optional[str]]]
    ) -> List[ClassificationResult]:
        """
        Classify multiple products at once.

        Args:
            products: List of dicts with keys: product_category, product_name, specifications

        Returns:
            List of ClassificationResult objects
        """
        results = []
        for product in products:
            result = self.classify(
                product_category=product.get("product_category"),
                product_name=product.get("product_name"),
                specifications=product.get("specifications"),
            )
            results.append(result)
        return results


# Convenience function for quick classification
def classify_food_category(
    product_category: Optional[str] = None,
    product_name: Optional[str] = None,
    specifications: Optional[str] = None,
) -> ClassificationResult:
    """
    Quick classification function.

    Args:
        product_category: Product category from scraped data
        product_name: Product name from scraped data
        specifications: Product specifications from scraped data

    Returns:
        ClassificationResult

    Example:
        >>> result = classify_food_category(
        ...     product_name="Blue Buffalo Wilderness Chicken Recipe Kibble",
        ...     product_category="Dry Dog Food"
        ... )
        >>> print(result.category)  # FoodCategory.DRY
        >>> print(result.confidence)  # 1.0
        >>> print(result.reason)  # "Classified as 'Dry' with high confidence..."
    """
    classifier = FoodCategoryClassifier()
    return classifier.classify(product_category, product_name, specifications)


if __name__ == "__main__":
    # Example usage and testing
    print("=" * 70)
    print("FOOD CATEGORY CLASSIFIER - TEST EXAMPLES")
    print("=" * 70)

    test_cases = [
        {
            "name": "Kibble Product",
            "product_category": "Dry Dog Food",
            "product_name": "Blue Buffalo Wilderness High Protein Kibble",
            "specifications": "Grain-free dry formula",
        },
        {
            "name": "Raw Product",
            "product_category": "Frozen Dog Food",
            "product_name": "Primal Raw Frozen Beef Formula",
            "specifications": "Raw frozen patties, uncooked",
        },
        {
            "name": "Fresh Product",
            "product_category": "Fresh Dog Food",
            "product_name": "The Farmer's Dog Fresh Meals",
            "specifications": "Gently cooked, refrigerated, human grade",
        },
        {
            "name": "Wet Product",
            "product_category": "Canned Dog Food",
            "product_name": "Merrick Grain Free Wet Dog Food",
            "specifications": "Chunks in gravy, pate style",
        },
        {
            "name": "Unclear Product",
            "product_category": "Dog Food",
            "product_name": "Generic Brand Dog Food",
            "specifications": None,
        },
    ]

    classifier = FoodCategoryClassifier()

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'─' * 70}")
        print(f"Category: {test['product_category']}")
        print(f"Name: {test['product_name']}")
        print(f"Specs: {test['specifications']}")

        result = classifier.classify(
            product_category=test["product_category"],
            product_name=test["product_name"],
            specifications=test["specifications"],
        )

        print(f"\n→ Result: {result.category.value}")
        print(f"→ Confidence: {result.confidence:.2f}")
        print(
            f"→ Matched Keywords: {', '.join(result.matched_keywords) if result.matched_keywords else 'None'}"
        )
        print(f"→ Reason: {result.reason}")

    print(f"\n{'=' * 70}")
    print("TESTS COMPLETE")
    print("=" * 70)
