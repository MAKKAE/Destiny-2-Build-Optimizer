"""
搜索策略（两阶段）：
  阶段一：枚举/采样不同的「五件框架 ID 组合」，每件再选最优随机属性
  阶段二：框架固定后分配模组（同件祝福/转换互斥）
  多方案：每个方案必须对应不同的 framework_combo_key
"""

import itertools
import random
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

from .calc import (
    compute_build,
    compute_piece_stats,
    conversion_options_for_piece,
    _rank_convert_from,
)
from .model import BuildResult, ModSettings, SlotChoice, SlotLock, Target
from .rules import FRAMEWORKS, SLOTS, random_candidates_for_framework

MAX_SOLUTIONS = 5
ALL_FRAMEWORKS = list(FRAMEWORKS.keys())
RANDOM_FW_SAMPLES = 64
FULL_ENUM_FW_LIMIT = 8000
PHASE1_CANDIDATE_LIMIT = 48


def active_targets(targets: List[Target]) -> List[Target]:
    return [t for t in sorted(targets, key=lambda x: x.priority) if t.target > 0]


def all_targets_met(total_stats: Dict[str, int], targets: List[Target]) -> bool:
    return all(total_stats.get(t.id, 0) >= t.target for t in targets)


def first_unmet_target(
    total_stats: Dict[str, int], targets: List[Target]
) -> Optional[Target]:
    for t in targets:
        if total_stats.get(t.id, 0) < t.target:
            return t
    return None


def score_solution(total_stats: Dict[str, int], targets: List[Target]) -> Tuple:
    n = len(targets)
    met_count = 0
    weighted_shortfall = 0
    first_unmet_idx: Optional[int] = None
    overshoot_before_unmet = 0
    total_overshoot = 0

    for i, t in enumerate(targets):
        actual = total_stats.get(t.id, 0)
        shortfall = max(0, t.target - actual)
        overshoot = max(0, actual - t.target)

        if shortfall == 0:
            met_count += 1
        elif first_unmet_idx is None:
            first_unmet_idx = i

        weight = 10 ** max(n - i, 1)
        weighted_shortfall += shortfall * weight
        total_overshoot += overshoot

    if first_unmet_idx is not None:
        for i in range(first_unmet_idx):
            t = targets[i]
            actual = total_stats.get(t.id, 0)
            overshoot_before_unmet += max(0, actual - t.target)

    return (met_count, -weighted_shortfall, -overshoot_before_unmet, -total_overshoot)


def framework_affinity(framework_id: str, targets: List[Target]) -> float:
    fixed = FRAMEWORKS.get(framework_id, {}).get("fixed", {})
    n = len(targets)
    score = 0.0
    for i, t in enumerate(targets):
        weight = 10 ** max(n - i, 1)
        score += fixed.get(t.id, 0) * weight
    return score


def random_attr_affinity(random_attr: str, targets: List[Target]) -> float:
    n = len(targets)
    score = 0.0
    for i, t in enumerate(targets):
        if t.id == random_attr:
            weight = 10 ** max(n - i, 1)
            score += 20 * weight
    return score


def framework_combo_key(slot_gear: Dict[str, Tuple[str, str]]) -> tuple:
    """五件框架按槽位排列（仅用于展示）。"""
    return tuple(slot_gear.get(s, ("", ""))[0] for s in SLOTS)


def framework_multiset_key(slot_gear: Dict[str, Tuple[str, str]]) -> tuple:
    """
    五件框架的无序集合（槽位等价，仅换位置不算新方案）。
    同一套框架只保留得分最高的一种摆法。
    """
    return tuple(sorted(fw for fw, _ in slot_gear.values()))


def framework_multiset_label(slot_gear: Dict[str, Tuple[str, str]]) -> str:
    names = [
        FRAMEWORKS.get(fw, {}).get("name", fw)
        for fw in framework_multiset_key(slot_gear)
    ]
    return "、".join(names)


