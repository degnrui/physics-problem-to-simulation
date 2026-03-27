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
from backend.app.schemas.physics import PhysicsJsonDocument
from backend.app.simulation.solver import simulate_circuit
from backend.app.vision.pipeline import (
    detect_circuit_from_image_id,
    load_sample_image,
    preprocess_image,
)


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
                "id": "series_circuit",
                "title": "Series resistor circuit",
                "image_path": "/sample_data/series_circuit.svg",
            },
            {
                "id": "parallel_circuit",
                "title": "Parallel resistor circuit",
                "image_path": "/sample_data/parallel_circuit.svg",
            },
        ]

    @app.get("/api/samples/{image_id}")
    def get_sample(image_id: str):
        try:
            image_bytes = load_sample_image(SAMPLE_DIR, image_id)
            detection = detect_circuit_from_image_id(image_id)
        except (FileNotFoundError, KeyError) as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        preprocessing = preprocess_image(image_bytes)
        physics = compile_detection_to_physics(detection)
        simulation = simulate_circuit(physics)
        return {
            "sample": {"id": image_id, "image_svg": image_bytes.decode("utf-8")},
            "preprocessing": preprocessing,
            "detection": detection,
            "physics": physics,
            "simulation": simulation,
        }

    @app.post("/api/upload")
    async def upload_image(file: UploadFile = File(...)):
        file_bytes = await file.read()
        preprocessing = preprocess_image(file_bytes)
        image_id = file.filename.rsplit(".", 1)[0] if file.filename else "uploaded-image"
        return {"image_id": image_id, "preprocessing": preprocessing}

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
        detection = detect_circuit_from_image_id(image_id)
        physics = compile_detection_to_physics(detection)
        return {
            "image_id": image_id,
            "physics_json": physics,
            "pretty": json.dumps(physics, indent=2),
        }

    return app


app = create_app() if FastAPI is not None else None
