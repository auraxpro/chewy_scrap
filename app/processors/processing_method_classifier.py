"""
Processing Method Classifier for Dog Food Products.

This module classifies dog food products into processing method categories based on
keyword matching across multiple product fields with support for composite methods
and negation handling.

Processing Methods:
- Uncooked (Not Frozen)
- Uncooked (Flash Frozen)
- Uncooked (Frozen)
- Lightly Cooked (Not Frozen)
- Lightly Cooked (Frozen)
- Freeze Dried
- Air Dried
- Dehydrated
- Baked
- Extruded
- Retorted

Strategy:
1. Multi-field text analysis with source trust ranking
2. Keyword matching with main and supporting keywords
3. Negation detection and penalty scoring
4. Composite method detection (e.g., Lightly Cooked + Frozen)
5. Disambiguation rules for conflicting methods
6. Confidence scoring and reasoning
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class ProcessingMethod(str, Enum):
    """Processing method classifications."""

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


@dataclass
class ProcessingKeywords:
    """Keywords for a specific processing method."""

    main: List[str]
    supporting: List[str]


# Keyword definitions for each processing method
PROCESSING_KEYWORDS: Dict[ProcessingMethod, ProcessingKeywords] = {
    ProcessingMethod.UNCOOKED_NOT_FROZEN: ProcessingKeywords(
        main=["raw", "not frozen"],
        supporting=[
            "raw",
            "not frozen",
            "refrigerated",
            "ready to serve",
            "fridge fresh",
            "gently handled",
            "prepared daily",
            "fridge-stored",
            "raw and fresh",
            "delivered fresh",
            "no freezing",
            "never frozen",
            "fresh never frozen",
            "uncooked",
            "fridge-kept",
            "stored in fridge",
            "raw refrigerated",
            "uncooked and unfrozen",
            "raw ready-to-eat",
            "raw kept cold not frozen",
            "fresh raw blend",
            "raw uncooked blend",
            "raw not frozen formula",
            "raw not frozen patties",
            "raw not frozen nuggets",
            "raw meal no freezing",
            "cold but not frozen",
            "raw no freeze preservation",
            "raw minimal processing",
            "raw kept in refrigerator",
        ],
    ),
    ProcessingMethod.UNCOOKED_FLASH_FROZEN: ProcessingKeywords(
        main=["raw", "flash frozen"],
        supporting=[
            "raw flash frozen",
            "instantly frozen",
            "preserved raw",
            "rapid frozen",
            "IQF raw",
            "flash frozen",
            "flash freeze",
            "flash-frozen raw",
            "rapidly frozen",
            "frozen immediately",
            "preserved by flash freezing",
            "ultra-cold frozen",
            "raw frozen fast",
            "instant frozen",
            "fresh then flash frozen",
            "flash frozen patties",
            "flash frozen nuggets",
            "flash frozen raw blend",
            "flash frozen formula",
            "raw quick frozen",
            "flash frozen meals",
            "nitrogen frozen",
            "raw sealed and flash frozen",
            "raw fast frozen preservation",
            "raw deep frozen",
            "flash freeze preserved",
        ],
    ),
    ProcessingMethod.UNCOOKED_FROZEN: ProcessingKeywords(
        main=["raw", "frozen"],
        supporting=[
            "frozen",
            "deep frozen",
            "freeze to preserve",
            "frozen chubs",
            "frozen dog food",
            "frozen form",
            "frozen meals",
            "frozen nuggets",
            "frozen packaging",
            "frozen patties",
            "frozen raw",
            "frozen recipe",
            "kept frozen",
            "raw frozen",
            "ships frozen",
            "store frozen",
            "human-grade raw meals",
            "uncooked",
            "not cooked",
            "raw frozen dog food",
            "raw kept frozen",
            "stored frozen",
            "frozen patties",
            "raw frozen blend",
            "raw frozen meal",
            "raw and frozen",
            "frozen meat mix",
            "frozen formula",
            "frozen fresh raw",
            "stay frozen",
            "raw in freezer",
            "freezer-stored raw",
            "frozen raw mix",
            "raw frozen medallions",
            "frozen whole prey",
            "frozen bones and meat",
        ],
    ),
    ProcessingMethod.LIGHTLY_COOKED_NOT_FROZEN: ProcessingKeywords(
        main=["fresh food", "lightly cooked", "not frozen"],
        supporting=[
            "fresh food",
            "lightly cooked",
            "gently cooked",
            "gently prepared",
            "slow cooked",
            "sous vide",
            "flash cooked",
            "lightly steamed",
            "partially cooked",
            "gently blanched",
            "keep refrigerated",
            "fresh never frozen",
            "refrigerated",
            "ready to serve",
            "fridge fresh",
            "fridge-stored",
            "delivered fresh",
            "no freezing",
            "minimally cooked",
            "small batch cooked",
            "cooked fresh",
            "home cooked",
            "just cooked",
            "prepared fresh",
            "cooked meals",
            "fridge cooked meals",
            "cooked not frozen",
            "ready-to-serve cooked",
            "fridge-ready meals",
            "lightly simmered",
            "cooked and refrigerated",
            "real cooked food",
            "cooked daily",
            "heat-prepared meals",
        ],
    ),
    ProcessingMethod.LIGHTLY_COOKED_FROZEN: ProcessingKeywords(
        main=["fresh food", "lightly cooked", "frozen"],
        supporting=[
            "fresh food",
            "frozen lightly cooked",
            "lightly cooked",
            "gently cooked",
            "gently prepared",
            "slow cooked",
            "sous vide",
            "flash cooked",
            "lightly steamed",
            "partially cooked",
            "gently blanched",
            "fresh-frozen",
            "frozen fresh",
            "kept frozen",
            "ships frozen",
            "frozen meals",
            "cooked then frozen",
            "cooked and frozen",
            "frozen cooked meals",
            "frozen gently prepared",
            "small batch cooked and frozen",
            "frozen dog entrees",
            "frozen fresh-cooked",
            "cooked frozen food",
            "frozen homemade meals",
            "cooked frozen recipes",
            "slow-cooked and frozen",
            "minimally cooked and frozen",
            "thaw before serving",
        ],
    ),
    ProcessingMethod.FREEZE_DRIED: ProcessingKeywords(
        main=["freeze dried"],
        supporting=[
            "freeze dried",
            "freeze dried nuggets",
            "primal freeze dried",
            "freeze-dried",
            "freeze-dried nuggets",
            "freeze-dried raw",
            "freeze-dried meal",
            "freeze-dried patties",
            "freeze-dried bites",
            "freeze-dried toppers",
            "freeze-dried formula",
            "freeze-dried dog food",
            "freeze-dried treats",
            "freeze-dried beef",
            "freeze-dried chicken",
            "freeze-dried nuggets for dogs",
            "freeze-dried complete meal",
            "freeze-dried whole food",
            "raw freeze-dried",
            "shelf-stable raw",
            "raw preserved through freeze drying",
            "primal nuggets",
            "freeze-dried complete and balanced",
            "freeze-dried blend",
            "freeze-dried entrée",
            "freeze-dried lamb formula",
            "freeze-dried raw diet",
            "shelf-stable freeze-dried",
        ],
    ),
    ProcessingMethod.AIR_DRIED: ProcessingKeywords(
        main=["air dried"],
        supporting=[
            "air dried",
            "cold dried",
            "air-dried raw",
            "gently air dried",
            "sun dried",
            "wind dried",
            "low-temperature dried",
            "gently dried",
            "slow dried",
            "cold-air dried",
            "fresh dried",
            "slow air dried",
            "air dried nuggets",
            "air dried bites",
            "air dried recipes",
            "low heat dried",
            "nutrient-rich air dried",
            "air dehydrated",
            "handcrafted air dried",
            "natural air dried",
            "artisan air dried",
            "air-dried food",
            "air dried patties",
        ],
    ),
    ProcessingMethod.DEHYDRATED: ProcessingKeywords(
        main=["dehydrated"],
        supporting=[
            "dehydrated",
            "gently dehydrated",
            "slow dehydrated",
            "dried raw",
            "raw dehydrated",
            "dehydrated dog food",
            "dehydrated meals",
            "dehydrated patties",
            "dehydrated recipes",
            "rehydrate with water",
            "dry mix formula",
            "add water to serve",
            "warm water preparation",
            "shelf-stable dehydrated",
            "dry pre-mix",
            "dehydrated whole foods",
            "dehydrated base mix",
        ],
    ),
    ProcessingMethod.BAKED: ProcessingKeywords(
        main=["baked"],
        supporting=[
            "baked",
            "oven baked",
            "gently baked",
            "slow baked",
            "low-temp baked",
            "baked kibble",
            "oven roasted",
            "handcrafted baked",
            "artisan baked",
            "small batch baked",
            "baked dry food",
            "air baked",
            "dry baked",
            "baked recipe",
            "baked formula",
            "crunchy bites",
            "dry oven-cooked",
            "lightly baked",
            "oven-baked dog food",
            "baked in small batches",
            "slow-cooked in oven",
            "crunchy baked bites",
        ],
    ),
    ProcessingMethod.EXTRUDED: ProcessingKeywords(
        main=["extruded"],
        supporting=[
            "extruded",
            "traditional kibble",
            "cold-pressed kibble",
            "pellet kibble",
            "crunchy kibble",
            "high heat processed",
            "standard kibble",
            "oven-extruded",
            "expanded kibble",
            "steam extruded",
            "heat extruded",
            "high-temp kibble",
            "processed kibble",
            "machine-processed kibble",
            "dry expanded pet food",
            "typical kibble",
            "mass-produced kibble",
            "kibble",
            "dry food",
            "dry kibble",
            "crunchy bites",
            "dry formula",
            "premium dry",
            "grain-free kibble",
            "extruded kibble",
            "high-pressure extrusion",
            "extruded dry food",
            "puffed kibble",
            "commercial kibble",
            "hot extruded",
            "dry extruded",
            "extruded pet food",
        ],
    ),
    ProcessingMethod.RETORTED: ProcessingKeywords(
        main=["retorted", "wet food"],
        supporting=[
            "canned food",
            "high heat sterilized",
            "shelf-stable wet",
            "thermally processed",
            "pressure cooked",
            "canned",
            "wet food",
            "slow-cooked in gravy",
            "shelf-stable pouch",
            "stew-like consistency",
            "gently cooked and sealed",
            "cooked in the can",
            "retort pouch",
            "cooked for safety",
            "moisture rich food",
            "moist food",
            "stewed",
            "loaf",
            "pate",
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
            "retort processed",
            "canned dog food",
            "wet food in can",
            "sealed can",
            "cooked in can",
            "moist food in can",
        ],
    ),
}

# Negation words
NEGATION_WORDS = [
    "no",
    "not",
    "never",
    "without",
    "free of",
    "doesn't",
    "isn't",
    "aren't",
    "non",
    "un",
]


@dataclass
class ProcessingClassificationResult:
    """Result of processing method classification."""

    processing_method_1: ProcessingMethod
    processing_method_2: Optional[ProcessingMethod]
    confidence: float  # 0.0 to 1.0
    matched_keywords_1: List[str]
    matched_keywords_2: List[str]
    reason: str


class ProcessingMethodClassifier:
    """
    Classifier for determining processing methods based on keyword matching.

    Uses a weighted scoring system with:
    - Main keyword match: +5 points
    - Supporting keyword match: +2 points
    - Negated main keyword: -3 points
    - Negated supporting keyword: -1 point

    Supports composite methods:
    - Uncooked (Not Frozen/Flash Frozen/Frozen)
    - Lightly Cooked (Not Frozen/Frozen)

    Applies disambiguation rules for conflicting methods.
    """

    def __init__(self):
        """Initialize the classifier."""
        self.keywords = PROCESSING_KEYWORDS
        self.negation_words = NEGATION_WORDS

    def classify(
        self,
        product_name: Optional[str] = None,
        details: Optional[str] = None,
        more_details: Optional[str] = None,
        ingredients: Optional[str] = None,
        specifications: Optional[str] = None,
        feeding_instructions: Optional[str] = None,
    ) -> ProcessingClassificationResult:
        """
        Classify a product into processing method categories.

        Args:
            product_name: Product name
            details: Product details/description
            more_details: Additional product details
            ingredients: Product ingredient list
            specifications: Product specifications
            feeding_instructions: Feeding instructions

        Returns:
            ProcessingClassificationResult with methods, confidence, and reasoning
        """
        # Combine all text fields
        combined_text = self._combine_text(
            product_name,
            details,
            more_details,
            ingredients,
            specifications,
            feeding_instructions,
        )

        if not combined_text:
            return ProcessingClassificationResult(
                processing_method_1=ProcessingMethod.OTHER,
                processing_method_2=None,
                confidence=1.0,
                matched_keywords_1=[],
                matched_keywords_2=[],
                reason="No text available for classification",
            )

        # Normalize text
        normalized_text = self._normalize_text(combined_text)

        # Calculate scores for all methods
        scores = {}
        matched_keywords_by_method = {}

        for method, keywords in self.keywords.items():
            score, matches = self._calculate_score(normalized_text, keywords, method)
            scores[method] = score
            matched_keywords_by_method[method] = matches

        # Get best match
        best_method, best_score = self._get_best_method(scores)

        # Check minimum threshold
        if best_score < 3 and not self._has_main_keyword_match(
            matched_keywords_by_method[best_method]
        ):
            return ProcessingClassificationResult(
                processing_method_1=ProcessingMethod.OTHER,
                processing_method_2=None,
                confidence=0.8,
                matched_keywords_1=[],
                matched_keywords_2=[],
                reason="No processing method keywords detected with sufficient confidence",
            )

        # Apply disambiguation rules
        best_method = self._apply_disambiguation_rules(
            best_method, scores, matched_keywords_by_method, normalized_text
        )

        # Check for composite methods
        second_method = self._detect_composite_method(
            best_method, scores, matched_keywords_by_method
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            best_score, matched_keywords_by_method[best_method]
        )

        # Generate reason
        reason = self._generate_reason(
            best_method,
            second_method,
            matched_keywords_by_method[best_method],
            matched_keywords_by_method.get(second_method, []) if second_method else [],
            confidence,
        )

        return ProcessingClassificationResult(
            processing_method_1=best_method,
            processing_method_2=second_method,
            confidence=confidence,
            matched_keywords_1=matched_keywords_by_method[best_method],
            matched_keywords_2=matched_keywords_by_method.get(second_method, [])
            if second_method
            else [],
            reason=reason,
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

    def _is_negated(self, text: str, keyword: str, keyword_pos: int) -> bool:
        """Check if a keyword is negated by looking at preceding words."""
        # Get text before keyword
        before_text = text[:keyword_pos].strip()
        words_before = before_text.split()

        # Check last 4 words for negation
        check_words = words_before[-4:] if len(words_before) >= 4 else words_before

        for word in check_words:
            for negation in self.negation_words:
                if negation in word:
                    return True

        return False

    def _calculate_score(
        self, text: str, keywords: ProcessingKeywords, method: ProcessingMethod
    ) -> Tuple[float, List[str]]:
        """
        Calculate confidence score for a method with negation handling.

        Scoring:
        - Main keyword match: +5 points
        - Supporting keyword match: +2 points
        - Negated main keyword: -3 points
        - Negated supporting keyword: -1 point

        Returns:
            (score, matched_keywords)
        """
        score = 0.0
        matched = []

        # Check main keywords
        for main_keyword in keywords.main:
            main_normalized = self._normalize_text(main_keyword)

            # Multi-word phrase
            if len(main_normalized.split()) > 1:
                if main_normalized in text:
                    pos = text.find(main_normalized)
                    if self._is_negated(text, main_normalized, pos):
                        score -= 3
                        matched.append(f"{main_keyword} (negated)")
                    else:
                        score += 5
                        matched.append(main_keyword)
            else:
                # Single word - check with word boundaries
                pattern = r"\b" + re.escape(main_normalized) + r"\b"
                match = re.search(pattern, text)
                if match:
                    if self._is_negated(text, main_normalized, match.start()):
                        score -= 3
                        matched.append(f"{main_keyword} (negated)")
                    else:
                        score += 5
                        matched.append(main_keyword)

        # Check supporting keywords
        for support_keyword in keywords.supporting:
            support_normalized = self._normalize_text(support_keyword)

            # Multi-word phrase
            if len(support_normalized.split()) > 1:
                if support_normalized in text:
                    pos = text.find(support_normalized)
                    if self._is_negated(text, support_normalized, pos):
                        score -= 1
                        matched.append(f"{support_keyword} (negated)")
                    else:
                        score += 2
                        matched.append(support_keyword)
            else:
                # Single word
                pattern = r"\b" + re.escape(support_normalized) + r"\b"
                match = re.search(pattern, text)
                if match:
                    if self._is_negated(text, support_normalized, match.start()):
                        score -= 1
                        matched.append(f"{support_keyword} (negated)")
                    else:
                        score += 2
                        matched.append(support_keyword)

        return score, matched

    def _get_best_method(
        self, scores: Dict[ProcessingMethod, float]
    ) -> Tuple[ProcessingMethod, float]:
        """Get the method with the highest score."""
        best_method = max(scores, key=scores.get)
        best_score = scores[best_method]
        return best_method, best_score

    def _has_main_keyword_match(self, matched_keywords: List[str]) -> bool:
        """Check if there's at least one non-negated main keyword match."""
        # Main keywords are indicated by higher scores
        # Check if we have any matches that aren't negated
        for kw in matched_keywords:
            if "(negated)" not in kw:
                return True
        return False

    def _apply_disambiguation_rules(
        self,
        method: ProcessingMethod,
        scores: Dict[ProcessingMethod, float],
        matched_keywords: Dict[ProcessingMethod, List[str]],
        text: str,
    ) -> ProcessingMethod:
        """Apply disambiguation rules for conflicting methods."""

        # Rule 1: Extruded vs Baked
        if method == ProcessingMethod.BAKED and scores.get(
            ProcessingMethod.EXTRUDED, 0
        ) >= scores.get(ProcessingMethod.BAKED, 0):
            # Check for oven-baked or gently baked as main keywords
            baked_keywords = matched_keywords.get(ProcessingMethod.BAKED, [])
            has_oven_baked = any(
                "oven baked" in kw.lower() or "gently baked" in kw.lower()
                for kw in baked_keywords
                if "(negated)" not in kw
            )
            if not has_oven_baked and "extruded" not in text:
                return ProcessingMethod.EXTRUDED

        # Rule 2: Retorted indicators
        retorted_indicators = [
            "canned",
            "in gravy",
            "pate",
            "retort pouch",
            "sterilized",
        ]
        if any(indicator in text for indicator in retorted_indicators):
            if scores.get(ProcessingMethod.RETORTED, 0) >= 3:
                return ProcessingMethod.RETORTED

        # Rule 3: Freeze Dried vs Frozen
        if (
            method == ProcessingMethod.UNCOOKED_FROZEN
            and scores.get(ProcessingMethod.FREEZE_DRIED, 0) > 0
        ):
            freeze_dried_keywords = matched_keywords.get(
                ProcessingMethod.FREEZE_DRIED, []
            )
            has_freeze_dried_main = any(
                "freeze dried" in kw.lower() or "freeze-dried" in kw.lower()
                for kw in freeze_dried_keywords
                if "(negated)" not in kw
            )
            keep_frozen_indicators = [
                "keep frozen",
                "thaw before serving",
                "store frozen",
            ]
            has_keep_frozen = any(
                indicator in text for indicator in keep_frozen_indicators
            )

            if has_freeze_dried_main and not has_keep_frozen:
                return ProcessingMethod.FREEZE_DRIED

        # Rule 4: Air Dried vs Dehydrated
        if method == ProcessingMethod.DEHYDRATED and scores.get(
            ProcessingMethod.AIR_DRIED, 0
        ) >= scores.get(ProcessingMethod.DEHYDRATED, 0):
            air_dried_keywords = matched_keywords.get(ProcessingMethod.AIR_DRIED, [])
            has_air_dried_main = any(
                "air dried" in kw.lower()
                for kw in air_dried_keywords
                if "(negated)" not in kw
            )
            if has_air_dried_main:
                return ProcessingMethod.AIR_DRIED

        # Rule 5: Uncooked vs Lightly Cooked
        if method == ProcessingMethod.UNCOOKED_NOT_FROZEN:
            heat_verbs = ["gently cooked", "sous vide", "lightly cooked", "cooked"]
            has_heat_verb = any(verb in text for verb in heat_verbs)
            if (
                has_heat_verb
                and scores.get(ProcessingMethod.LIGHTLY_COOKED_NOT_FROZEN, 0) >= 3
            ):
                return ProcessingMethod.LIGHTLY_COOKED_NOT_FROZEN

        return method

    def _detect_composite_method(
        self,
        primary_method: ProcessingMethod,
        scores: Dict[ProcessingMethod, float],
        matched_keywords: Dict[ProcessingMethod, List[str]],
    ) -> Optional[ProcessingMethod]:
        """Detect if a composite method (two-step processing) is present."""

        # Terminal processes cannot be composite
        terminal_methods = [
            ProcessingMethod.FREEZE_DRIED,
            ProcessingMethod.AIR_DRIED,
            ProcessingMethod.DEHYDRATED,
            ProcessingMethod.BAKED,
            ProcessingMethod.EXTRUDED,
            ProcessingMethod.RETORTED,
        ]

        if primary_method in terminal_methods:
            return None

        # Check for Uncooked + Frozen variants
        if primary_method in [
            ProcessingMethod.UNCOOKED_NOT_FROZEN,
            ProcessingMethod.UNCOOKED_FROZEN,
            ProcessingMethod.UNCOOKED_FLASH_FROZEN,
        ]:
            # Check for flash frozen
            if scores.get(ProcessingMethod.UNCOOKED_FLASH_FROZEN, 0) >= 3:
                if primary_method != ProcessingMethod.UNCOOKED_FLASH_FROZEN:
                    return ProcessingMethod.UNCOOKED_FLASH_FROZEN
            # Check for frozen
            elif scores.get(ProcessingMethod.UNCOOKED_FROZEN, 0) >= 3:
                if primary_method != ProcessingMethod.UNCOOKED_FROZEN:
                    return ProcessingMethod.UNCOOKED_FROZEN

        # Check for Lightly Cooked + Frozen
        if primary_method in [
            ProcessingMethod.LIGHTLY_COOKED_NOT_FROZEN,
            ProcessingMethod.LIGHTLY_COOKED_FROZEN,
        ]:
            if scores.get(ProcessingMethod.LIGHTLY_COOKED_FROZEN, 0) >= 3:
                if primary_method != ProcessingMethod.LIGHTLY_COOKED_FROZEN:
                    return ProcessingMethod.LIGHTLY_COOKED_FROZEN

        return None

    def _calculate_confidence(self, score: float, matched_keywords: List[str]) -> float:
        """Calculate confidence based on score and matches."""
        # Remove negated keywords from count
        non_negated = [kw for kw in matched_keywords if "(negated)" not in kw]

        if score >= 10 and len(non_negated) >= 3:
            return 1.0
        elif score >= 7 and len(non_negated) >= 2:
            return 0.9
        elif score >= 5 and len(non_negated) >= 2:
            return 0.8
        elif score >= 3 and len(non_negated) >= 1:
            return 0.7
        elif score >= 3:
            return 0.6
        else:
            return 0.5

    def _generate_reason(
        self,
        method1: ProcessingMethod,
        method2: Optional[ProcessingMethod],
        keywords1: List[str],
        keywords2: List[str],
        confidence: float,
    ) -> str:
        """Generate human-readable reason for classification."""
        # Filter out negated keywords for display
        keywords1_display = [kw for kw in keywords1 if "(negated)" not in kw]
        keywords2_display = [kw for kw in keywords2 if "(negated)" not in kw]

        if not keywords1_display:
            return f"Classified as '{method1.value}' with low confidence"

        confidence_level = (
            "high" if confidence >= 0.8 else "medium" if confidence >= 0.6 else "low"
        )

        # Primary method
        top_keywords1 = keywords1_display[:3]
        keywords_str = ", ".join(f"'{kw}'" for kw in top_keywords1)
        if len(keywords1_display) > 3:
            keywords_str += f" (and {len(keywords1_display) - 3} more)"

        reason = (
            f"Classified as '{method1.value}' with {confidence_level} confidence "
            f"based on keywords: {keywords_str}"
        )

        # Add secondary method if present
        if method2 and keywords2_display:
            top_keywords2 = keywords2_display[:2]
            keywords_str2 = ", ".join(f"'{kw}'" for kw in top_keywords2)
            reason += f". Secondary method '{method2.value}' detected: {keywords_str2}"

        return reason

    def classify_batch(
        self, products: List[Dict[str, Optional[str]]]
    ) -> List[ProcessingClassificationResult]:
        """
        Classify multiple products at once.

        Args:
            products: List of dicts with keys: product_name, details, more_details,
                     ingredients, specifications, feeding_instructions

        Returns:
            List of ProcessingClassificationResult objects
        """
        results = []
        for product in products:
            result = self.classify(
                product_name=product.get("product_name"),
                details=product.get("details"),
                more_details=product.get("more_details"),
                ingredients=product.get("ingredients"),
                specifications=product.get("specifications"),
                feeding_instructions=product.get("feeding_instructions"),
            )
            results.append(result)
        return results


