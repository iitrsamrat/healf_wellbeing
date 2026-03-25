"""
Mock data for Healf personalisation system.
Represents users, products, interactions and biomarkers.
"""

# Product catalog — 20 products across 4 pillars
# Each product has ingredients mapped to health goals
PRODUCTS = {
    "p001": {
        "name": "Magnesium Glycinate",
        "brand": "Momentous",
        "pillar": "Sleep",
        "price": 29.99,
        "ingredients": ["Magnesium"],
        "health_goals": ["Better Sleep", "Muscle Recovery", "Stress Relief"],
        "benefits": "Supports sleep quality and muscle relaxation"
    },
    "p002": {
        "name": "Vitamin D3 + K2",
        "brand": "Thorne",
        "pillar": "Eat",
        "price": 24.99,
        "ingredients": ["Vitamin D3", "Vitamin K2"],
        "health_goals": ["Bone Health", "Immune Support", "Energy"],
        "benefits": "Supports bone health and immune function"
    },
    "p003": {
        "name": "Omega-3 Fish Oil",
        "brand": "Momentous",
        "pillar": "Eat",
        "price": 34.99,
        "ingredients": ["EPA", "DHA"],
        "health_goals": ["Heart Health", "Reduce Inflammation", "Brain Health"],
        "benefits": "Supports heart and brain health"
    },
    "p004": {
        "name": "Creatine Monohydrate",
        "brand": "Thorne",
        "pillar": "Move",
        "price": 34.99,
        "ingredients": ["Creatine Monohydrate"],
        "health_goals": ["Muscle Strength", "Athletic Performance"],
        "benefits": "Supports muscle strength and power output"
    },
    "p005": {
        "name": "Ashwagandha",
        "brand": "Momentous",
        "pillar": "Mind",
        "price": 27.99,
        "ingredients": ["Ashwagandha Extract"],
        "health_goals": ["Stress Relief", "Better Sleep", "Energy"],
        "benefits": "Supports stress resilience and calm energy"
    },
    "p006": {
        "name": "L-Theanine",
        "brand": "Pure Encapsulations",
        "pillar": "Mind",
        "price": 19.99,
        "ingredients": ["L-Theanine"],
        "health_goals": ["Stress Relief", "Focus", "Better Sleep"],
        "benefits": "Promotes calm focus without drowsiness"
    },
    "p007": {
        "name": "Whey Protein",
        "brand": "Momentous",
        "pillar": "Move",
        "price": 49.99,
        "ingredients": ["Whey Protein Isolate"],
        "health_goals": ["Muscle Recovery", "Muscle Strength"],
        "benefits": "Supports muscle repair and growth"
    },
    "p008": {
        "name": "Vitamin B12",
        "brand": "Thorne",
        "pillar": "Eat",
        "price": 18.99,
        "ingredients": ["Methylcobalamin B12"],
        "health_goals": ["Energy", "Brain Health", "Reduce Fatigue"],
        "benefits": "Supports energy production and brain function"
    },
    "p009": {
        "name": "Iron Bisglycinate",
        "brand": "Pure Encapsulations",
        "pillar": "Eat",
        "price": 22.99,
        "ingredients": ["Iron Bisglycinate"],
        "health_goals": ["Energy", "Reduce Fatigue", "Athletic Performance"],
        "benefits": "Gentle iron for energy and vitality"
    },
    "p010": {
        "name": "Sleep Drops",
        "brand": "The Nue Co",
        "pillar": "Sleep",
        "price": 35.00,
        "ingredients": ["Passionflower", "Chamomile", "Valerian Root"],
        "health_goals": ["Better Sleep", "Stress Relief", "Relaxation"],
        "benefits": "Botanical blend for natural sleep support"
    },
    "p011": {
        "name": "Zinc",
        "brand": "Thorne",
        "pillar": "Eat",
        "price": 16.99,
        "ingredients": ["Zinc Picolinate"],
        "health_goals": ["Immune Support", "Hormone Balance", "Skin Health"],
        "benefits": "Supports immune function and hormone health"
    },
    "p012": {
        "name": "Curcumin Complete",
        "brand": "Natroceutics",
        "pillar": "Eat",
        "price": 39.99,
        "ingredients": ["Curcumin"],
        "health_goals": ["Reduce Inflammation", "Joint Health", "Brain Health"],
        "benefits": "Highly bioavailable curcumin for inflammation support"
    },
    "p013": {
        "name": "Folate",
        "brand": "Thorne",
        "pillar": "Eat",
        "price": 15.99,
        "ingredients": ["5-MTHF Folate"],
        "health_goals": ["Energy", "Brain Health", "Hormone Balance"],
        "benefits": "Active folate for energy and cellular health"
    },
    "p014": {
        "name": "Oura Ring 4",
        "brand": "Oura",
        "pillar": "Move",
        "price": 349.00,
        "ingredients": [],
        "health_goals": ["Better Sleep", "Athletic Performance", "Stress Relief"],
        "benefits": "Track sleep, activity and recovery 24/7"
    },
    "p015": {
        "name": "Electrolytes",
        "brand": "LMNT",
        "pillar": "Move",
        "price": 24.99,
        "ingredients": ["Sodium", "Potassium", "Magnesium"],
        "health_goals": ["Athletic Performance", "Energy", "Hydration"],
        "benefits": "Clean electrolytes for hydration and performance"
    },
    "p016": {
        "name": "Melatonin",
        "brand": "Pure Encapsulations",
        "pillar": "Sleep",
        "price": 14.99,
        "ingredients": ["Melatonin"],
        "health_goals": ["Better Sleep", "Jet Lag", "Sleep Cycle"],
        "benefits": "Supports natural sleep cycle regulation"
    },
    "p017": {
        "name": "Colostrum",
        "brand": "ARMRA",
        "pillar": "Eat",
        "price": 55.00,
        "ingredients": ["Bovine Colostrum"],
        "health_goals": ["Immune Support", "Gut Health", "Athletic Performance"],
        "benefits": "Bioactive colostrum for immune and gut health"
    },
    "p018": {
        "name": "Berberine",
        "brand": "Thorne",
        "pillar": "Eat",
        "price": 32.99,
        "ingredients": ["Berberine HCl"],
        "health_goals": ["Blood Sugar", "Heart Health", "Gut Health"],
        "benefits": "Supports healthy blood sugar and metabolism"
    },
    "p019": {
        "name": "Gut Restore",
        "brand": "BodyHealth",
        "pillar": "Eat",
        "price": 44.99,
        "ingredients": ["PerfectAmino", "ImmunoLin", "Humic Acid"],
        "health_goals": ["Gut Health", "Muscle Recovery", "Immune Support"],
        "benefits": "Essential amino acids for gut and muscle health"
    },
    "p020": {
        "name": "Red Light Therapy",
        "brand": "BON CHARGE",
        "pillar": "Move",
        "price": 299.00,
        "ingredients": [],
        "health_goals": ["Muscle Recovery", "Skin Health", "Energy"],
        "benefits": "Science-backed red light for recovery and skin"
    }
}

