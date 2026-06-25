from fastapi import FastAPI
from pydantic import BaseModel
from solver.solver import EquipSolver
from solver.rules import ATTRS

app = FastAPI()


class SolveRequest(BaseModel):
    target_attr: str
    is_master: bool = True


@app.get("/attrs")
def get_attrs():
    return {"attrs": ATTRS}


@app.post("/solve")
def solve_build(req: SolveRequest):
    solver = EquipSolver(target_attr=req.target_attr, is_master=req.is_master)
    result = solver.solve()

    if result is None:
        return {"success": False, "message": "No solution found"}

    return {
        "success": True,
        "total_stats": result.total_stats,
        "choices": {
            slot: {
                "random_attr": choice.random_attr,
                "mod_attr": choice.mod_attr,
                "convert_to": choice.convert_to,
            }
            for slot, choice in result.choices.items()
        },
    }
