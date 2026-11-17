"""API de laboratorio aislada. No contiene datos reales ni servicios externos."""
import os
import time
from threading import Lock
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

app = FastAPI(title="TSI | API de laboratorio", version="1.0.0")
_LOCK = Lock()
_STATE = {"mode": "normal", "incident_id": 0}
ITEMS = [
    {"id": 1, "name": "Sensor temperatura", "stock": 18},
    {"id": 2, "name": "Sensor humedad", "stock": 9},
    {"id": 3, "name": "Microcontrolador", "stock": 24},
]

class FaultRequest(BaseModel):
    mode: str = Field(pattern="^(normal|slow|unavailable)$")


def mode() -> str:
    with _LOCK:
        return _STATE["mode"]


def emulate_dependency():
    current = mode()
    if current == "slow":
        time.sleep(0.8)
    elif current == "unavailable":
        raise HTTPException(status_code=503, detail="Dependencia simulada no disponible")


@app.get("/health/live")
def liveness():
    return {"status": "alive", "service": "api-lab"}


@app.get("/health/ready")
def readiness():
    if mode() == "unavailable":
        raise HTTPException(503, "Dependencia simulada no disponible")
    return {"status": "ready", "dependency": mode()}


@app.get("/api/items")
def list_items():
    emulate_dependency()
    return {"items": ITEMS, "total": len(ITEMS)}


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    emulate_dependency()
    found = next((x for x in ITEMS if x["id"] == item_id), None)
    if not found:
        raise HTTPException(404, "Elemento inexistente")
    return found


@app.get("/admin/status")
def admin_status(x_lab_key: str | None = Header(default=None)):
    authorize(x_lab_key)
    with _LOCK:
        return dict(_STATE)


def authorize(key: str | None):
    if os.getenv("LAB_FAULTS_ENABLED", "false").lower() != "true":
        raise HTTPException(404, "Funciones de laboratorio deshabilitadas")
    expected = os.getenv("LAB_ADMIN_KEY", "tsi-local-only")
    if not key or key != expected:
        raise HTTPException(403, "Clave de laboratorio incorrecta")


@app.post("/admin/fault")
def set_fault(payload: FaultRequest, x_lab_key: str | None = Header(default=None)):
    authorize(x_lab_key)
    with _LOCK:
        _STATE["mode"] = payload.mode
        _STATE["incident_id"] += 1
        return {"status": "updated", **_STATE}