# Users — 5 profiles at different stages of the journey
USERS = {
    "u001": {
        "name": "Sarah",
        "age": 32,
        "gender": "female",
        "goals": ["Better Sleep", "Stress Relief"],
        "pillar_affinity": "Sleep",
        "purchases": ["p001"],           # bought Magnesium
        "subscriptions": ["p001"],        # subscribed to Magnesium
        "browse_history": ["p010", "p006", "p016"],
        "zone_member": False,
        "biomarkers": {},
        "helix_profile": {
            "sleep_issue": "takes long to fall asleep",
            "stress_level": "high",
            "current_supplements": ["Magnesium"]
        }
    },
    "u002": {
        "name": "James",
        "age": 28,
        "gender": "male",
        "goals": ["Muscle Strength", "Athletic Performance", "Energy"],
        "pillar_affinity": "Move",
        "purchases": ["p004", "p007", "p015"],
        "subscriptions": ["p004", "p007"],
        "browse_history": ["p012", "p003", "p019"],
        "zone_member": False,
        "biomarkers": {},
        "helix_profile": {
            "training": "5 days a week strength training",
            "current_supplements": ["Creatine", "Whey Protein", "Electrolytes"]
        }
    },
    "u003": {
        "name": "Priya",
        "age": 41,
        "gender": "female",
        "goals": ["Energy", "Reduce Fatigue", "Immune Support"],
        "pillar_affinity": "Eat",
        "purchases": ["p002", "p008", "p013"],
        "subscriptions": ["p002"],
        "browse_history": ["p009", "p017", "p003"],
        "zone_member": True,
        "biomarkers": {
            "Vitamin D": {"value": 28, "unit": "nmol/L", "status": "deficient", "optimal_min": 50, "optimal_max": 125},
            "Ferritin": {"value": 12, "unit": "ug/L", "status": "deficient", "optimal_min": 30, "optimal_max": 150},
            "Active B12": {"value": 45, "unit": "pmol/L", "status": "suboptimal", "optimal_min": 50, "optimal_max": 165},
            "Magnesium": {"value": 0.75, "unit": "mmol/L", "status": "optimal", "optimal_min": 0.7, "optimal_max": 1.0},
            "CRP": {"value": 1.2, "unit": "mg/L", "status": "optimal", "optimal_min": 0, "optimal_max": 3.0}
        },
        "helix_profile": {
            "main_complaint": "always tired, especially afternoons",
            "current_supplements": ["Vitamin D", "B12", "Folate"]
        }
    },
    "u004": {
        "name": "Tom",
        "age": 25,
        "gender": "male",
        "goals": [],
        "pillar_affinity": None,
        "purchases": [],
        "subscriptions": [],
        "browse_history": ["p004", "p001"],
        "zone_member": False,
        "biomarkers": {},
        "helix_profile": {}
    },
    "u005": {
    "name": "Elena",
    "age": 45,
    "gender": "female",
    "goals": ["Heart Health", "Reduce Inflammation", "Brain Health"],
    "pillar_affinity": "Eat",
    "purchases": ["p003", "p012", "p002", "p011"],
    "subscriptions": ["p003", "p012"],
    "browse_history": ["p018", "p017", "p019"],
    "zone_member": True,
    "missed_second_test": False,
    "test1_date": "Jan 2024",
    "test2_date": "Jul 2024",

    # Current biomarkers — this is her LATEST (test 2) values
    "biomarkers": {
        "Vitamin D":       {"value": 68,   "unit": "nmol/L", "status": "optimal",   "optimal_min": 50,  "optimal_max": 125},
        "LDL Cholesterol": {"value": 3.6,  "unit": "mmol/L", "status": "elevated",  "optimal_min": 0,   "optimal_max": 3.0},
        "CRP":             {"value": 2.1,  "unit": "mg/L",   "status": "elevated",  "optimal_min": 0,   "optimal_max": 3.0},
        "ApoB":            {"value": 0.95, "unit": "g/L",    "status": "suboptimal","optimal_min": 0,   "optimal_max": 0.9},
        "Magnesium":       {"value": 0.78, "unit": "mmol/L", "status": "suboptimal","optimal_min": 0.7, "optimal_max": 1.0}
    },

    # Delta — Jan test vs Jul test
    # This is the labeled training example: products taken + outcome
    "biomarker_delta": {
        "LDL Cholesterol": {
            "before": 4.1,  "after": 3.6,  "unit": "mmol/L",
            "change": -0.5, "direction": "down", "status": "improving"
        },
        "CRP": {
            "before": 3.8,  "after": 2.1,  "unit": "mg/L",
            "change": -1.7, "direction": "down", "status": "improving"
        },
        "ApoB": {
            "before": 1.1,  "after": 0.95, "unit": "g/L",
            "change": -0.15,"direction": "down", "status": "improving"
        },
        "Magnesium": {
            "before": 0.65, "after": 0.78, "unit": "mmol/L",
            "change": +0.13,"direction": "up",   "status": "improving"
        }
    },

    # Products she was taking between test 1 and test 2
    # This is the attribution bridge — what moved the needle
    "products_between_tests": ["p003", "p012"],  # Omega-3, Curcumin

    "helix_profile": {
        "main_concern": "heart health and inflammation",
        "family_history": "cardiovascular disease",
        "current_supplements": ["Omega-3", "Curcumin", "Vitamin D", "Zinc"],
        "composite_pattern": "cardiovascular_risk",
        "pattern_markers": ["LDL Cholesterol", "CRP", "ApoB"]
    }
},
    "u006": {
        "name": "Marcus",
        "age": 38,
        "gender": "Male",
        "goals": ["Heart Health", "Energy", "Better Sleep"],
        "pillar": "Eat",
        "purchases": ["p002", "p003"],
        "subscriptions": ["p003"],
        "zone": True,
        "missed_second_test": True,
        "biomarkers": {
            "Vitamin D": "32 nmol/L — deficient",
            "LDL Cholesterol": "3.8 mmol/L — elevated",
            "CRP": "2.9 mg/L — elevated",
            "Ferritin": "18 ug/L — deficient"
        },
        "test1_date": "Jan 2024",
        "test2_date": None,
        "biomarker_delta": None
        }

}