def is_slot_gear_fixed(slot_lock: SlotLock) -> bool:
    return bool(slot_lock.locked and slot_lock.frameworkId and slot_lock.randomAttr)


def framework_ids_for_slot(slot_lock: SlotLock, targets: List[Target]) -> List[str]:
    """该槽位可选框架：锁定则唯一，否则包含全部 12 种（避免漏掉如楷模典范）。"""
    if slot_lock.locked and slot_lock.frameworkId:
        return [slot_lock.frameworkId]

    ranked = sorted(
        ALL_FRAMEWORKS,
        key=lambda fw: framework_affinity(fw, targets),
        reverse=True,
    )
    return ranked


def build_gear_from_framework_combo(
    slot_locks: List[SlotLock],
    fw_by_slot: Dict[str, str],
    targets: List[Target],
    mod_settings: ModSettings,
) -> Dict[str, Tuple[str, str]]:
    """
    给定五件框架 ID，为每件选择最优随机属性。
    对未锁定随机的槽位枚举 4 种随机候选，取得分最高者。
    """
    acts = active_targets(targets)
    fixed: Dict[str, Tuple[str, str]] = {}

    for lock in slot_locks:
        slot = lock.slot
        if is_slot_gear_fixed(lock):
            fixed[slot] = (lock.frameworkId, lock.randomAttr)
        elif lock.locked and lock.randomAttr:
            fixed[slot] = (fw_by_slot[slot], lock.randomAttr)

    vary_slots: List[str] = []
    vary_choices: List[List[str]] = []
    for lock in slot_locks:
        slot = lock.slot
        if slot in fixed:
            continue
        fw_id = fw_by_slot[slot]
        vary_slots.append(slot)
        vary_choices.append(random_candidates_for_framework(fw_id))

    if not vary_slots:
        return {slot: fixed[slot] for slot in fixed}

    best_gear: Optional[Dict[str, Tuple[str, str]]] = None
    best_sc: Tuple = (-1, -10**18)

    for rand_tuple in itertools.product(*vary_choices):
        slot_gear = dict(fixed)
        for slot, rand in zip(vary_slots, rand_tuple):
            slot_gear[slot] = (fw_by_slot[slot], rand)
        sc = gear_phase_score(slot_gear, mod_settings, acts)
        if sc > best_sc:
            best_sc = sc
            best_gear = slot_gear

    return best_gear or fixed


def gear_phase_score(
    slot_gear: Dict[str, Tuple[str, str]],
    mod_settings: ModSettings,
    targets: List[Target],
) -> Tuple:
    no_mods = {s: {} for s in slot_gear}
    phase_settings = ModSettings(
        isMasterworked=mod_settings.isMasterworked,
        useMods=False,
        useBlessing=False,
        useArtifice=False,
    )
    total = compute_build(slot_gear, no_mods, phase_settings)
    return score_solution(total, targets)


def empty_slot_mods(slots: List[str]) -> Dict[str, dict]:
    return {
        s: {"extra_mod": None, "conversion": None, "stat_mod_attr": None} for s in slots
    }


def _greedy_fw_by_slot(
    slot_locks: List[SlotLock], targets: List[Target]
) -> Dict[str, str]:
    """逐槽取亲和力最高的框架，作为采样基准。"""
    acts = active_targets(targets)
    return {
        lock.slot: framework_ids_for_slot(lock, acts)[0] for lock in slot_locks
    }


