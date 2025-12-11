"""
Ingredient Quality Classifier for Dog Food Products.

This module classifies ingredients into categories (Protein, Fat, Carb, Fiber)
and assigns quality ratings (High, Good, Moderate, Low) based on keyword matching.

Strategy:
1. Split ingredients by comma
2. Normalize text
3. Identify category (Protein, Fat, Carb, Fiber) using keywords
4. Assign quality rating within each category
5. Identify Dirty Dozen ingredients
6. Identify Synthetic Nutrition additions
7. Count each category and determine overall quality class
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class QualityClass(str, Enum):
    """Quality classifications."""

    HIGH = "High"
    GOOD = "Good"
    MODERATE = "Moderate"
    LOW = "Low"
    OTHER = "Other"


class IngredientCategory(str, Enum):
    """Ingredient categories."""

    PROTEIN = "Protein"
    FAT = "Fat"
    CARB = "Carb"
    FIBER = "Fiber"
    OTHER = "Other"


@dataclass
class CategoryKeywords:
    """Keywords for a specific quality category."""

    main: List[str]
    supporting: List[str]


# Protein Quality Keywords
PROTEIN_KEYWORDS: Dict[QualityClass, CategoryKeywords] = {
    QualityClass.HIGH: CategoryKeywords(
        main=[
            "organic whole meat",
            "organic fresh meat",
            "organic raw meat",
            "organic human grade meat",
            "organic muscle meat",
            "organic organ meat",
            "organic named cuts",
            "pasture-raised organic chicken",
            "pasture-raised organic beef",
            "pasture-raised organic lamb",
            "grass-fed organic beef",
            "wild-caught organic salmon",
            "wild-caught organic fish",
            "grass-fed organic bison",
            "grass-fed organic venison",
            "wild-caught",
            "wild caught",
            "line caught",
        ],
        supporting=[
            "organic chicken",
            "organic turkey",
            "organic duck",
            "organic beef",
            "organic lamb",
            "organic pork",
            "organic venison",
            "organic bison",
            "organic rabbit",
            "organic whole chicken",
            "organic whole turkey",
            "organic whole duck",
            "organic whole beef",
            "organic fresh chicken",
            "organic fresh beef",
            "organic chicken breast",
            "organic chicken thigh",
            "organic turkey breast",
            "organic beef tenderloin",
            "organic liver",
            "organic kidney",
            "organic heart",
            "organic salmon",
            "organic organ meats",
            "organic pasture-raised chicken",
            "organic grass-fed beef",
            "organic free-range turkey",
            "USDA organic chicken",
            "USDA organic beef",
            "certified organic meat",
            "humanely raised organic meat",
        ],
    ),
    QualityClass.GOOD: CategoryKeywords(
        main=[
            "whole meat",
            "fresh meat",
            "raw meat",
            "human grade meat",
            "muscle meat",
            "organ meat",
            "named cuts",
            "pasture-raised chicken",
            "pasture-raised beef",
            "pasture-raised lamb",
            "grass-fed beef",
            "farm raised fish",
            "farm raised",
            "grass-fed bison",
            "grass-fed venison",
        ],
        supporting=[
            "chicken breast",
            "beef sirloin",
            "duck breast",
            "lamb shoulder",
            "turkey thigh",
            "salmon fillet",
            "whitefish fillet",
            "beef liver",
            "chicken liver",
            "turkey liver",
            "beef heart",
            "lamb heart",
            "rabbit",
            "quail",
            "goat",
            "whole sardines",
            "whole anchovies",
            "pasture-raised pork",
            "cage-free chicken",
            "hormone-free beef",
            "antibiotic-free turkey",
            "boneless chicken",
            "whole turkey",
            "single-source protein",
        ],
    ),
    QualityClass.MODERATE: CategoryKeywords(
        main=["whole meat", "meat", "raw meat", "muscle meat", "organ meat", "chicken", "beef", "lamb", "bison", "fish meat"],
        supporting=[
            "chicken",
            "turkey",
            "duck",
            "goose",
            "quail",
            "pheasant",
            "beef",
            "lamb",
            "pork",
            "goat",
            "venison",
            "bison",
            "rabbit",
            "salmon",
            "whitefish",
            "trout",
            "cod",
            "herring",
            "mackerel",
            "sardines",
            "tuna",
        ],
    ),
    QualityClass.LOW: CategoryKeywords(
        main=[
            "by-products",
            "meat meals",
            "animal digest",
            "rendered proteins",
            "unspecified animal parts",
            "plant based protein",
            "plant protein",
            "legume protein",
            "vegetable protein",
            "grain protein",
            "cereal protein",
            "pulse protein",
        ],
        supporting=[
            "meat by-products",
            "poultry by-products",
            "animal by-products",
            "chicken by-product meal",
            "beef by-product meal",
            "meat meal",
            "poultry meal",
            "chicken meal",
            "animal digest",
            "liver digest",
            "hydrolyzed animal tissue",
            "animal fat (unspecified)",
            "rendered meat",
            "rendered fat",
            "spray-dried digest",
            "bone meal",
            "feather meal",
            "meat and bone meal",
            "meals",
            "digests",
            "soy protein isolate",
            "soy protein concentrate",
            "corn gluten meal",
            "wheat gluten",
            "pea protein",
            "potato protein",
            "rice protein",
            "lentil protein",
            "chickpea protein",
            "plant protein concentrate",
            "pork liver",
            "chick fat",
            "pork fat",
            "lungs",
            "spleen",
            "kidney",
            "brain",
            "liver",
            "blood",
            "muscle",
            "tissue",
        ],
    ),
}

# Fat Quality Keywords
FAT_KEYWORDS: Dict[QualityClass, CategoryKeywords] = {
    QualityClass.HIGH: CategoryKeywords(
        main=["fish oil", "salmon oil", "krill oil", "duck fat"],
        supporting=[
            "chicken fat",
            "duck fat",
            "lamb fat",
            "turkey fat",
            "beef fat",
            "salmon oil",
            "fish oil",
            "krill oil",
            "anchovy oil",
            "sardine oil",
            "cod liver oil",
            "mackerel oil",
            "menhaden oil",
            "omega-3 rich oils",
            "marine oils",
            "naturally preserved fish oil",
        ],
    ),
    QualityClass.GOOD: CategoryKeywords(
        main=["flaxseed oil", "avocado oil", "plant oils", "olive oil"],
        supporting=[
            "avocado oil",
            "chia seed oil",
            "coconut oil",
            "flaxseed oil",
            "linseed oil",
            "chia seed oil",
            "coconut oil",
            "hemp seed oil",
            "safflower oil (high oleic)",
            "camelina oil",
            "flaxseed oil",
            "linseed oil",
            "chia seed oil",
            "coconut oil",
            "hemp seed oil",
            "safflower oil (high oleic)",
            "camelina oil",
            "olive oil",
        ],
    ),
    QualityClass.LOW: CategoryKeywords(
        main=[
            "seed oils",
            "low-quality fats",
            "by-product fats",
            "rendered fats",
            "recycled fats",
            "low-grade oils",
            "unspecified fats",
            "plant-based fats (unspecified)",
            "hydrogenated oils",
            "trans fats",
            "animal fat (unspecified)",
            "linoleic acid",
            "linoleic acid (omega 6 fatty acid)",
            "omega 6 fatty acid",
        ],
        supporting=[
            "sunflower oil (cold-pressed)",
            "safflower oil (cold-pressed)",
            "canola oil (cold-pressed)",
            "vegetable oil (named)",
            "seed oils",
            "plant-derived oils (named)",
            "animal fats (unspecified)",
            "sunflower oil",
            "canola oil",
            "vegetable oils",
            "soybean oil",
            "cottonseed oil",
            "corn oil",
            "palm oil",
            "palm kernel oil",
            "rapeseed oil",
            "generic plant oil",
            "hydrogenated vegetable oil",
            "partially hydrogenated oils",
            "lard (unspecified)",
            "animal fat (unspecified)",
            "poultry fat (unspecified)",
            "by-product fat",
            "rendered fat",
            "recycled restaurant grease",
            "yellow grease",
            "used cooking oil",
            "low-grade cooking oil",
            "beef fat (unspecified)",
            "sunflower oil (high oleic)",
            "canola oil",
            "rice bran oil",
            "sesame oil",
            "safflower oil",
            "sunflower oil",
            "grapeseed oil",
            "soybean oil",
            "cottonseed oil",
            "corn oil",
            "palm oil",
            "palm kernel oil",
            "rapeseed oil",
            "vegetable oil",
            "hydrogenated vegetable oil",
            "tallow (unspecified source)",
            "poultry fat (unspecified)",
            "meat fat (unspecified)",
        ],
    ),
}

# Carb Quality Keywords
CARB_KEYWORDS: Dict[QualityClass, CategoryKeywords] = {
    QualityClass.HIGH: CategoryKeywords(
        main=[
            "sweet potatoes",
            "pumpkin",
            "butternut squash",
            "lentils",
            "garbanzo beans",
            "green beans",
            "carrots",
            "parsnips",
            "beetroot",
            "peas",
        ],
        supporting=[
            "sweet potatoes",
            "pumpkin",
            "butternut squash",
            "lentils",
            "garbanzo beans",
            "green beans",
            "carrots",
            "parsnips",
            "beetroot",
            "peas",
        ],
    ),
    QualityClass.GOOD: CategoryKeywords(
        main=[
            "oats",
            "quinoa",
            "brown rice",
            "barley",
            "millet",
            "amaranth",
            "rye",
            "buckwheat",
            "sorghum",
            "teff",
            "quinoa",
            "chickpeas",
        ],
        supporting=[
            "oats",
            "quinoa",
            "brown rice",
            "barley",
            "millet",
            "amaranth",
            "rye",
            "buckwheat",
            "sorghum",
            "teff",
            "quinoa",
            "chickpeas",
            "whole grain oats",
        ],
    ),
    QualityClass.MODERATE: CategoryKeywords(
        main=[
            "white rice",
            "potatoes",
            "potato starch",
            "sweet potato flour",
            "rice flour",
            "tapioca",
            "cassava root",
            "arrowroot flour",
        ],
        supporting=[
            "white rice",
            "potatoes",
            "potato starch",
            "sweet potato flour",
            "rice flour",
            "tapioca",
            "cassava root",
            "arrowroot flour",
        ],
    ),
    QualityClass.LOW: CategoryKeywords(
        main=[
            "corn",
            "cornmeal",
            "corn gluten meal",
            "wheat",
            "wheat flour",
            "wheat gluten meal",
            "wheat middlings",
            "soy grits",
            "soy flour",
            "rice bran",
            "brewer's rice",
            "pearled barley",
            "middlings",
            "mill run",
            "cereal by-products",
            "wheat bran",
            "rice milling",
        ],
        supporting=[
            "corn",
            "cornmeal",
            "corn gluten meal",
            "wheat",
            "wheat flour",
            "wheat gluten meal",
            "wheat middlings",
            "soy grits",
            "soy flour",
            "rice bran",
            "brewer's rice",
            "pearled barley",
            "middlings",
            "mill run",
            "cereal by-products",
            "wheat bran",
            "rice milling",
            "alfalfa meal",
            "alfalfa meal",
            "dextrose",
        ],
    ),
}

# Fiber Quality Keywords
FIBER_KEYWORDS: Dict[QualityClass, CategoryKeywords] = {
    QualityClass.HIGH: CategoryKeywords(
        main=["pumpkin", "flaxseed", "chia seed", "psyllium husk", "beet greens", "kale", "spinach", "alfalfa", "carrots", "apples"],
        supporting=[
            "pumpkin",
            "flaxseed",
            "chia seed",
            "psyllium husk",
            "beet greens",
            "kale",
            "spinach",
            "alfalfa",
            "carrots",
            "apples",
        ],
    ),
    QualityClass.GOOD: CategoryKeywords(
        main=["beet pulp", "sweet potatoes", "peas", "lentils", "garbanzo beans", "tomato pomace", "carrot fiber"],
        supporting=[
            "beet pulp",
            "sweet potatoes",
            "peas",
            "lentils",
            "garbanzo beans",
            "tomato pomace",
            "carrot fiber",
            "fructooligosaccharides (FOS)",
        ],
    ),
    QualityClass.MODERATE: CategoryKeywords(
        main=["cellulose", "rice bran", "oat hulls", "peanut hulls", "wheat bran", "soy hulls", "tomato fiber", "pea fiber"],
        supporting=[
            "cellulose",
            "rice bran",
            "oat hulls",
            "peanut hulls",
            "wheat bran",
            "soy hulls",
            "tomato fiber",
            "pea fiber",
            "dried tomato pomace",
            "powdered cellulose",
        ],
    ),
    QualityClass.LOW: CategoryKeywords(
        main=[
            "soybean hulls",
            "corn fiber",
            "wheat fiber",
            "peanut skins",
            "hull fiber",
            "cottonseed hulls",
            "peanut shells",
            "grain hulls",
        ],
        supporting=[
            "soybean hulls",
            "corn fiber",
            "wheat fiber",
            "peanut skins",
            "hull fiber",
            "cottonseed hulls",
            "peanut shells",
            "grain hulls",
            "alfalfa meal",
        ],
    ),
}

# Dirty Dozen Keywords
DIRTY_DOZEN_KEYWORDS: Dict[str, CategoryKeywords] = {
    "BHA": CategoryKeywords(
        main=["BHA", "Butylated Hydroxyanisole", "BHA preservative"],
        supporting=[
            "BHA additive",
            "BHA chemical preservative",
            "artificial preservative BHA",
            "antioxidant BHA",
            "preservative butylated hydroxyanisole",
        ],
    ),
    "BHT": CategoryKeywords(
        main=["BHT", "Butylated Hydroxytoluene", "BHT preservative"],
        supporting=[
            "BHT additive",
            "BHT chemical preservative",
            "artificial preservative BHT",
            "antioxidant BHT",
            "preservative butylated hydroxytoluene",
        ],
    ),
    "Ethoxyquin": CategoryKeywords(
        main=["Ethoxyquin", "Ethoxyquin preservative"],
        supporting=[
            "preservative ethoxyquin",
            "antioxidant ethoxyquin",
            "chemical preservative ethoxyquin",
            "pet food preservative ethoxyquin",
            "synthetic antioxidant",
        ],
    ),
    "Propylene Glycol": CategoryKeywords(
        main=["Propylene Glycol", "Propylene Glycol preservative", "Propylene Glycol additive"],
        supporting=[
            "propylene glycol (humectant)",
            "moisture-retaining agent propylene glycol",
            "food additive propylene glycol",
            "pet food humectant",
            "synthetic humectant",
        ],
    ),
    "Artificial Colors": CategoryKeywords(
        main=["Artificial colors", "Artificial coloring", "Artificial dyes", "Synthetic colors", "FD&C colors", "Red 40", "Allura Red"],
        supporting=[
            "Red 40",
            "Allura Red",
            "Yellow 5",
            "Tartrazine",
            "Yellow 6",
            "Sunset Yellow",
            "Blue 1",
            "Brilliant Blue",
            "Blue 2",
            "Indigotine",
            "Green 3",
            "Fast Green FCF",
            "caramel coloring",
            "caramel color",
            "added color",
            "synthetic dyes",
            "color additives",
            "artificial food coloring",
        ],
    ),
    "Corn": CategoryKeywords(
        main=["Corn", "Ground corn", "Cornmeal", "Corn flour", "Corn gluten meal", "Whole grain corn"],
        supporting=[
            "yellow corn",
            "GMO corn",
            "maize",
            "corn bran",
            "corn grits",
            "cracked corn",
            "degermed corn meal",
            "corn starch",
        ],
    ),
    "Wheat": CategoryKeywords(
        main=["Wheat", "Wheat flour", "Whole grain wheat", "Wheat bran", "Wheat gluten meal", "Wheat middlings"],
        supporting=[
            "white flour",
            "GMO wheat",
            "wheat gluten",
            "wheat germ",
            "cracked wheat",
            "wheat starch",
            "durum wheat",
        ],
    ),
    "Soy": CategoryKeywords(
        main=["Soy", "Soybeans", "Soy protein", "Soy flour", "Soy meal", "Soy protein concentrate"],
        supporting=[
            "soy grits",
            "hydrolyzed soy protein",
            "soy isoflavones",
            "soy oil",
            "soybean hulls",
            "soy lecithin",
            "soy starch",
        ],
    ),
    "By-products": CategoryKeywords(
        main=["Animal by-products", "Poultry by-products", "Meat by-products", "By-product meal"],
        supporting=[
            "beaks",
            "feet",
            "necks",
            "rice bran",
            "brewer's yeast",
            "corn fiber",
            "by-product fats",
            "poultry by-product meal",
            "feathers",
            "meat meal",
            "chicken meal",
            "turkey meal",
            "beef meal",
            "lamb meal",
            "fish meal",
            "bone meal",
            "chicken by-product meal",
            "beef by-product meal",
            "organs (unspecified)",
            "rendered by-products",
            "meat meal (unspecified species)",
        ],
    ),
    "Animal Digest": CategoryKeywords(
        main=["Animal digest", "Meat digest", "Poultry digest", "Fish digest"],
        supporting=[
            "hydrolyzing",
            "hydrolyzed",
            "hydrolyzed animal tissue",
            "spray-dried digest",
            "digest of animal origin",
            "palatant",
            "liver digest",
            "flavoring digest",
            "animal protein digest",
        ],
    ),
    "Rendered Fat": CategoryKeywords(
        main=["Rendered fat", "Animal fat", "Poultry fat", "Beef fat"],
        supporting=[
            "meat fat (unspecified)",
            "beef fat (unspecified)",
            "poultry fat (unspecified)",
            "tallow",
            "lard",
            "chicken fat (rendered)",
            "turkey fat (rendered)",
            "mutton fat",
            "lamb fat (rendered)",
            "fish oil (rendered)",
            "pork fat",
        ],
    ),
    "Sugar": CategoryKeywords(
        main=["Sugar", "Corn syrup", "Cane sugar", "Beet sugar", "Brown sugar"],
        supporting=[
            "glucose",
            "fructose",
            "sucrose",
            "high fructose corn syrup",
            "HFCS",
            "xylitol",
            "dextrose",
            "molasses",
            "date sugar",
            "stevia",
            "maple syrup",
            "agave syrup",
            "rice syrup",
        ],
    ),
}

# Synthetic Nutrition Keywords
SYNTHETIC_NUTRITION_KEYWORDS: Dict[str, CategoryKeywords] = {
    "Synthetic Vitamins": CategoryKeywords(
        main=["Vitamins"],
        supporting=[
            "retinyl palmitate",
            "retinyl acetate",
            "vitamin A",
            "ascorbic acid",
            "sodium ascorbate",
            "vitamin C",
            "ergocalciferol",
            "cholecalciferol",
            "vitamin D",
            "dl-alpha-tocopherol",
            "dl-alpha-tocopheryl acetate",
            "vitamin E",
            "phytonadione",
            "menaquinone",
            "MK-7",
            "vitamin K",
            "thiamine mononitrate",
            "thiamine hydrochloride",
            "vitamin B1",
            "riboflavin",
            "vitamin B2",
            "niacinamide",
            "nicotinamide",
            "niacin",
            "vitamin B3",
            "calcium pantothenate",
            "pantothenic acid",
            "vitamin B5",
            "pyridoxine hydrochloride",
            "pyridoxine HCl",
            "vitamin B6",
            "biotin",
            "vitamin B7",
            "folic acid",
            "folate",
            "vitamin B9",
            "cyanocobalamin",
            "methylcobalamin",
            "vitamin B12",
            "choline chloride",
            "mixed tocopherols",
            "Vitamin E Supplement",
            "L-Ascorbyl-2-Polyphosphate",
            "Niacin Supplement",
            "Vitamin A Supplement",
            "Calcium Pantothenate",
            "Vitamin B12 Supplement",
            "Pyridoxine Hydrochloride",
            "Riboflavin Supplement",
            "Menadione Sodium Bisulfite Complex",
            "Vitamin D3 Supplement",
        ],
    ),
    "Synthetic Amino Acids": CategoryKeywords(
        main=["Amino Acids"],
        supporting=[
            "L-Lysine",
            "DL-Methionine",
            "L-Threonine",
            "L-Carnitine",
            "L-Tryptophan",
            "Choline Chloride",
            "Betaine",
        ],
    ),
    "Synthetic Minerals": CategoryKeywords(
        main=["Minerals"],
        supporting=[
            "calcium carbonate",
            "dicalcium phosphate",
            "monocalcium phosphate",
            "potassium chloride",
            "potassium citrate",
            "potassium gluconate",
            "sodium selenite",
            "sodium selenate",
            "sodium chloride",
            "magnesium oxide",
            "magnesium sulfate",
            "magnesium citrate",
            "magnesium gluconate",
            "ferrous sulfate",
            "ferrous gluconate",
            "ferrous fumarate",
            "iron oxide",
            "iron proteinate",
            "zinc oxide",
            "zinc sulfate",
            "zinc gluconate",
            "zinc proteinate",
            "zinc methionine",
            "copper sulfate",
            "copper gluconate",
            "copper proteinate",
            "manganese oxide",
            "manganese sulfate",
            "manganese proteinate",
            "selenium yeast",
            "potassium iodide",
            "calcium iodate",
            "cobalt sulfate",
            "cobalt proteinate",
            "mineral premix",
            "trace mineral blend",
            "Zinc Oxide",
            "Ferrous Sulfate",
            "Manganese Sulfate",
            "Calcium Iodate",
            "Magnesium Oxide",
            "Sodium Tripolyphosphate",
        ],
    ),
}


@dataclass
class IngredientClassification:
    """Classification result for a single ingredient."""

    ingredient: str
    category: IngredientCategory
    quality: Optional[QualityClass] = None
    matched_keywords: List[str] = None

    def __post_init__(self):
        if self.matched_keywords is None:
            self.matched_keywords = []


@dataclass
class CategoryResult:
    """Result for a category (Protein, Fat, Carb, Fiber)."""

    all_ingredients: List[str]
    high: List[str]
    good: List[str]
    moderate: List[str]
    low: List[str]
    other: List[str]
    quality_class: QualityClass


@dataclass
class IngredientQualityResult:
    """Complete ingredient quality classification result."""

    # All ingredients
    ingredients_all: str

    # Protein results
    protein_ingredients_all: str
    protein_ingredients_high: List[str]
    protein_ingredients_good: List[str]
    protein_ingredients_moderate: List[str]
    protein_ingredients_low: List[str]
    protein_ingredients_other: List[str]
    protein_quality_class: QualityClass

    # Fat results
    fat_ingredients_all: str
    fat_ingredients_high: List[str]
    fat_ingredients_good: List[str]
    fat_ingredients_moderate: List[str]
    fat_ingredients_low: List[str]
    fat_ingredients_other: List[str]
    fat_quality_class: QualityClass

    # Carb results
    carb_ingredients_all: str
    carb_ingredients_high: List[str]
    carb_ingredients_good: List[str]
    carb_ingredients_moderate: List[str]
    carb_ingredients_low: List[str]
    carb_ingredients_other: List[str]
    carb_quality_class: QualityClass

    # Fiber results
    fiber_ingredients_all: str
    fiber_ingredients_high: List[str]
    fiber_ingredients_good: List[str]
    fiber_ingredients_moderate: List[str]
    fiber_ingredients_low: List[str]
    fiber_ingredients_other: List[str]
    fiber_quality_class: QualityClass

    # Dirty Dozen
    dirty_dozen_ingredients: List[str]
    dirty_dozen_ingredients_count: int

    # Synthetic Nutrition
    synthetic_nutrition_addition: List[str]
    synthetic_nutrition_addition_count: int


class IngredientQualityClassifier:
    """
    Classifier for determining ingredient quality based on keyword matching.
    """

    def __init__(self):
        """Initialize the classifier."""
        self.protein_keywords = PROTEIN_KEYWORDS
        self.fat_keywords = FAT_KEYWORDS
        self.carb_keywords = CARB_KEYWORDS
        self.fiber_keywords = FIBER_KEYWORDS
        self.dirty_dozen_keywords = DIRTY_DOZEN_KEYWORDS
        self.synthetic_nutrition_keywords = SYNTHETIC_NUTRITION_KEYWORDS

    def classify(self, ingredients: Optional[str]) -> IngredientQualityResult:
        """
        Classify ingredients into categories and quality ratings.

        Args:
            ingredients: Comma-separated ingredient list

        Returns:
            IngredientQualityResult with all classifications
        """
        if not ingredients or not ingredients.strip():
            return self._empty_result()

        # Split ingredients by comma
        ingredient_list = self._split_ingredients(ingredients)

        # Normalize each ingredient
        normalized_ingredients = [self._normalize_text(ing) for ing in ingredient_list]

        # Classify each ingredient
        classifications = []
        for orig, normalized in zip(ingredient_list, normalized_ingredients):
            classification = self._classify_ingredient(normalized, orig)
            classifications.append(classification)

        # Group by category
        protein_ingredients = [
            c for c in classifications if c.category == IngredientCategory.PROTEIN
        ]
        fat_ingredients = [
            c for c in classifications if c.category == IngredientCategory.FAT
        ]
        carb_ingredients = [
            c for c in classifications if c.category == IngredientCategory.CARB
        ]
        fiber_ingredients = [
            c for c in classifications if c.category == IngredientCategory.FIBER
        ]

        # Process each category
        protein_result = self._process_category(
            protein_ingredients, self.protein_keywords, IngredientCategory.PROTEIN
        )
        fat_result = self._process_category(
            fat_ingredients, self.fat_keywords, IngredientCategory.FAT
        )
        carb_result = self._process_category(
            carb_ingredients, self.carb_keywords, IngredientCategory.CARB
        )
        fiber_result = self._process_category(
            fiber_ingredients, self.fiber_keywords, IngredientCategory.FIBER
        )

        # Identify Dirty Dozen
        dirty_dozen = self._identify_dirty_dozen(normalized_ingredients, ingredient_list)

        # Identify Synthetic Nutrition
        synthetic_nutrition = self._identify_synthetic_nutrition(
            normalized_ingredients, ingredient_list
        )

        # Build result
        return IngredientQualityResult(
            ingredients_all=", ".join(ingredient_list),
            protein_ingredients_all=", ".join([c.ingredient for c in protein_ingredients]),
            protein_ingredients_high=protein_result.high,
            protein_ingredients_good=protein_result.good,
            protein_ingredients_moderate=protein_result.moderate,
            protein_ingredients_low=protein_result.low,
            protein_ingredients_other=protein_result.other,
            protein_quality_class=protein_result.quality_class,
            fat_ingredients_all=", ".join([c.ingredient for c in fat_ingredients]),
            fat_ingredients_high=fat_result.high,
            fat_ingredients_good=fat_result.good,
            fat_ingredients_moderate=fat_result.moderate,
            fat_ingredients_low=fat_result.low,
            fat_ingredients_other=fat_result.other,
            fat_quality_class=fat_result.quality_class,
            carb_ingredients_all=", ".join([c.ingredient for c in carb_ingredients]),
            carb_ingredients_high=carb_result.high,
            carb_ingredients_good=carb_result.good,
            carb_ingredients_moderate=carb_result.moderate,
            carb_ingredients_low=carb_result.low,
            carb_ingredients_other=carb_result.other,
            carb_quality_class=carb_result.quality_class,
            fiber_ingredients_all=", ".join([c.ingredient for c in fiber_ingredients]),
            fiber_ingredients_high=fiber_result.high,
            fiber_ingredients_good=fiber_result.good,
            fiber_ingredients_moderate=fiber_result.moderate,
            fiber_ingredients_low=fiber_result.low,
            fiber_ingredients_other=fiber_result.other,
            fiber_quality_class=fiber_result.quality_class,
            dirty_dozen_ingredients=dirty_dozen,
            dirty_dozen_ingredients_count=len(dirty_dozen),
            synthetic_nutrition_addition=synthetic_nutrition,
            synthetic_nutrition_addition_count=len(synthetic_nutrition),
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

    def _classify_ingredient(
        self, normalized: str, original: str
    ) -> IngredientClassification:
        """
        Classify a single ingredient into a category.

        Returns classification with category and quality (if found).
        """
        # Check each category in priority order
        # Protein
        quality, matched = self._match_keywords(normalized, self.protein_keywords)
        if quality:
            return IngredientClassification(
                ingredient=original,
                category=IngredientCategory.PROTEIN,
                quality=quality,
                matched_keywords=matched,
            )

        # Fat
        quality, matched = self._match_keywords(normalized, self.fat_keywords)
        if quality:
            return IngredientClassification(
                ingredient=original,
                category=IngredientCategory.FAT,
                quality=quality,
                matched_keywords=matched,
            )

        # Carb
        quality, matched = self._match_keywords(normalized, self.carb_keywords)
        if quality:
            return IngredientClassification(
                ingredient=original,
                category=IngredientCategory.CARB,
                quality=quality,
                matched_keywords=matched,
            )

        # Fiber
        quality, matched = self._match_keywords(normalized, self.fiber_keywords)
        if quality:
            return IngredientClassification(
                ingredient=original,
                category=IngredientCategory.FIBER,
                quality=quality,
                matched_keywords=matched,
            )

        # Not classified
        return IngredientClassification(
            ingredient=original, category=IngredientCategory.OTHER
        )

    def _match_keywords(
        self, text: str, keywords_dict: Dict[QualityClass, CategoryKeywords]
    ) -> Tuple[Optional[QualityClass], List[str]]:
        """
        Match text against keywords and return quality class and matched keywords.

        Returns:
            (quality_class, matched_keywords)
        """
        # Check in priority order: HIGH, GOOD, MODERATE, LOW
        for quality in [QualityClass.HIGH, QualityClass.GOOD, QualityClass.MODERATE, QualityClass.LOW]:
            keywords = keywords_dict.get(quality)
            if not keywords:
                continue

            matched = []
            # Check main keywords first
            for main_keyword in keywords.main:
                main_normalized = self._normalize_text(main_keyword)
                if self._text_contains_keyword(text, main_normalized):
                    matched.append(main_keyword)
                    return quality, matched

            # Check supporting keywords
            for support_keyword in keywords.supporting:
                support_normalized = self._normalize_text(support_keyword)
                if self._text_contains_keyword(text, support_normalized):
                    matched.append(support_keyword)

            if matched:
                return quality, matched

        return None, []

    def _text_contains_keyword(self, text: str, keyword: str) -> bool:
        """Check if text contains keyword (with word boundaries for single words)."""
        # For multi-word keywords, check if phrase exists
        if len(keyword.split()) > 1:
            return keyword in text

        # For single words, use word boundaries
        pattern = r"\b" + re.escape(keyword) + r"\b"
        return bool(re.search(pattern, text))

    def _process_category(
        self,
        classifications: List[IngredientClassification],
        keywords_dict: Dict[QualityClass, CategoryKeywords],
        category: IngredientCategory,
    ) -> CategoryResult:
        """Process a category and group by quality."""
        high = []
        good = []
        moderate = []
        low = []
        other = []

        for classification in classifications:
            if not classification.quality:
                other.append(classification.ingredient)
            elif classification.quality == QualityClass.HIGH:
                high.append(classification.ingredient)
            elif classification.quality == QualityClass.GOOD:
                good.append(classification.ingredient)
            elif classification.quality == QualityClass.MODERATE:
                moderate.append(classification.ingredient)
            elif classification.quality == QualityClass.LOW:
                low.append(classification.ingredient)

        # Determine overall quality class
        quality_class = self._determine_quality_class(high, good, moderate, low)

        return CategoryResult(
            all_ingredients=[c.ingredient for c in classifications],
            high=high,
            good=good,
            moderate=moderate,
            low=low,
            other=other,
            quality_class=quality_class,
        )

    def _determine_quality_class(
        self, high: List[str], good: List[str], moderate: List[str], low: List[str]
    ) -> QualityClass:
        """
        Determine overall quality class using weighted deduction formula.

        Weighted Deduction = (count_high × 0 + count_good × 2 + count_moderate × 3 + count_low × 5) / total_ingredients

        Tier Thresholds:
        - 0.00 - 1.00 → High (0 pts)
        - 1.01 - 2.00 → Good (-2 pts)
        - 2.01 - 3.50 → Moderate (-3 pts)
        - 3.51+ → Low (-5 pts)
        """
        # Count ingredients in each tier
        count_high = len(high)
        count_good = len(good)
        count_moderate = len(moderate)
        count_low = len(low)
        
        total_ingredients = count_high + count_good + count_moderate + count_low
        
        # If no ingredients, return Moderate as default
        if total_ingredients == 0:
            return QualityClass.OTHER
        
        # Calculate weighted average
        # Tier Point Values: High=0, Good=2, Moderate=3, Low=5
        weighted_avg = (
            (count_high * 0) + 
            (count_good * 2) + 
            (count_moderate * 3) + 
            (count_low * 5)
        ) / total_ingredients
        
        # Map weighted average to quality tier
        if weighted_avg <= 1.00:
            return QualityClass.HIGH
        elif weighted_avg <= 2.00:
            return QualityClass.GOOD
        elif weighted_avg <= 3.50:
            return QualityClass.MODERATE
        else:  # weighted_avg > 3.50
            return QualityClass.LOW

    def _identify_dirty_dozen(
        self, normalized_ingredients: List[str], original_ingredients: List[str]
    ) -> List[str]:
        """Identify Dirty Dozen ingredients."""
        found = []
        found_set = set()

        for normalized, original in zip(normalized_ingredients, original_ingredients):
            for category, keywords in self.dirty_dozen_keywords.items():
                # Check main keywords
                for main_keyword in keywords.main:
                    main_normalized = self._normalize_text(main_keyword)
                    if self._text_contains_keyword(normalized, main_normalized):
                        if category not in found_set:
                            found.append(original)
                            found_set.add(category)
                            break

                # Check supporting keywords
                for support_keyword in keywords.supporting:
                    support_normalized = self._normalize_text(support_keyword)
                    if self._text_contains_keyword(normalized, support_normalized):
                        if category not in found_set:
                            found.append(original)
                            found_set.add(category)
                            break

        return found

    def _identify_synthetic_nutrition(
        self, normalized_ingredients: List[str], original_ingredients: List[str]
    ) -> List[str]:
        """Identify Synthetic Nutrition additions."""
        found = []
        found_set = set()

        for normalized, original in zip(normalized_ingredients, original_ingredients):
            for category, keywords in self.synthetic_nutrition_keywords.items():
                # Check main keywords
                for main_keyword in keywords.main:
                    main_normalized = self._normalize_text(main_keyword)
                    if self._text_contains_keyword(normalized, main_normalized):
                        if original not in found_set:
                            found.append(original)
                            found_set.add(original)
                            break

                # Check supporting keywords
                for support_keyword in keywords.supporting:
                    support_normalized = self._normalize_text(support_keyword)
                    if self._text_contains_keyword(normalized, support_normalized):
                        if original not in found_set:
                            found.append(original)
                            found_set.add(original)
                            break

        return found

    def _empty_result(self) -> IngredientQualityResult:
        """Return empty result."""
        empty_category = CategoryResult(
            all_ingredients=[],
            high=[],
            good=[],
            moderate=[],
            low=[],
            other=[],
            quality_class=QualityClass.OTHER,
        )

        return IngredientQualityResult(
            ingredients_all="",
            protein_ingredients_all="",
            protein_ingredients_high=[],
            protein_ingredients_good=[],
            protein_ingredients_moderate=[],
            protein_ingredients_low=[],
            protein_ingredients_other=[],
            protein_quality_class=QualityClass.OTHER,
            fat_ingredients_all="",
            fat_ingredients_high=[],
            fat_ingredients_good=[],
            fat_ingredients_moderate=[],
            fat_ingredients_low=[],
            fat_ingredients_other=[],
            fat_quality_class=QualityClass.OTHER,
            carb_ingredients_all="",
            carb_ingredients_high=[],
            carb_ingredients_good=[],
            carb_ingredients_moderate=[],
            carb_ingredients_low=[],
            carb_ingredients_other=[],
            carb_quality_class=QualityClass.OTHER,
            fiber_ingredients_all="",
            fiber_ingredients_high=[],
            fiber_ingredients_good=[],
            fiber_ingredients_moderate=[],
            fiber_ingredients_low=[],
            fiber_ingredients_other=[],
            fiber_quality_class=QualityClass.OTHER,
            dirty_dozen_ingredients=[],
            dirty_dozen_ingredients_count=0,
            synthetic_nutrition_addition=[],
            synthetic_nutrition_addition_count=0,
        )


# Convenience function
def classify_ingredient_quality(
    ingredients: Optional[str],
) -> IngredientQualityResult:
    """
    Quick classification function.

    Args:
        ingredients: Comma-separated ingredient list

    Returns:
        IngredientQualityResult
    """
    classifier = IngredientQualityClassifier()
    return classifier.classify(ingredients)