# Ingredient to biomarker mapping
# Used to connect product ingredients to blood test results
INGREDIENT_BIOMARKER_MAP = {
    "Vitamin D3": "Vitamin D",
    "Methylcobalamin B12": "Active B12",
    "Magnesium": "Magnesium",
    "Iron Bisglycinate": "Ferritin",
    "EPA": "CRP",
    "DHA": "CRP",
    "Curcumin": "CRP",
    "Zinc Picolinate": "Zinc",
    "Folate": "Folate",
    "5-MTHF Folate": "Folate"
}

# Interaction log — simulated clicks and purchases
INTERACTION_LOG = [
    {"user_id": "u001", "product_id": "p010", "action": "view", "timestamp": "2024-01-10"},
    {"user_id": "u001", "product_id": "p006", "action": "view", "timestamp": "2024-01-10"},
    {"user_id": "u001", "product_id": "p001", "action": "purchase", "timestamp": "2024-01-11"},
    {"user_id": "u002", "product_id": "p004", "action": "purchase", "timestamp": "2024-01-05"},
    {"user_id": "u002", "product_id": "p007", "action": "purchase", "timestamp": "2024-01-05"},
    {"user_id": "u003", "product_id": "p002", "action": "purchase", "timestamp": "2023-12-01"},
    {"user_id": "u003", "product_id": "p009", "action": "view", "timestamp": "2024-01-15"},
    {"user_id": "u005", "product_id": "p018", "action": "view", "timestamp": "2024-01-20"},
    {"user_id": "u005", "product_id": "p003", "action": "purchase", "timestamp": "2023-11-01"},
]

# Popular products per goal — used for cold start social proof
POPULAR_BY_GOAL = {
    "Better Sleep": ["p001", "p010", "p006", "p016"],
    "Muscle Strength": ["p004", "p007", "p015"],
    "Energy": ["p008", "p002", "p005", "p009"],
    "Stress Relief": ["p005", "p006", "p010"],
    "Heart Health": ["p003", "p012", "p018"],
    "Reduce Inflammation": ["p003", "p012"],
    "Immune Support": ["p002", "p011", "p017"],
    "Athletic Performance": ["p004", "p007", "p015", "p014"],
    "Gut Health": ["p019", "p017", "p018"]
}
