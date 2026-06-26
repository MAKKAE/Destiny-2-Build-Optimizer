"""将求解器内部结果格式化为前端展示结构。"""

from typing import List

from .model import BuildResult, Target
from .rules import ATTR_NAMES, FRAMEWORKS, MOD_VALUE, RANDOM_VALUE, SLOT_NAMES, SLOTS
from .search import framework_multiset_label


def format_solutions(
    results: List[BuildResult],
    targets: List[Target],
) -> List[dict]:
    active_targets = [t for t in sorted(targets, key=lambda x: x.priority) if t.target > 0]

    solutions = []
    for idx, result in enumerate(results, start=1):
        conversion_count = sum(
            1 for c in result.choices.values() if c.convert_to is not None
        )

        priority_results = []
        for t in active_targets:
            actual = result.total_stats.get(t.id, 0)
            priority_results.append(
                {
                    "attr": t.id,
                    "attrName": ATTR_NAMES.get(t.id, t.id),
                    "rank": t.priority,
                    "actual": actual,
                    "target": t.target,
                    "met": actual >= t.target,
                }
            )

        slots = []
        for slot_id, choice in result.choices.items():
            fw = FRAMEWORKS.get(choice.framework_id, {})
            slots.append(
                {
                    "slotId": slot_id,
                    "slotName": SLOT_NAMES.get(slot_id, slot_id),
                    "frameworkId": choice.framework_id,
                    "frameworkName": fw.get("name", choice.framework_id or "—"),
                    "randomAttrName": f"{ATTR_NAMES.get(choice.random_attr, choice.random_attr)} +{RANDOM_VALUE}",
                    "statMod": (
                        {
                            "attr": choice.stat_mod_attr,
                            "attrName": ATTR_NAMES.get(choice.stat_mod_attr, choice.stat_mod_attr),
                            "value": MOD_VALUE,
                        }
                        if choice.stat_mod_attr
                        else None
                    ),
                    "blessingMod": (
                        {"name": "祝福模组（最低三条 +1）"}
                        if choice.blessing
                        else None
                    ),
                    "conversionMod": (
                        {
                            "from": choice.convert_from,
                            "fromName": ATTR_NAMES.get(choice.convert_from, choice.convert_from),
                            "to": choice.convert_to,
                            "toName": ATTR_NAMES.get(choice.convert_to, choice.convert_to),
                        }
                        if choice.convert_to
                        else None
                    ),
                }
            )

        slot_gear = {
            s: (result.choices[s].framework_id, result.choices[s].random_attr)
            for s in result.choices
        }

        solutions.append(
            {
                "id": idx,
                "conversionCount": conversion_count,
                "allMet": result.all_met,
                "isClosest": result.is_closest,
                "frameworkCombo": framework_multiset_label(slot_gear),
                "frameworkSlots": " / ".join(
                    f"{SLOT_NAMES.get(s, s)}:{FRAMEWORKS.get(result.choices[s].framework_id, {}).get('name', '')}"
                    for s in SLOTS
                    if s in result.choices
                ),
                "priorityResults": priority_results,
                "slots": slots,
            }
        )

    return solutions
