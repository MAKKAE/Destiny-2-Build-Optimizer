SLOTS = ["head", "arms", "chest", "legs", "class_item"]

ATTRS = ["mobility", "resilience", "recovery", "discipline", "intellect", "strength"]

BASE_STATS = {
    "head": {"mobility": 30, "resilience": 25},
    "arms": {"recovery": 30, "discipline": 25},
    "chest": {"resilience": 30, "recovery": 25},
    "legs": {"discipline": 30, "strength": 25},
    "class_item": {"mobility": 30, "intellect": 25},
}

RANDOM_CANDIDATES = {
    "head": ["mobility", "recovery", "discipline", "strength"],
    "arms": ["mobility", "resilience", "intellect", "strength"],
    "chest": ["resilience", "recovery", "discipline", "intellect"],
    "legs": ["mobility", "recovery", "discipline", "strength"],
    "class_item": ["mobility", "resilience", "intellect", "strength"],
}

RANDOM_VALUE = 20
MASTER_BONUS = 5
MOD_VALUE = 10
MOD_ATTRS = ATTRS

CONVERT_VALUE = 5
CONVERT_RULES = {
    "head": ATTRS,
    "arms": ["strength"],
    "chest": ["discipline"],
    "legs": ["strength"],
    "class_item": ["strength"],
}
