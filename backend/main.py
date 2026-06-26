from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

from solver.model import ModSettings, SlotLock, Target
from solver.rules import ATTR_NAMES, FRAMEWORKS, SLOT_NAMES, SLOTS
from solver.solver import solve_build

app = FastAPI(title="Destiny 2 Build Optimizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TargetIn(BaseModel):
    id: str
    target: int
    priority: int


class ModSettingsIn(BaseModel):
    isMasterworked: bool
    useMods: bool
    useBlessing: bool
    useArtifice: bool


class SlotLockIn(BaseModel):
    slot: str
    locked: bool
    frameworkId: str = ""
    randomAttr: str = ""


class SolveRequest(BaseModel):
    targets: List[TargetIn]
    modSettings: ModSettingsIn
    slotLocks: List[SlotLockIn] = Field(default_factory=list)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/config")
def get_config():
    return {
        "attributes": [{"id": k, "name": v} for k, v in ATTR_NAMES.items()],
        "slots": [{"id": s, "name": SLOT_NAMES[s]} for s in SLOTS],
        "frameworks": [
            {"id": fid, "name": fw["name"], "fixed": fw["fixed"]}
            for fid, fw in FRAMEWORKS.items()
        ],
    }


@app.post("/solve")
def solve(req: SolveRequest):
    targets = [Target(**t.model_dump()) for t in req.targets]
    mod_settings = ModSettings(**req.modSettings.model_dump())
    slot_locks = [SlotLock(**s.model_dump()) for s in req.slotLocks]
    return solve_build(targets, mod_settings, slot_locks)
