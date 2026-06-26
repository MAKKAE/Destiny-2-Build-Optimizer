"""
配装数值计算 — 每个函数对应一条独立规则，便于调试与扩展。

单件护甲计算顺序：
  框架固定 → 随机属性 → 大师 → （写入总属性）→ 属性模组 → 祝福 或 转换（互斥）
"""

import logging
from typing import Dict, List, Optional, Tuple

from .rules import (
    ATTRS,
    BLESSING_VALUE,
    CONVERT_RULES,
    CONVERT_VALUE,
    FRAMEWORKS,
    MASTER_BONUS,
    MOD_VALUE,
    RANDOM_VALUE,
)

logger = logging.getLogger(__name__)

CALC_PIPELINE = [
    ("apply_framework_fixed_stats", "累加框架固定属性（30 / 25）"),
    ("apply_random_stat", f"累加随机属性 +{RANDOM_VALUE}"),
    ("apply_masterwork", f"大师护甲：最低三条各 +{MASTER_BONUS}"),
    ("apply_stat_mod", f"属性模组：指定属性 +{MOD_VALUE}"),
    ("apply_blessing_mod", f"祝福模组：最低三条各 +{BLESSING_VALUE}"),
    ("apply_conversion_mod", f"转换模组：-5 / +5（与祝福互斥）"),
    ("evaluate_targets_by_priority", "按优先级检查：实际值 ≥ 目标值"),
]


def log_active_pipeline(mod_settings) -> None:
    """保留接口供调试时手动调用，正常运行时不输出。"""
    pass


def lowest_attrs(piece_stats: Dict[str, int], count: int) -> List[str]:
    sorted_attrs = sorted(piece_stats.items(), key=lambda x: (x[1], x[0]))
    return [a for a, _ in sorted_attrs[:count]]


def apply_framework_fixed_stats(piece_stats: Dict[str, int], framework_id: str) -> None:
    fixed = FRAMEWORKS.get(framework_id, {}).get("fixed", {})
    for attr, val in fixed.items():
        piece_stats[attr] += val


def apply_random_stat(piece_stats: Dict[str, int], random_attr: str) -> None:
    piece_stats[random_attr] += RANDOM_VALUE


def apply_masterwork(piece_stats: Dict[str, int]) -> None:
    for attr in lowest_attrs(piece_stats, 3):
        piece_stats[attr] += MASTER_BONUS


def apply_stat_mod(total_stats: Dict[str, int], stat_mod_attr: Optional[str]) -> None:
    if stat_mod_attr:
        total_stats[stat_mod_attr] += MOD_VALUE


def apply_blessing_mod(piece_stats: Dict[str, int], total_stats: Dict[str, int]) -> None:
    for attr in lowest_attrs(piece_stats, 3):
        total_stats[attr] += BLESSING_VALUE


def apply_conversion_mod(
    total_stats: Dict[str, int], convert_from: str, convert_to: str
) -> None:
    total_stats[convert_from] -= CONVERT_VALUE
    total_stats[convert_to] += CONVERT_VALUE


def compute_piece_stats(
    slot_gear: Dict[str, Tuple[str, str]],
    slot: str,
    mod_settings,
) -> Dict[str, int]:
    """单件护甲在应用模组前的属性（框架 + 随机 + 大师）。"""
    piece_stats: Dict[str, int] = {a: 0 for a in ATTRS}
    framework_id, random_attr = slot_gear[slot]
    apply_framework_fixed_stats(piece_stats, framework_id)
    apply_random_stat(piece_stats, random_attr)
    if mod_settings.isMasterworked:
        apply_masterwork(piece_stats)
    return piece_stats


def _rank_convert_from(
    attr: str, total_stats: Dict[str, int], targets: List
) -> tuple:
    """
    转换来源优先级（越小越优先作为 -5 来源）：
    1. 不在目标列表中的属性（不要的属性）
    2. 已达标属性（优先扣溢出部分）
    3. 未达标属性（优先级越低越优先扣）
    """
    target_map = {t.id: t for t in targets}
    if attr not in target_map:
        return (0, 0)

    t = target_map[attr]
    actual = total_stats.get(attr, 0)
    shortfall = max(0, t.target - actual)
    if shortfall == 0:
        return (1, -(actual - t.target))

    return (2, t.priority)


def conversion_options_for_piece(
    slot: str,
    piece_stats: Dict[str, int],
    total_stats: Dict[str, int],
    targets: List,
) -> List[Tuple[str, str]]:
    """
    生成转换模组候选：尽量从「不要的属性」扣 -5，向未达标目标 +5。
    """
    allowed_to = CONVERT_RULES.get(slot, [])
    if not allowed_to:
        return []

    from_candidates = [a for a in ATTRS if piece_stats.get(a, 0) > 0]
    if not from_candidates:
        return []

    from_candidates.sort(
        key=lambda a: _rank_convert_from(a, total_stats, targets)
    )

    focus = None
    for t in sorted(targets, key=lambda x: x.priority):
        if total_stats.get(t.id, 0) < t.target and t.id in allowed_to:
            focus = t
            break

    to_ordered = list(allowed_to)
    if focus:
        to_ordered.sort(key=lambda a: 0 if a == focus.id else 1)

    options: List[Tuple[str, str]] = []
    seen: set = set()
    for to_attr in to_ordered:
        for from_attr in from_candidates:
            if from_attr == to_attr:
                continue
            pair = (from_attr, to_attr)
            if pair not in seen:
                seen.add(pair)
                options.append(pair)
    return options


def conversion_options(slot: str, random_attr: str) -> List[Tuple[str, str]]:
    """兼容旧接口：仅从随机属性转出。"""
    allowed = CONVERT_RULES.get(slot, [])
    return [(random_attr, to_attr) for to_attr in allowed if to_attr != random_attr]


def compute_build(
    slot_gear: Dict[str, Tuple[str, str]],
    slot_mods: Dict[str, dict],
    mod_settings,
) -> Dict[str, int]:
    """
    计算一套完整配装的总属性。

    slot_gear: { slot_id: (framework_id, random_attr) }
    slot_mods: { slot_id: { extra_mod, conversion, stat_mod_attr } }
    """
    total_stats: Dict[str, int] = {a: 0 for a in ATTRS}

    for slot, (framework_id, random_attr) in slot_gear.items():
        piece_stats: Dict[str, int] = {a: 0 for a in ATTRS}
        mods = slot_mods.get(slot, {})

        apply_framework_fixed_stats(piece_stats, framework_id)
        apply_random_stat(piece_stats, random_attr)

        for attr, val in piece_stats.items():
            total_stats[attr] += val

        if mod_settings.isMasterworked:
            pre = piece_stats.copy()
            apply_masterwork(piece_stats)
            for attr in ATTRS:
                total_stats[attr] += piece_stats[attr] - pre[attr]

        if mod_settings.useMods:
            apply_stat_mod(total_stats, mods.get("stat_mod_attr"))

        extra = mods.get("extra_mod")
        if extra == "blessing" and mod_settings.useBlessing:
            apply_blessing_mod(piece_stats, total_stats)
        elif extra == "conversion" and mod_settings.useArtifice:
            conv = mods.get("conversion")
            if conv:
                apply_conversion_mod(total_stats, conv[0], conv[1])

    return total_stats
