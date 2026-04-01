from __future__ import annotations

import json
from pathlib import Path

try:
    from fastapi import FastAPI, File, HTTPException, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:  # pragma: no cover - exercised only when dependency missing
    FastAPI = None  # type: ignore[assignment]
    File = None  # type: ignore[assignment]
    UploadFile = None  # type: ignore[assignment]
    HTTPException = RuntimeError  # type: ignore[assignment]
    CORSMiddleware = object  # type: ignore[assignment]

from backend.app.abstraction.compiler import compile_detection_to_physics
from backend.app.scenes.figure1 import (
    apply_figure1_edit,
    build_figure1_scene,
    simulate_figure1_scene,
)
from backend.app.schemas.physics import PhysicsJsonDocument
from backend.app.simulation.solver import simulate_circuit
from backend.app.vision.pipeline import (
    detect_circuit_from_image_id,
    load_sample_image,
    preprocess_image,
)
from backend.app.vision.recognition import recognize_clean_circuit


ROOT_DIR = Path(__file__).resolve().parents[2]
SAMPLE_DIR = ROOT_DIR / "sample_data"


def create_app():
    if FastAPI is None:
        raise RuntimeError(
            "FastAPI is not installed. Install backend dependencies to run the API."
        )

    app = FastAPI(title="Circuit Image to Simulation MVP", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    @app.get("/api/samples")
    def list_samples():
        return [
            {
                "id": "figure-1",
                "title": "图 1 复刻式电路 simulation",
                "status": "ready",
            },
            {
                "id": "figure-2",
                "title": "图 2 器材布局 simulation",
                "status": "coming_soon",
            },
        ]

    @app.get("/api/scenes/figure-1")
    def get_figure1_scene():
        payload = build_figure1_scene()
        simulation = simulate_figure1_scene(payload["scene"], payload["state"])
        return {
            "reference_image": payload["reference_image"],
            "scene": payload["scene"],
            "state": payload["state"],
            "simulation": simulation,
        }

    @app.post("/api/scenes/figure-1/simulate")
    def simulate_figure1(payload: dict):
        scene = payload.get("scene")
        state = payload.get("state")
        if not scene or not state:
            raise HTTPException(status_code=400, detail="scene and state are required")
        return simulate_figure1_scene(scene, state)

    @app.post("/api/scenes/figure-1/edit")
    def edit_figure1(payload: dict):
        scene = payload.get("scene")
        edit = payload.get("edit")
        state = payload.get("state")
        if not scene or not edit:
            raise HTTPException(status_code=400, detail="scene and edit are required")
        try:
            updated_scene = apply_figure1_edit(scene, edit)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        effective_state = state or build_figure1_scene()["state"]
        simulation = simulate_figure1_scene(updated_scene, effective_state)
        return {
            "scene": updated_scene,
            "state": effective_state,
            "simulation": simulation,
        }

    @app.get("/api/samples/{image_id}")
    def get_sample(image_id: str):
        if image_id == "figure-1":
            return get_figure1_scene()
        raise HTTPException(status_code=404, detail=f"Unsupported sample: {image_id}")

    @app.post("/api/upload")
    async def upload_image(file: UploadFile = File(...)):
        file_bytes = await file.read()
        preprocessing = preprocess_image(file_bytes)
        image_id = file.filename.rsplit(".", 1)[0] if file.filename else "uploaded-image"
        return {"image_id": image_id, "preprocessing": preprocessing}

    @app.post("/api/recognize")
    async def recognize_uploaded_image(file: UploadFile = File(...)):
        file_bytes = await file.read()
        try:
            return recognize_clean_circuit(file_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/detect")
    def detect(payload: dict):
        image_id = payload.get("image_id")
        if not image_id:
            raise HTTPException(status_code=400, detail="image_id is required")
        try:
            return detect_circuit_from_image_id(image_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/compile")
    def compile_topology(payload: dict):
        return compile_detection_to_physics(payload)

    @app.post("/api/simulate")
    def simulate(payload: dict):
        document = PhysicsJsonDocument.model_validate(payload)
        return simulate_circuit(document.model_dump())

    @app.get("/api/export/{image_id}")
    def export_sample(image_id: str):
        if image_id == "figure-1":
            payload = build_figure1_scene()
            simulation = simulate_figure1_scene(payload["scene"], payload["state"])
            return {
                "image_id": image_id,
                "scene": payload["scene"],
                "state": payload["state"],
                "simulation": simulation,
                "pretty": json.dumps(
                    {
                        "scene": payload["scene"],
                        "state": payload["state"],
                        "simulation": simulation,
                    },
                    indent=2,
                ),
            }
        detection = detect_circuit_from_image_id(image_id)
        physics = compile_detection_to_physics(detection)
        return {
            "image_id": image_id,
            "physics_json": physics,
            "pretty": json.dumps(physics, indent=2),
        }

    return app


app = create_app() if FastAPI is not None else None
