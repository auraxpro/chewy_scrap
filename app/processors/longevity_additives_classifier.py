"""
Longevity Additives Classifier for Dog Food Products.

This module identifies longevity additives in ingredient lists by matching
keywords across four categories: Herbs, Botanicals, Probiotics, and Other Longevity Additives.

Strategy:
1. Split ingredients by comma
2. Normalize text
3. Identify longevity additives using main and support keywords
4. Return list of found additives and count
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class LongevityAdditivesResult:
    """Result of longevity additives classification."""

    longevity_additives: List[str]  # List of found additive ingredients
    longevity_additives_count: int  # Count of unique additives found


@dataclass
class CategoryKeywords:
    """Keywords for a specific longevity additive category."""

    main: List[str]
    supporting: List[str]


# Herbs Keywords
HERBS_KEYWORDS = CategoryKeywords(
    main=[
        "rosemary",
        "rosemary extract",
        "parsley",
        "parsley extract",
        "turmeric",
        "turmeric extract",
        "oregano",
        "oregano extract",
        "basil",
        "basil extract",
        "cilantro",
        "cilantro extract",
        "ginger",
        "ginger extract",
        "sage",
        "sage extract",
        "thyme",
        "thyme extract",
        "chamomile",
        "chamomile extract",
        "peppermint",
        "peppermint extract",
        "spearmint",
        "spearmint extract",
        "lemongrass",
        "lemongrass extract",
        "dandelion",
        "dandelion extract",
        "fennel",
        "fennel extract",
        "echinacea",
        "echinacea extract",
        "milk thistle",
        "milk thistle extract",
        "nettle",
        "nettle extract",
        "licorice root",
        "licorice root extract",
        "yucca",
        "yucca extract",
        "coriander",
        "coriander seed",
        "turmeric root",
        "dill",
        "dill seed",
        "dill extract",
        "marjoram",
        "marjoram extract",
        "savory",
        "savory extract",
        "lemon balm",
        "lemon balm extract",
        "motherwort",
        "motherwort extract",
        "hawthorn",
        "hawthorn berry",
        "hawthorn extract",
        "ashwagandha",
        "ashwagandha root",
        "ashwagandha extract",
    ],
    supporting=[
        "natural rosemary extract",
        "antioxidant rosemary extract",
        "organic rosemary",
        "organic rosemary extract",
        "fresh parsley",
        "organic parsley",
        "dried parsley",
        "natural parsley extract",
        "curcumin",
        "organic turmeric",
        "organic turmeric extract",
        "wild oregano",
        "organic oregano",
        "oregano oil",
        "natural oregano extract",
        "organic basil",
        "sweet basil",
        "basil leaf",
        "basil leaf extract",
        "fresh cilantro",
        "coriander leaf",
        "coriander extract",
        "natural cilantro extract",
        "fresh ginger",
        "dried ginger",
        "organic ginger",
        "natural ginger extract",
        "garden sage",
        "organic sage",
        "sage leaf extract",
        "fresh thyme",
        "thyme leaf",
        "natural thyme extract",
        "organic chamomile",
        "chamomile flower",
        "chamomile flower extract",
        "organic peppermint",
        "peppermint oil",
        "peppermint leaf extract",
        "organic spearmint",
        "spearmint oil",
        "spearmint leaf extract",
        "organic lemongrass",
        "lemongrass oil",
        "lemongrass leaf extract",
        "dandelion root",
        "dandelion leaf",
        "natural dandelion extract",
        "fennel seed",
        "fennel seed extract",
        "organic fennel extract",
        "organic echinacea",
        "echinacea purpurea",
        "echinacea purpurea extract",
        "organic milk thistle",
        "silymarin",
        "milk thistle seed extract",
        "organic nettle",
        "nettle leaf extract",
        "nettle root extract",
        "organic licorice root",
        "licorice root powder",
        "natural licorice extract",
        "yucca schidigera",
        "yucca powder",
        "yucca schidigera extract",
        "ground coriander seed",
        "organic coriander",
        "coriander leaf",
        "dried coriander",
        "curcuma longa",
        "turmeric powder",
        "dried oregano",
        "origanum vulgare",
        "sweet basil",
        "ocimum basilicum",
        "basil powder",
        "organic dill",
        "anethum graveolens",
        "dill weed",
        "dried dill seed",
        "foeniculum vulgare",
        "fennel powder",
        "organic thyme",
        "thymus vulgaris",
        "dried marjoram",
        "origanum majorana",
        "savory herb",
        "satureja hortensis",
        "parsley flakes",
        "petroselinum crispum",
        "peppermint leaves",
        "mentha piperita",
        "spearmint leaves",
        "mentha spicata",
        "salvia officinalis",
        "lemon balm powder",
        "melissa officinalis",
        "leonurus cardiaca",
        "crataegus monogyna",
        "withania somnifera",
        "winter cherry",
    ],
)

# Botanicals Keywords
BOTANICALS_KEYWORDS = CategoryKeywords(
    main=[
        "blueberry",
        "blueberry extract",
        "cranberry",
        "cranberry extract",
        "spinach",
        "spinach extract",
        "carrot",
        "carrot extract",
        "pumpkin",
        "pumpkin extract",
        "kelp",
        "kelp extract",
        "spirulina",
        "spirulina extract",
        "chlorella",
        "chlorella extract",
        "green tea",
        "green tea extract",
        "aloe vera",
        "aloe vera extract",
        "apple",
        "apple extract",
        "beet",
        "beet extract",
        "broccoli",
        "broccoli extract",
        "tomato",
        "tomato extract",
        "sweet potato",
        "sweet potato extract",
        "pomegranate",
        "pomegranate extract",
        "chicory root",
        "chicory root extract",
        "seaweed",
        "seaweed extract",
        "barley grass",
        "barley grass extract",
        "wheatgrass",
        "wheatgrass extract",
        "acai",
        "acai berry",
        "acai extract",
        "goji",
        "goji berry",
        "goji extract",
        "elderberry",
        "elderberry extract",
        "raspberry",
        "raspberry extract",
        "blackberry",
        "blackberry extract",
        "grape",
        "grape extract",
        "mango",
        "mango extract",
        "papaya",
        "papaya extract",
        "kale",
        "kale extract",
        "cucumber",
        "cucumber extract",
        "zucchini",
        "zucchini extract",
        "dandelion greens",
    ],
    supporting=[
        "wild blueberry",
        "organic blueberry",
        "blueberry powder",
        "natural blueberry extract",
        "organic cranberry",
        "dried cranberry",
        "cranberry powder",
        "cranberry juice powder",
        "natural cranberry extract",
        "organic spinach",
        "dried spinach",
        "spinach leaf powder",
        "natural spinach extract",
        "organic carrot",
        "dehydrated carrot",
        "carrot powder",
        "natural carrot extract",
        "organic pumpkin",
        "dried pumpkin",
        "pumpkin powder",
        "natural pumpkin extract",
        "ascophyllum nodosum",
        "brown kelp",
        "kelp meal",
        "kelp powder",
        "organic spirulina",
        "spirulina powder",
        "organic chlorella",
        "chlorella powder",
        "camellia sinensis",
        "matcha powder",
        "natural green tea extract",
        "aloe barbadensis",
        "aloe gel powder",
        "aloe vera juice powder",
        "organic apple",
        "dried apple",
        "apple pomace",
        "apple powder",
        "organic beet",
        "beetroot powder",
        "beet juice powder",
        "natural beet extract",
        "organic broccoli",
        "broccoli powder",
        "tomato pomace",
        "lycopene",
        "natural tomato extract",
        "organic sweet potato",
        "sweet potato flour",
        "sweet potato powder",
        "organic pomegranate",
        "pomegranate powder",
        "chicory inulin",
        "chicory fiber",
        "dried chicory root",
        "natural chicory extract",
        "dried seaweed",
        "kelp flakes",
        "seaweed powder",
        "hordeum vulgare",
        "barley grass powder",
        "triticum aestivum",
        "wheatgrass juice powder",
        "euterpe oleracea",
        "freeze-dried acai",
        "dried acai powder",
        "lycium barbarum",
        "goji powder",
        "sambucus nigra",
        "dried elderberry",
        "elderberry powder",
        "rubus idaeus",
        "raspberry powder",
        "rubus fruticosus",
        "blackberry powder",
        "vitis vinifera",
        "grape skin extract",
        "grape seed extract",
        "mangifera indica",
        "mango powder",
        "carica papaya",
        "papaya powder",
        "brassica oleracea var. sabellica",
        "kale powder",
        "cucumis sativus",
        "cucumber juice powder",
        "cucurbita pepo var. cylindrica",
        "zucchini powder",
        "taraxacum officinale",
        "dried dandelion leaf",
        "dandelion root powder",
    ],
)

# Probiotics Keywords
PROBIOTICS_KEYWORDS = CategoryKeywords(
    main=[
        "probiotics",
        "probiotic blend",
        "probiotic cultures",
        "live cultures",
        "lactobacillus acidophilus",
        "lactobacillus casei",
        "lactobacillus plantarum",
        "lactobacillus rhamnosus",
        "bifidobacterium bifidum",
        "bifidobacterium animalis",
        "bifidobacterium longum",
        "bacillus coagulans",
        "bacillus subtilis",
        "enterococcus faecium",
        "streptococcus thermophilus",
        "pediococcus acidilactici",
        "lactobacillus brevis",
        "lactobacillus fermentum",
        "bifidobacterium breve",
        "dried bacillus coagulans fermentation",
        "dried bacillus coagulans fermentation product",
    ],
    supporting=[
        "lactobacillus acidophilus fermentation product",
        "l. acidophilus",
        "lactobacillus casei fermentation product",
        "l. casei",
        "lactobacillus plantarum fermentation product",
        "l. plantarum",
        "lactobacillus rhamnosus fermentation product",
        "l. rhamnosus",
        "bifidobacterium bifidum fermentation product",
        "b. bifidum",
        "bifidobacterium animalis fermentation product",
        "b. animalis",
        "bifidobacterium longum fermentation product",
        "b. longum",
        "bacillus coagulans fermentation product",
        "b. coagulans",
        "bacillus subtilis fermentation product",
        "b. subtilis",
        "enterococcus faecium fermentation product",
        "e. faecium",
        "probiotic blend",
        "direct-fed microbials",
        "stabilized probiotics",
        "dried fermentation product",
        "freeze-dried probiotics",
        "microencapsulated probiotics",
        "streptococcus thermophilus fermentation product",
        "s. thermophilus",
        "pediococcus acidilactici fermentation product",
        "p. acidilactici",
        "lactobacillus brevis fermentation product",
        "l. brevis",
        "lactobacillus fermentum fermentation product",
        "l. fermentum",
        "bifidobacterium breve fermentation product",
        "b. breve",
        "shelf-stable probiotics",
        "viable probiotic culture",
        "probiotic consortium",
        "probiotic culture blend",
        "multi-strain probiotics",
    ],
)

# Other Longevity Additives Keywords
OTHER_LONGEVITY_KEYWORDS = CategoryKeywords(
    main=[
        "medicinal mushrooms",
        "functional mushrooms",
        "reishi mushroom",
        "shiitake mushroom",
        "maitake mushroom",
        "cordyceps mushroom",
        "turkey tail mushroom",
        "lion's mane mushroom",
        "chaga mushroom",
        "bee products",
        "bee pollen",
        "royal jelly",
        "colostrum",
        "green-lipped mussel",
        "green‑lipped mussel",  # Special dash variant
        "greenlipped mussel",  # Normalized variant (no hyphen)
        "glucosamine",
        "chondroitin sulfate",
        "msm",
        "astaxanthin",
        "curcumin",
        "resveratrol",
        "omega-3 fish oil",
        "krill oil",
        "algal dha",
        "camelina oil",
        "hemp seed",
        "chia seed",
        "sunflower seed",
        "black cumin seed",
        "quinoa",
        "amaranth",
        "coq10",
        "l-carnitine",
        "taurine",
    ],
    supporting=[
        "mushroom blend",
        "mushroom complex",
        "beta-glucans",
        "1,3/1,6-beta-glucans",
        "immune mushroom",
        "reishi extract",
        "ganoderma lucidum",
        "reishi powder",
        "shiitake extract",
        "lentinus edodes",
        "maitake extract",
        "grifola frondosa",
        "cordyceps militaris",
        "cordyceps sinensis",
        "turkey tail extract",
        "coriolus versicolor",
        "trametes versicolor",
        "lion's mane extract",
        "hericium erinaceus",
        "chaga extract",
        "inonotus obliquus",
        "bee superfoods",
        "dried bee pollen",
        "pollen granules",
        "royal jelly powder",
        "bovine colostrum",
        "colostrum powder",
        "igg-rich colostrum",
        "perna canaliculus",
        "green-lipped mussel powder",
        "green‑lipped mussel powder",  # Special dash variant
        "greenlipped mussel powder",  # Normalized variant (no hyphen)
        "glm powder",
        "mussel extract",
        "joint complex",
        "joint support",
        "glucosamine hcl",
        "glucosamine sulfate",
        "chondroitin",
        "chondroitin sulfate sodium",
        "msm (methylsulfonylmethane)",
        "sulfur donor",
        "cartilage support",
        "natural astaxanthin",
        "haematococcus pluvialis extract",
        "carotenoid antioxidant",
        "turmeric extract",
        "curcumin (95%)",
        "curcuminoids",
        "turmeric curcumin",
        "piperine-enhanced",
        "black pepper extract",
        "resveratrol (trans-resveratrol)",
        "polygonum cuspidatum extract",
        "japanese knotweed extract",
        "fish oil powder",
        "salmon oil",
        "sardine oil",
        "anchovy oil",
        "menhaden oil",
        "concentrated epa/dha",
        "triglyceride-form omega-3",
        "krill oil powder",
        "phospholipid omega-3",
        "algal oil",
        "dha algal oil",
        "schizochytrium sp.",
        "camelina sativa oil",
        "camelina meal",
        "ala source",
        "hempseed powder",
        "cold-pressed hemp",
        "chia seed powder",
        "milled chia",
        "sunflower seed meal",
        "black cumin (nigella sativa)",
        "nigella seed",
        "thymoquinone source",
        "quinoa flakes",
        "puffed quinoa",
        "amaranth flour",
        "coenzyme q10",
        "ubiquinone",
        "ubiquinol",
        "mitochondrial support",
        "l-carnitine tartrate",
        "acetyl-l-carnitine",
        "carnitine",
        "taurine supplement",
        "taurine additive",
        "heart support",
        "antioxidant complex",
        "longevity blend",
        "vitality blend",
        "superfood blend",
        "omega-3 fortification",
        "joint & hip formula",
        "mobility support",
        "immune support complex",
        "skin & coat support",
        "cognitive support",
        "senior vitality",
        "senior support",
        "longevity formula",
    ],
)


class LongevityAdditivesClassifier:
    """
    Classifier for identifying longevity additives in ingredient lists.
    """

    def __init__(self):
        """Initialize the classifier with keyword categories."""
        self.categories = {
            "herbs": HERBS_KEYWORDS,
            "botanicals": BOTANICALS_KEYWORDS,
            "probiotics": PROBIOTICS_KEYWORDS,
            "other": OTHER_LONGEVITY_KEYWORDS,
        }

    def classify(self, ingredients: Optional[str]) -> LongevityAdditivesResult:
        """
        Classify ingredients and identify longevity additives.

        Args:
            ingredients: Comma-separated ingredient list string

        Returns:
            LongevityAdditivesResult with found additives and count
        """
        # Handle empty input
        if not ingredients or not ingredients.strip():
            return LongevityAdditivesResult(
                longevity_additives=[], longevity_additives_count=0
            )

        # Split ingredients by comma
        ingredient_list = self._split_ingredients(ingredients)

        # Normalize each ingredient
        normalized_ingredients = [self._normalize_text(ing) for ing in ingredient_list]

        # Identify longevity additives
        found_additives = self._identify_longevity_additives(
            normalized_ingredients, ingredient_list
        )

        return LongevityAdditivesResult(
            longevity_additives=found_additives,
            longevity_additives_count=len(found_additives),
        )

    def _split_ingredients(self, ingredients: str) -> List[str]:
        """Split ingredients by comma."""
        # Split by comma and clean up
        parts = [p.strip() for p in ingredients.split(",")]
        # Filter out empty strings
        return [p for p in parts if p]

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

    def _identify_longevity_additives(
        self, normalized_ingredients: List[str], original_ingredients: List[str]
    ) -> List[str]:
        """
        Identify longevity additives by matching keywords.

        Args:
            normalized_ingredients: List of normalized ingredient strings
            original_ingredients: List of original ingredient strings

        Returns:
            List of found additive ingredients (original format)
        """
        found = []
        found_set = set()

        for normalized, original in zip(normalized_ingredients, original_ingredients):
            # Check each category
            for category_name, keywords in self.categories.items():
                # Check main keywords first
                for main_keyword in keywords.main:
                    main_normalized = self._normalize_text(main_keyword)
                    if self._text_contains_keyword(normalized, main_normalized):
                        if original not in found_set:
                            found.append(original)
                            found_set.add(original)

                # Check supporting keywords
                for support_keyword in keywords.supporting:
                    support_normalized = self._normalize_text(support_keyword)
                    if self._text_contains_keyword(normalized, support_normalized):
                        if original not in found_set:
                            found.append(original)
                            found_set.add(original)

        return found

    def _text_contains_keyword(self, text: str, keyword: str) -> bool:
        """Check if text contains keyword (with word boundaries for single words)."""
        # For multi-word keywords, check if phrase exists
        if len(keyword.split()) > 1:
            return keyword in text

        # For single words, use word boundaries
        pattern = r"\b" + re.escape(keyword) + r"\b"
        return bool(re.search(pattern, text))


# Convenience function
def classify_longevity_additives(
    ingredients: Optional[str],
) -> LongevityAdditivesResult:
    """
    Quick classification function.

    Args:
        ingredients: Comma-separated ingredient list

    Returns:
        LongevityAdditivesResult
    """
    classifier = LongevityAdditivesClassifier()
    return classifier.classify(ingredients)