def collect_distinct_framework_gears(
    slot_locks: List[SlotLock],
    mod_settings: ModSettings,
    targets: List[Target],
) -> List[Dict[str, Tuple[str, str]]]:
    acts = active_targets(targets)
    slots = [lock.slot for lock in slot_locks]
    per_slot_fw = [framework_ids_for_slot(lock, acts) for lock in slot_locks]

    fw_combo_count = 1
    for ids in per_slot_fw:
        fw_combo_count *= max(len(ids), 1)

    best_by_combo: Dict[tuple, Tuple[Tuple, Dict[str, Tuple[str, str]]]] = {}

    def register(fw_by_slot: Dict[str, str]) -> None:
        slot_gear = build_gear_from_framework_combo(
            slot_locks, fw_by_slot, acts, mod_settings
        )
        mkey = framework_multiset_key(slot_gear)
        sc = gear_phase_score(slot_gear, mod_settings, acts)
        if mkey not in best_by_combo or sc > best_by_combo[mkey][0]:
            best_by_combo[mkey] = (sc, slot_gear)

    if fw_combo_count <= FULL_ENUM_FW_LIMIT:
        for fw_tuple in itertools.product(*per_slot_fw):
            register(dict(zip(slots, fw_tuple)))
    else:
        baseline = _greedy_fw_by_slot(slot_locks, acts)
        register(baseline)

        # 每个未锁定槽位单独尝试全部 12 种框架，避免漏掉「楷模典范」等
        for lock in slot_locks:
            if lock.locked and lock.frameworkId:
                continue
            for fw_id in ALL_FRAMEWORKS:
                trial = dict(baseline)
                trial[lock.slot] = fw_id
                register(trial)

        for _ in range(RANDOM_FW_SAMPLES):
            fw_by = {slots[i]: random.choice(per_slot_fw[i]) for i in range(len(slots))}
            register(fw_by)

    ranked = sorted(best_by_combo.values(), key=lambda x: x[0], reverse=True)
    return [sg for _, sg in ranked[:PHASE1_CANDIDATE_LIMIT]]


def _assign_extra_mods_without_conversion(
    slot_locks: List[SlotLock],
    slot_mods: Dict[str, dict],
    slot_gear: Dict[str, Tuple[str, str]],
    mod_settings: ModSettings,
    acts: List[Target],
    eval_mods,
) -> None:
    """为每件护甲选择「无模组」或「祝福」，不使用转换。"""
    for lock in slot_locks:
        slot = lock.slot
        options: List[Tuple[Optional[str], Optional[tuple]]] = [(None, None)]
        if mod_settings.useBlessing:
            options.append(("blessing", None))

        best_extra = None
        best_conv = None
        best_score = eval_mods(slot_mods)[0]

        for extra, conv in options:
            trial = deepcopy(slot_mods)
            trial[slot]["extra_mod"] = extra
            trial[slot]["conversion"] = conv
            sc, _ = eval_mods(trial)
            if sc > best_score:
                best_score = sc
                best_extra = extra
                best_conv = conv

        slot_mods[slot]["extra_mod"] = best_extra
        slot_mods[slot]["conversion"] = best_conv


def _try_add_conversions_if_needed(
    slot_locks: List[SlotLock],
    slot_mods: Dict[str, dict],
    slot_gear: Dict[str, Tuple[str, str]],
    mod_settings: ModSettings,
    acts: List[Target],
    eval_mods,
) -> None:
    """仅在未达标且转换能严格提升评分时，才为单槽添加转换模组。"""
    if not mod_settings.useArtifice:
        return

    _, total = eval_mods(slot_mods)
    if all_targets_met(total, acts):
        return

    for lock in slot_locks:
        slot = lock.slot
        baseline_score = eval_mods(slot_mods)[0]
        piece_stats = compute_piece_stats(slot_gear, slot, mod_settings)
        convs = conversion_options_for_piece(
            slot, piece_stats, eval_mods(slot_mods)[1], acts
        )
        if not convs:
            continue

        best_conv = None
        best_score = baseline_score
        best_from_rank = (999, 999)

        for conv in convs:
            trial = deepcopy(slot_mods)
            trial[slot]["extra_mod"] = "conversion"
            trial[slot]["conversion"] = conv
            sc, trial_total = eval_mods(trial)
            if sc <= baseline_score:
                continue
            from_rank = _rank_convert_from(conv[0], trial_total, acts)
            if sc > best_score or (
                sc == best_score and from_rank < best_from_rank
            ):
                best_score = sc
                best_conv = conv
                best_from_rank = from_rank

        if best_conv is not None:
            slot_mods[slot]["extra_mod"] = "conversion"
            slot_mods[slot]["conversion"] = best_conv


