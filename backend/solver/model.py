from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Target:
    id: str
    target: int
    priority: int


@dataclass
class ModSettings:
    isMasterworked: bool
    useMods: bool
    useBlessing: bool
    useArtifice: bool


@dataclass
class SlotLock:
    slot: str
    locked: bool
    frameworkId: str
    randomAttr: str


@dataclass
class SlotChoice:
    slot: str
    framework_id: str
    random_attr: str
    stat_mod_attr: Optional[str] = None
    blessing: bool = False
    convert_from: Optional[str] = None
    convert_to: Optional[str] = None


@dataclass
class BuildResult:
    total_stats: Dict[str, int]
    choices: Dict[str, SlotChoice] = field(default_factory=dict)
    all_met: bool = False
    is_closest: bool = False


@dataclass
class SolveInput:
    targets: List[Target]
    mod_settings: ModSettings
    slot_locks: List[SlotLock]
