"""求解入口 — 协调两阶段搜索与结果格式化。"""

from typing import List, Optional

from .formatter import format_solutions
from .model import ModSettings, SlotLock, Target
from .search import MAX_SOLUTIONS, active_targets, search_builds


class EquipSolver:
    def __init__(
        self,
        targets: List[Target],
        mod_settings: ModSettings,
        slot_locks: List[SlotLock],
    ):
        self.targets = targets
        self.mod_settings = mod_settings
        self.slot_locks = slot_locks

    def solve(self) -> Optional[List[dict]]:
        if not active_targets(self.targets):
            return []

        if not self._has_locked_preset():
            return None

        results = search_builds(self.targets, self.mod_settings, self.slot_locks)
        if not results:
            return None

        return format_solutions(results, self.targets)

    def _has_locked_preset(self) -> bool:
        return any(
            lock.locked and lock.frameworkId and lock.randomAttr
            for lock in self.slot_locks
        )


def solve_build(
    targets: List[Target],
    mod_settings: ModSettings,
    slot_locks: List[SlotLock],
) -> dict:
    solutions = EquipSolver(targets, mod_settings, slot_locks).solve()

    if solutions is None:
        return {
            "success": False,
            "message": "请至少锁定一个部位的框架与随机属性",
            "solutions": [],
        }

    if not solutions:
        return {
            "success": False,
            "message": "请设置至少一个大于 0 的目标属性",
            "solutions": [],
        }

    all_met = solutions[0].get("allMet", False)
    count = len(solutions)

    if all_met:
        message = f"已找到 {count} 种不同框架套装方案（最多 {MAX_SOLUTIONS} 个，同套装换槽位不重复）"
    else:
        message = f"未完全达标，已返回 {count} 种不同框架套装的最接近方案"

    return {
        "success": True,
        "allMet": all_met,
        "isClosest": not all_met,
        "message": message,
        "solutions": solutions,
    }
