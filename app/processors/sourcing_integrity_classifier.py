"""
Sourcing Integrity Classifier for Dog Food Products.

This module classifies dog food products into sourcing integrity categories
(Human Grade (organic), Human Grade, Feed Grade, Other) based on keyword matching
with product_category, product_name, specifications, and ingredient_list.

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


class SourcingIntegrity(str, Enum):
    """Sourcing integrity classifications."""

    HUMAN_GRADE_ORGANIC = "Human Grade (organic)"
    HUMAN_GRADE = "Human Grade"
    FEED_GRADE = "Feed Grade"
    OTHER = "Other"


@dataclass
class SourcingKeywords:
    """Keywords for a specific sourcing integrity category."""

    main: List[str]
    supporting: List[str]


# Keyword definitions with priority
SOURCING_KEYWORDS: Dict[SourcingIntegrity, SourcingKeywords] = {
    SourcingIntegrity.HUMAN_GRADE_ORGANIC: SourcingKeywords(
        main=["organic human-grade"],
        supporting=[
            "USDA organic",
            "certified organic",
            "organic meat",
            "organic vegetables",
            "organic certified",
            "human grade + organic",
            "made with organic ingredients",
            "organic-certified facility",
            "organic produce",
            "organically sourced",
            "all-organic formula",
            "non-GMO and organic",
            "organic pet food",
            "100% organic",
            "premium organic ingredients",
            "organic human grade food",
            "organic superfoods",
            "clean organic label",
            "small batch organic",
            "organic chicken",
            "organic beef",
            "organic lamb",
            "organic turkey",
            "humanely raised organic",
            "organic whole foods",
        ],
    ),
    SourcingIntegrity.HUMAN_GRADE: SourcingKeywords(
        main=["human grade", "human-grade"],
        supporting=[
            "human grade ingredients",
            "human quality",
            "USDA inspected",
            "fit for human consumption",
            "human edible",
            "made in human food facility",
            "made in USDA-inspected facility",
            "cooked in human-grade kitchens",
            "made in human food kitchens",
            "crafted to human food standards",
            "made in USDA kitchen",
            "inspected for human consumption",
            "food-grade facility",
            "premium human-grade meat",
            "prepared in human-quality facilities",
            "meets human food safety standards",
            "small batch human grade",
            "restaurant quality",
            "human-approved formulas",
            "made with human edible meat",
            "real food for dogs",
            "human-grade sourcing",
            "home-cooked quality",
        ],
    ),
    SourcingIntegrity.FEED_GRADE: SourcingKeywords(
        main=["feed grade", "feed-grade"],
        supporting=[
            "feed quality",
            "animal feed",
            "not for human consumption",
            "rendered meat",
            "by-products",
            "meat meal",
            "feed-safe",
            "pet feed",
            "feed-grade ingredients",
            "feed-use only",
            "not USDA inspected",
            "4D meat",
            "meat by-product meal",
            "not human edible",
            "factory scraps",
            "feed-grade facility",
            "waste-derived protein",
            "animal digest",
            "feed standard",
            "bulk animal feed",
            "meat and bone meal",
            "slaughterhouse waste",
            "unfit for human consumption",
        ],
    ),
}


@dataclass
class SourcingClassificationResult:
    """Result of sourcing integrity classification."""

    sourcing_integrity: SourcingIntegrity
    confidence: float  # 0.0 to 1.0
    matched_keywords: List[str]
    reason: str


class SourcingIntegrityClassifier:
    """
    Classifier for determining sourcing integrity based on keyword matching.

    Uses a weighted scoring system:
    - Main keyword exact match: 1.0 confidence
    - Supporting keyword phrase match: 0.8 confidence
    - Supporting keyword partial match: 0.5 confidence

    Priority order:
    1. Human Grade (organic) - highest priority, must have both human grade and organic indicators
    2. Human Grade - second priority
    3. Feed Grade - third priority
    4. Other - fallback
    """

    def __init__(self):
        """Initialize the classifier."""
        self.keywords = SOURCING_KEYWORDS

    def classify(
        self,
        product_name: Optional[str] = None,
        details: Optional[str] = None,
        more_details: Optional[str] = None,
        specifications: Optional[str] = None,
    ) -> SourcingClassificationResult:
        """
        Classify a product into a sourcing integrity category.

        Args:
            product_name: Product name from scraped data
            details: Product category from scraped data
            more_details: Product specifications from scraped data
            specifications: Product specifications from scraped data

        Returns:
            SourcingClassificationResult with category, confidence, and reasoning
        """
        # Combine all text fields
        combined_text = self._combine_text(
            details, product_name, more_details, specifications
        )

        if not combined_text:
            return SourcingClassificationResult(
                sourcing_integrity=SourcingIntegrity.OTHER,
                confidence=1.0,
                matched_keywords=[],
                reason="No text available for classification",
            )

        # Normalize text
        normalized_text = self._normalize_text(combined_text)

        # Calculate scores for all categories
        scores = {}
        matched_keywords_by_category = {}

        for category, keywords in self.keywords.items():
            score, matches = self._calculate_score(normalized_text, keywords)
            scores[category] = score
            matched_keywords_by_category[category] = matches

        # Special handling for Human Grade (organic)
        # Must have indicators of BOTH human grade AND organic
        if scores.get(SourcingIntegrity.HUMAN_GRADE_ORGANIC, 0) > 0:
            # Check if we have both human grade and organic indicators
            has_human_grade = self._has_human_grade_indicator(
                normalized_text,
                matched_keywords_by_category[SourcingIntegrity.HUMAN_GRADE_ORGANIC],
            )
            has_organic = self._has_organic_indicator(
                normalized_text,
                matched_keywords_by_category[SourcingIntegrity.HUMAN_GRADE_ORGANIC],
            )

            if has_human_grade and has_organic:
                # Valid Human Grade (organic)
                return SourcingClassificationResult(
                    sourcing_integrity=SourcingIntegrity.HUMAN_GRADE_ORGANIC,
                    confidence=min(scores[SourcingIntegrity.HUMAN_GRADE_ORGANIC], 1.0),
                    matched_keywords=matched_keywords_by_category[
                        SourcingIntegrity.HUMAN_GRADE_ORGANIC
                    ],
                    reason=self._generate_reason(
                        SourcingIntegrity.HUMAN_GRADE_ORGANIC,
                        matched_keywords_by_category[
                            SourcingIntegrity.HUMAN_GRADE_ORGANIC
                        ],
                        scores[SourcingIntegrity.HUMAN_GRADE_ORGANIC],
                    ),
                )

        # Check remaining categories in priority order
        priority_order = [
            SourcingIntegrity.HUMAN_GRADE,
            SourcingIntegrity.FEED_GRADE,
        ]

        for category in priority_order:
            if scores.get(category, 0) > 0:
                return SourcingClassificationResult(
                    sourcing_integrity=category,
                    confidence=min(scores[category], 1.0),
                    matched_keywords=matched_keywords_by_category[category],
                    reason=self._generate_reason(
                        category,
                        matched_keywords_by_category[category],
                        scores[category],
                    ),
                )

        # No match found
        return SourcingClassificationResult(
            sourcing_integrity=SourcingIntegrity.OTHER,
            confidence=0.8,
            matched_keywords=[],
            reason="No sourcing integrity keywords detected in product information",
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

    def _has_human_grade_indicator(
        self, text: str, matched_keywords: List[str]
    ) -> bool:
        """Check if text has human grade indicators."""
        human_grade_indicators = [
            "human grade",
            "human-grade",
            "human quality",
            "human edible",
            "human food facility",
            "human food kitchens",
            "human food standards",
            "human consumption",
            "food-grade facility",
            "human-grade meat",
            "human-quality facilities",
            "human food safety",
            "human-approved",
            "human edible meat",
            "human-grade sourcing",
        ]

        # Check if text contains human grade indicators
        for indicator in human_grade_indicators:
            if indicator in text:
                return True

        # Check matched keywords
        for keyword in matched_keywords:
            keyword_lower = keyword.lower()
            if "human" in keyword_lower and (
                "grade" in keyword_lower
                or "quality" in keyword_lower
                or "edible" in keyword_lower
            ):
                return True

        return False

    def _has_organic_indicator(self, text: str, matched_keywords: List[str]) -> bool:
        """Check if text has organic indicators."""
        organic_indicators = [
            "organic",
            "usda organic",
            "certified organic",
            "organically",
        ]

        # Check if text contains organic indicators
        for indicator in organic_indicators:
            if indicator in text:
                return True

        # Check matched keywords
        for keyword in matched_keywords:
            if "organic" in keyword.lower():
                return True

        return False

    def _calculate_score(
        self, text: str, keywords: SourcingKeywords
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

            # For multi-word main keywords, check for phrase match
            if len(main_normalized.split()) > 1:
                if main_normalized in text:
                    score = max(score, 1.0)
                    matched.append(main_keyword)
            else:
                # Single word - check with word boundaries
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
        self, category: SourcingIntegrity, matched_keywords: List[str], score: float
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
    ) -> List[SourcingClassificationResult]:
        """
        Classify multiple products at once.

        Args:
            products: List of dicts with keys: product_name,
                     details, more_details, specifications

        Returns:
            List of SourcingClassificationResult objects
        """
        results = []
        for product in products:
            result = self.classify(
                product_name=product.get("product_name"),
                details=product.get("details"),
                more_details=product.get("more_details"),
                specifications=product.get("specifications"),
            )
            results.append(result)
        return results


# Convenience function for quick classification
def classify_sourcing_integrity(
    product_name: Optional[str] = None,
    details: Optional[str] = None,
    more_details: Optional[str] = None,
    specifications: Optional[str] = None,
) -> SourcingClassificationResult:
    """
    Quick classification function.

    Args:
        product_name: Product name from scraped data
        details: Additional details about the product
        more_details: More details about the product
        specifications: Product specifications from scraped data

    Returns:
        SourcingClassificationResult

    Example:
        >>> result = classify_sourcing_integrity(
        ...     product_name="Organic Human Grade Chicken Recipe",
        ...     details="USDA organic certified",
        ...     more_details="human grade ingredients",
        ...     specifications="USDA organic certified, human grade ingredients"
        ... )
        >>> print(result.sourcing_integrity)  # SourcingIntegrity.HUMAN_GRADE_ORGANIC
        >>> print(result.confidence)  # 1.0
        >>> print(result.reason)  # "Classified as 'Human Grade (organic)'..."
    """
    classifier = SourcingIntegrityClassifier()
    return classifier.classify(product_name, details, more_details, specifications)


if __name__ == "__main__":
    # Example usage and testing
    print("=" * 70)
    print("SOURCING INTEGRITY CLASSIFIER - TEST EXAMPLES")
    print("=" * 70)

    test_cases = [
        {
            "name": "Human Grade Organic Product",
            "product_name": "Organic Human Grade Chicken Recipe",
            "details": "Dog Food",
            "more_details": "USDA organic certified, made in human food facility",
            "specifications": "USDA organic certified, made in human food facility",
        },
        {
            "name": "Human Grade Product",
            "product_name": "Human Grade Beef Formula",
            "details": "Premium Dog Food",
            "more_details": "Human edible beef, restaurant quality vegetables",
            "specifications": "Human grade ingredients, USDA inspected facility",
        },
        {
            "name": "Feed Grade Product",
            "details": "Dog Food",
            "product_name": "Complete Dog Food",
            "specifications": "Feed grade, meat meal, by-products",
            "more_details": "Meat by-product meal, rendered meat, animal feed quality",
        },
        {
            "name": "Organic Only (Not Human Grade)",
            "details": "Organic Dog Food",
            "product_name": "Organic Chicken Meal",
            "specifications": "USDA organic certified",
            "more_details": "Organic chicken meal, organic vegetables",
        },
        {
            "name": "Unclear Product",
            "details": "Dog Food",
            "product_name": "Premium Recipe",
            "specifications": "High quality ingredients",
            "more_details": None,
        },
    ]

    classifier = SourcingIntegrityClassifier()

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'─' * 70}")
        print(f"Name: {test['product_name']}")
        print(f"Details: {test['details']}")
        print(f"More Details: {test['more_details']}")
        print(f"Specs: {test['specifications']}")

        result = classifier.classify(
            product_name=test["product_name"],
            details=test["details"],
            more_details=test["more_details"],
            specifications=test["specifications"],
        )

        print(f"\n→ Result: {result.sourcing_integrity.value}")
        print(f"→ Confidence: {result.confidence:.2f}")
        print(
            f"→ Matched Keywords: {', '.join(result.matched_keywords) if result.matched_keywords else 'None'}"
        )
        print(f"→ Reason: {result.reason}")

    print(f"\n{'=' * 70}")
    print("TESTS COMPLETE")
    print("=" * 70)
