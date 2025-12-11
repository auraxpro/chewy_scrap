"""
Nutritionally Adequate Classifier for Dog Food Products.

This module identifies whether a product is nutritionally adequate (complete and balanced)
by analyzing product details, specifications, and feeding instructions.

Strategy:
1. Combine text from details, more_details, specifications, feeding_instructions, transition_instructions
2. Normalize text
3. Detect "No" first (not nutritionally complete & balanced)
4. Then detect "Yes" (complete and balanced)
5. Otherwise classify as "Other"
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class NutritionallyAdequateResult:
    """Result of nutritionally adequate classification."""

    nutritionally_adequate: str  # "Yes", "No", or "Other"
    confidence: float  # Confidence score (0.0 to 1.0)
    matched_keywords: List[str]  # Keywords that matched
    reason: str  # Explanation of classification


@dataclass
class CategoryKeywords:
    """Keywords for a specific nutritionally adequate category."""

    main: List[str]
    supporting: List[str]


# Yes Keywords - Complete and Balanced
YES_KEYWORDS = CategoryKeywords(
    main=[
        "complete and balanced",
    ],
    supporting=[
        "formulated to meet aafco dog food nutrient profiles for",
        "animal feeding tests using aafco procedures substantiate that this product provides complete and balanced nutrition for",
        "this product is formulated to meet the nutritional levels established by the aafco dog food nutrient profiles for maintenance of adult dogs",
        "animal feeding tests using aafco procedures",
        "substantiates complete and balanced nutrition",
        "meets aafco nutrient profiles",
        "formulated for all life stages",
        "meets nutritional levels established by aafco",
        "aafco compliant",
        "nutritionally adequate",
        "meets dog food nutrient guidelines",
        "balanced for maintenance",
        "suitable for growth and maintenance",
        "developed to support dog health",
        "veterinarian formulated to aafco standards",
        "aafco feeding trials",
        "provides full and balanced nutrition",
        "meets all nutritional requirements",
        "covers canine nutritional needs",
        "meets aafco recommendations",
        "aafco approved formulation",
    ],
)

# No Keywords - Not Nutritionally Complete & Balanced
NO_KEYWORDS = CategoryKeywords(
    main=[
        "not nutritionally complete & balanced",
        "not nutritionally complete and balanced",
    ],
    supporting=[
        "this product is intended for intermittent or supplemental feeding only",
        "this food is not complete and balanced and should be fed only as a topper or with a complete and balanced base food",
        "intended for intermittent or supplemental feeding only",
        "not complete and balanced",
        "feed as a topper only",
        "feed with a complete and balanced base",
        "not a sole source of nutrition",
        "should be fed with a balanced food",
        "does not meet aafco nutrient profiles",
        "incomplete nutrition",
        "not a complete diet",
        "lacks full nutrient profile",
        "not suitable as primary food",
        "for intermittent feeding",
        "not for long-term feeding",
        "supplemental use only",
        "feed in combination with other foods",
        "requires additional nutritional support",
        "not aafco compliant",
        "not formulated to meet aafco standards",
        "unbalanced formula",
        "missing essential nutrients",
    ],
)


class NutritionallyAdequateClassifier:
    """
    Classifier for determining nutritionally adequate status based on keyword matching.

    Uses a weighted scoring system:
    - Main keyword exact match: 1.0 confidence
    - Supporting keyword phrase match: 0.8 confidence
    - Supporting keyword partial match: 0.5 confidence

    Priority order:
    1. No - highest priority (detect first)
    2. Yes - second priority
    3. Other - fallback
    """

    def __init__(self):
        """Initialize the classifier."""
        self.yes_keywords = YES_KEYWORDS
        self.no_keywords = NO_KEYWORDS

    def classify(
        self,
        details: Optional[str] = None,
        more_details: Optional[str] = None,
        specifications: Optional[str] = None,
        feeding_instructions: Optional[str] = None,
        transition_instructions: Optional[str] = None,
    ) -> NutritionallyAdequateResult:
        """
        Classify a product into a nutritionally adequate category.

        Args:
            details: Product details from scraped data
            more_details: Additional product details
            specifications: Product specifications
            feeding_instructions: Feeding instructions
            transition_instructions: Transition instructions

        Returns:
            NutritionallyAdequateResult with category, confidence, and reasoning
        """
        # Combine all text fields
        combined_text = self._combine_text(
            details,
            more_details,
            specifications,
            feeding_instructions,
            transition_instructions,
        )

        if not combined_text:
            return NutritionallyAdequateResult(
                nutritionally_adequate="Other",
                confidence=1.0,
                matched_keywords=[],
                reason="No text available for classification",
            )

        # Normalize text
        normalized_text = self._normalize_text(combined_text)

        # Check for "No" first (highest priority)
        no_score, no_matched = self._calculate_score(normalized_text, self.no_keywords)
        if no_score > 0:
            return NutritionallyAdequateResult(
                nutritionally_adequate="No",
                confidence=min(no_score, 1.0),
                matched_keywords=no_matched,
                reason=self._generate_reason("No", no_matched, no_score),
            )

        # Check for "Yes" second
        yes_score, yes_matched = self._calculate_score(
            normalized_text, self.yes_keywords
        )
        if yes_score > 0:
            return NutritionallyAdequateResult(
                nutritionally_adequate="Yes",
                confidence=min(yes_score, 1.0),
                matched_keywords=yes_matched,
                reason=self._generate_reason("Yes", yes_matched, yes_score),
            )

        # No match found - classify as "Other"
        return NutritionallyAdequateResult(
            nutritionally_adequate="Other",
            confidence=0.8,
            matched_keywords=[],
            reason="No nutritionally adequate keywords detected in product information",
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
    ) -> tuple[float, List[str]]:
        """
        Calculate score for a category based on keyword matching.

        Args:
            text: Normalized text to search
            keywords: CategoryKeywords with main and supporting keywords

        Returns:
            Tuple of (score, matched_keywords_list)
        """
        score = 0.0
        matched_keywords = []

        # Check main keywords (exact match = 1.0)
        for keyword in keywords.main:
            normalized_keyword = self._normalize_text(keyword)
            if normalized_keyword in text:
                score += 1.0
                matched_keywords.append(keyword)

        # Check supporting keywords
        for keyword in keywords.supporting:
            normalized_keyword = self._normalize_text(keyword)
            # Phrase match (exact phrase) = 0.8
            if normalized_keyword in text:
                score += 0.8
                matched_keywords.append(keyword)
            # Partial match (contains all words) = 0.5
            elif self._partial_match(text, normalized_keyword):
                score += 0.5
                matched_keywords.append(keyword)

        return score, matched_keywords

    def _partial_match(self, text: str, keyword: str) -> bool:
        """Check if all words in keyword appear in text."""
        keyword_words = keyword.split()
        return all(word in text for word in keyword_words if len(word) > 2)

    def _generate_reason(
        self, category: str, matched_keywords: List[str], score: float
    ) -> str:
        """Generate a human-readable reason for the classification."""
        if not matched_keywords:
            return f"Classified as {category} - no specific keywords found"

        if len(matched_keywords) == 1:
            return f"Classified as {category} based on keyword: '{matched_keywords[0]}'"

        # Show top 3 keywords
        top_keywords = matched_keywords[:3]
        if len(matched_keywords) > 3:
            return f"Classified as {category} based on keywords: {', '.join(top_keywords)} (and {len(matched_keywords) - 3} more)"
        else:
            return f"Classified as {category} based on keywords: {', '.join(top_keywords)}"


if __name__ == "__main__":
    # Test/demo mode
    print("Nutritionally Adequate Classifier - Test Mode")
    print("=" * 70)

    classifier = NutritionallyAdequateClassifier()

    # Test cases
    test_cases = [
        {
            "name": "Complete and Balanced (Yes)",
            "details": "This product is formulated to meet AAFCO Dog Food Nutrient Profiles for maintenance of adult dogs. Complete and balanced nutrition.",
            "more_details": None,
            "specifications": None,
            "feeding_instructions": None,
            "transition_instructions": None,
        },
        {
            "name": "Not Complete (No)",
            "details": "This product is intended for intermittent or supplemental feeding only.",
            "more_details": "Not a complete and balanced diet. Feed as a topper only.",
            "specifications": None,
            "feeding_instructions": None,
            "transition_instructions": None,
        },
        {
            "name": "No Information (Other)",
            "details": "Premium dog food with natural ingredients.",
            "more_details": None,
            "specifications": None,
            "feeding_instructions": None,
            "transition_instructions": None,
        },
    ]

    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Details: {test_case['details']}")
        result = classifier.classify(
            details=test_case["details"],
            more_details=test_case["more_details"],
            specifications=test_case["specifications"],
            feeding_instructions=test_case["feeding_instructions"],
            transition_instructions=test_case["transition_instructions"],
        )
        print(f"Result: {result.nutritionally_adequate}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Reason: {result.reason}")
        if result.matched_keywords:
            print(f"Matched Keywords: {', '.join(result.matched_keywords[:5])}")

    print("\n" + "=" * 70)