# Convenience function for quick classification
def classify_processing_method(
    product_name: Optional[str] = None,
    details: Optional[str] = None,
    more_details: Optional[str] = None,
    ingredients: Optional[str] = None,
    specifications: Optional[str] = None,
    feeding_instructions: Optional[str] = None,
) -> ProcessingClassificationResult:
    """
    Quick classification function.

    Args:
        product_name: Product name
        details: Product details/description
        more_details: Additional product details
        ingredients: Product ingredient list
        specifications: Product specifications
        feeding_instructions: Feeding instructions

    Returns:
        ProcessingClassificationResult

    Example:
        >>> result = classify_processing_method(
        ...     product_name="Freeze-Dried Raw Chicken Recipe",
        ...     specifications="Freeze-dried for shelf stability"
        ... )
        >>> print(result.processing_method_1)  # ProcessingMethod.FREEZE_DRIED
        >>> print(result.confidence)  # 1.0
    """
    classifier = ProcessingMethodClassifier()
    return classifier.classify(
        product_name,
        details,
        more_details,
        ingredients,
        specifications,
        feeding_instructions,
    )


if __name__ == "__main__":
    # Example usage and testing
    print("=" * 70)
    print("PROCESSING METHOD CLASSIFIER - TEST EXAMPLES")
    print("=" * 70)

    test_cases = [
        {
            "name": "Freeze Dried Product",
            "product_name": "Primal Freeze-Dried Chicken Formula",
            "specifications": "Freeze-dried raw nuggets, shelf-stable",
            "details": "Complete freeze-dried raw dog food",
        },
        {
            "name": "Raw Frozen Product",
            "product_name": "Raw Frozen Beef Patties",
            "specifications": "Keep frozen, raw frozen dog food",
            "details": "Frozen raw meals for dogs",
        },
        {
            "name": "Lightly Cooked Fresh Product",
            "product_name": "Gently Cooked Fresh Meals",
            "specifications": "Lightly cooked, never frozen, refrigerated",
            "details": "Fresh cooked dog food, keep refrigerated",
        },
        {
            "name": "Extruded Kibble",
            "product_name": "Premium Dry Kibble",
            "specifications": "Traditional kibble, dry food",
            "details": "Extruded dry dog food",
        },
        {
            "name": "Canned Wet Food",
            "product_name": "Classic Canned Dog Food",
            "specifications": "Wet food in gravy, shelf-stable",
            "details": "Chunks in gravy, pate style",
        },
        {
            "name": "Air Dried Product",
            "product_name": "Air Dried Beef Recipe",
            "specifications": "Gently air dried, cold air dried",
            "details": "Slowly air dried dog food",
        },
        {
            "name": "Baked Kibble",
            "product_name": "Oven Baked Dog Food",
            "specifications": "Oven baked, gently baked kibble",
            "details": "Baked in small batches",
        },
    ]

    classifier = ProcessingMethodClassifier()

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'─' * 70}")
        print(f"Name: {test['product_name']}")
        print(f"Specs: {test['specifications']}")
        print(f"Details: {test['details']}")

        result = classifier.classify(
            product_name=test["product_name"],
            specifications=test["specifications"],
            details=test["details"],
        )

        print(f"\n→ Primary Method: {result.processing_method_1.value}")
        if result.processing_method_2:
            print(f"→ Secondary Method: {result.processing_method_2.value}")
        print(f"→ Confidence: {result.confidence:.2f}")
        if result.matched_keywords_1:
            keywords_preview = ", ".join(result.matched_keywords_1[:3])
            if len(result.matched_keywords_1) > 3:
                keywords_preview += f" (+{len(result.matched_keywords_1) - 3} more)"
            print(f"→ Matched Keywords: {keywords_preview}")
        print(f"→ Reason: {result.reason}")

    print(f"\n{'=' * 70}")
    print("TESTS COMPLETE")
    print("=" * 70)