def optimize_mods_for_gear(
    slot_locks: List[SlotLock],
    slot_gear: Dict[str, Tuple[str, str]],
    mod_settings: ModSettings,
    targets: List[Target],
) -> BuildResult:
    acts = active_targets(targets)
    slots = [lock.slot for lock in slot_locks]
    slot_mods = empty_slot_mods(slots)

    def eval_mods(mods: Dict[str, dict]) -> Tuple:
        total = compute_build(slot_gear, mods, mod_settings)
        return score_solution(total, acts), total

    if mod_settings.useMods:
        target_ids = [t.id for t in acts]
        for lock in slot_locks:
            slot = lock.slot
            best_attr = None
            best_score = eval_mods(slot_mods)[0]
            for attr in target_ids:
                trial = deepcopy(slot_mods)
                trial[slot]["stat_mod_attr"] = attr
                sc, _ = eval_mods(trial)
                if sc > best_score:
                    best_score = sc
                    best_attr = attr
            slot_mods[slot]["stat_mod_attr"] = best_attr

    # 先不用转换；仅在仍不达标且转换能严格改善结果时才启用
    _assign_extra_mods_without_conversion(
        slot_locks, slot_mods, slot_gear, mod_settings, acts, eval_mods
    )
    _try_add_conversions_if_needed(
        slot_locks, slot_mods, slot_gear, mod_settings, acts, eval_mods
    )

    _, final_total = eval_mods(slot_mods)
    met = all_targets_met(final_total, acts)

    return build_result_from_solution(
        slot_locks,
        slot_gear,
        slot_mods,
        mod_settings,
        targets,
        all_met=met,
        is_closest=not met,
    )


def build_result_from_solution(
    slot_locks: List[SlotLock],
    slot_gear: Dict[str, Tuple[str, str]],
    slot_mods: Dict[str, dict],
    mod_settings: ModSettings,
    targets: List[Target],
    all_met: bool,
    is_closest: bool,
) -> BuildResult:
    total_stats = compute_build(slot_gear, slot_mods, mod_settings)
    choices: Dict[str, SlotChoice] = {}

    for lock in slot_locks:
        slot = lock.slot
        fw_id, random_attr = slot_gear[slot]
        mods = slot_mods[slot]
        conv = mods.get("conversion")
        choices[slot] = SlotChoice(
            slot=slot,
            framework_id=fw_id,
            random_attr=random_attr,
            stat_mod_attr=mods.get("stat_mod_attr"),
            blessing=mods.get("extra_mod") == "blessing",
            convert_from=conv[0] if conv else None,
            convert_to=conv[1] if conv else None,
        )

    return BuildResult(
        total_stats=total_stats,
        choices=choices,
        all_met=all_met,
        is_closest=is_closest,
    )


def search_builds(
    targets: List[Target],
    mod_settings: ModSettings,
    slot_locks: List[SlotLock],
) -> List[BuildResult]:
    acts = active_targets(targets)
    if not acts:
        return []

    gear_list = collect_distinct_framework_gears(slot_locks, mod_settings, targets)

    # 对全部候选做含模组的完整评估，再排序（不能只看阶段一无模组的分数）
    optimized: List[BuildResult] = []
    for slot_gear in gear_list:
        optimized.append(
            optimize_mods_for_gear(slot_locks, slot_gear, mod_settings, targets)
        )

    optimized.sort(
        key=lambda r: (
            r.all_met,
            score_solution(r.total_stats, acts),
        ),
        reverse=True,
    )

    results: List[BuildResult] = []
    seen_multiset: set = set()
    for result in optimized:
        slot_gear = {
            slot: (c.framework_id, c.random_attr)
            for slot, c in result.choices.items()
        }
        mkey = framework_multiset_key(slot_gear)
        if mkey in seen_multiset:
            continue
        seen_multiset.add(mkey)
        results.append(result)
        if len(results) >= MAX_SOLUTIONS:
            break

    return results
