from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ArmorChoice:
    slot: str
    random_attr: str
    mod_attr: Optional[str]
    convert_to: Optional[str]


@dataclass
class BuildResult:
    total_stats: Dict[str, int]
    choices: Dict[str, ArmorChoice]
