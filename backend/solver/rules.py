"""游戏规则与静态数据 — 与前端 config.js 保持一致，完整求解逻辑在此扩展。"""

ATTRS = ["hp", "melee", "grenade", "super", "class", "weapon"]

ATTR_NAMES = {
    "hp": "生命",
    "melee": "近战",
    "grenade": "手雷",
    "super": "超能",
    "class": "职业",
    "weapon": "武器",
}

SLOTS = ["head", "hands", "chest", "legs", "class"]

SLOT_NAMES = {
    "head": "头部",
    "hands": "手部",
    "chest": "胸部",
    "legs": "腿部",
    "class": "职业",
}

# 槽位默认可选随机属性（未锁定框架时使用）
RANDOM_CANDIDATES = {
    "head": ["hp", "super", "grenade", "melee"],
    "hands": ["hp", "melee", "class", "weapon"],
    "chest": ["melee", "super", "grenade", "class"],
    "legs": ["hp", "super", "grenade", "melee"],
    "class": ["hp", "melee", "class", "weapon"],
}

RANDOM_VALUE = 20
MASTER_BONUS = 5
MOD_VALUE = 10
BLESSING_VALUE = 1
CONVERT_VALUE = 5

# 各槽位转换模组可增加属性的限制
CONVERT_RULES = {
    "head": ATTRS,
    "hands": ["weapon"],
    "chest": ["grenade"],
    "legs": ["melee"],
    "class": ["weapon"],
}

# 12 种装备框架
FRAMEWORKS = {
    "expert": {
        "name": "专家",
        "fixed": {"class": 30, "weapon": 25},
    },
    "assaulter": {
        "name": "突击手",
        "fixed": {"melee": 30, "weapon": 25},
    },
    "paragon": {
        "name": "楷模典范",
        "fixed": {"melee": 25, "super": 30},
    },
    "energizer": {
        "name": "高能者",
        "fixed": {"super": 25, "weapon": 30},
    },
    "gunslinger": {
        "name": "枪手",
        "fixed": {"grenade": 25, "weapon": 30},
    },
    "breacher": {
        "name": "突围者",
        "fixed": {"hp": 30, "grenade": 25},
    },
    "bastion": {
        "name": "堡垒",
        "fixed": {"hp": 30, "class": 25},
    },
    "fighter": {
        "name": "搏击手",
        "fixed": {"hp": 25, "melee": 30},
    },
    "grenadier": {
        "name": "掷雷手",
        "fixed": {"grenade": 30, "super": 25},
    },
    "demo_expert": {
        "name": "爆破专家",
        "fixed": {"grenade": 30, "class": 25},
    },
    "armored": {
        "name": "装甲兵",
        "fixed": {"hp": 25, "super": 30},
    },
    "marauder": {
        "name": "掠夺者",
        "fixed": {"melee": 25, "class": 30},
    },
}


def random_candidates_for_framework(framework_id: str) -> list[str]:
    """根据框架固定属性推导随机属性候选（四选一）。"""
    fw = FRAMEWORKS.get(framework_id)
    if not fw:
        return []
    fixed = set(fw["fixed"].keys())
    return [a for a in ATTRS if a not in fixed]
