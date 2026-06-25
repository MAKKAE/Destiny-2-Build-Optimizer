from typing import Dict, List, Optional
from .rules import (
    ATTRS,
    BASE_STATS,
    RANDOM_CANDIDATES,
    RANDOM_VALUE,
    MASTER_BONUS,
    MOD_VALUE,
)
from .model import ArmorChoice, BuildResult


class EquipSolver:
    """
    新版求解器：支持多属性目标、模组开关、槽位锁定、框架选择
    """

    def __init__(self, targets, mod_settings, slot_locks):
        self.targets = targets
        self.mod_settings = mod_settings
        self.slot_locks = slot_locks

    def solve(self) -> Optional[List[BuildResult]]:
        """
        这里返回一个方案数组（前端需要多个方案）
        目前先返回一个简化方案，后续你可以扩展为多方案搜索
        """

        total_stats: Dict[str, int] = {a: 0 for a in ATTRS}
        choices: Dict[str, ArmorChoice] = {}

        # 遍历 5 个槽位
        for slot_lock in self.slot_locks:
            slot = slot_lock.slot

            # 固定属性（框架固定属性你后续可加入）
            for attr, val in BASE_STATS.get(slot, {}).items():
                total_stats[attr] += val

            # 随机属性
            if slot_lock.locked and slot_lock.randomAttr:
                rand_attr = slot_lock.randomAttr
            else:
                # 默认策略：如果目标属性里有优先级 1 的，就选它
                primary_target = self.targets[0].id
                candidates = RANDOM_CANDIDATES[slot]
                rand_attr = primary_target if primary_target in candidates else candidates[0]

            total_stats[rand_attr] += RANDOM_VALUE

            # 大师护甲
            if self.mod_settings.isMasterworked:
                for a in ATTRS:
                    total_stats[a] += MASTER_BONUS

            # 属性模组（useMods）
            mod_attr = None
            if self.mod_settings.useMods:
                # 简化策略：给优先级最高的属性加 +10
                mod_attr = self.targets[0].id
                total_stats[mod_attr] += MOD_VALUE

            # 转换模组（useArtifice）
            convert_to = None
            if self.mod_settings.useArtifice:
                # 简化策略：把随机属性 -5，目标属性 +5
                convert_to = self.targets[0].id
                total_stats[rand_attr] -= 5
                total_stats[convert_to] += 5

            # 保存槽位选择
            choices[slot] = ArmorChoice(
                slot=slot,
                random_attr=rand_attr,
                mod_attr=mod_attr,
                convert_to=convert_to,
            )

        # 返回单个方案（你后续可以扩展为多个）
        return [
            BuildResult(
                total_stats=total_stats,
                choices=choices
            )
        ]
