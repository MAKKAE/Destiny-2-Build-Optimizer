from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from solver.solver import EquipSolver
from solver.rules import ATTRS

app = FastAPI()


# -----------------------------
# 请求模型（完全匹配前端）
# -----------------------------


class Target(BaseModel):
    id: str
    target: int
    priority: int


class ModSettings(BaseModel):
    isMasterworked: bool
    useMods: bool
    useBlessing: bool
    useArtifice: bool


class SlotLock(BaseModel):
    slot: str
    locked: bool
    frameworkId: str
    randomAttr: str


class SolveRequest(BaseModel):
    targets: List[Target]
    modSettings: ModSettings
    slotLocks: List[SlotLock]


# -----------------------------
# API：计算方案
# -----------------------------
@app.post("/solve")
def solve_build(req: SolveRequest):

    # 初始化求解器（你可以根据需要扩展）
    solver = EquipSolver(
        targets=req.targets, mod_settings=req.modSettings, slot_locks=req.slotLocks
    )

    result = solver.solve()

    if result is None:
        return {"success": False, "message": "No solution found"}

    # 返回统一格式
    return {
        "success": True,
        "solutions": result,  # 你在 solver.solve() 中返回方案数组即可
    }
