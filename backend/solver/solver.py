from typing import Dict
from .rules import (
    SLOTS,
    ATTRS,
    BASE_STATS,
    RANDOM_CANDIDATES,
    RANDOM_VALUE,
    MASTER_BONUS,
    MOD_VALUE,
)
from .model import ArmorChoice, BuildResult


class EquipSolver:
    def __init__(self, target_attr: str, is_master: bool = True):
        self.target_attr = target_attr
        self.is_master = is_master

    def solve(self) -> BuildResult | None:
        total_stats: Dict[str, int] = {a: 0 for a in ATTRS}
        choices: Dict[str, ArmorChoice] = {}

        for slot in SLOTS:
            # 固定属性
            for attr, val in BASE_STATS.get(slot, {}).items():
                total_stats[attr] += val

            # 简单策略：随机属性直接选 target_attr（如果可选），否则选第一个
            candidates = RANDOM_CANDIDATES[slot]
            if self.target_attr in candidates:
                rand_attr = self.target_attr
            else:
                rand_attr = candidates[0]
            total_stats[rand_attr] += RANDOM_VALUE

            # 大师护甲：所有属性 +5（简化）
            if self.is_master:
                for a in ATTRS:
                    total_stats[a] += MASTER_BONUS

            # 模组：给 target_attr +10
            mod_attr = self.target_attr
            total_stats[mod_attr] += MOD_VALUE

            choices[slot] = ArmorChoice(
                slot=slot,
                random_attr=rand_attr,
                mod_attr=mod_attr,
                convert_to=None,
            )

        return BuildResult(total_stats=total_stats, choices=choices)
