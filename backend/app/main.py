from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

try:
    from fastapi import FastAPI, File, Form, HTTPException, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:  # pragma: no cover - exercised only when dependency missing
    FastAPI = None  # type: ignore[assignment]
    File = None  # type: ignore[assignment]
    Form = None  # type: ignore[assignment]
    UploadFile = None  # type: ignore[assignment]
    HTTPException = RuntimeError  # type: ignore[assignment]
    CORSMiddleware = object  # type: ignore[assignment]

from backend.app.abstraction.compiler import compile_detection_to_physics
from backend.app.mechanics.service import (
    apply_mechanics_confirmation,
    generate_mechanics_scene,
    recognize_mechanics_problem,
    simulate_mechanics_scene,
)
from backend.app.scenes.figure1 import (
    apply_figure1_edit,
    build_figure1_scene,
    simulate_figure1_scene,
)
from backend.app.schemas.physics import PhysicsJsonDocument
from backend.app.schemas.scene import SceneDocument
from backend.app.simulation.solver import simulate_circuit


ROOT_DIR = Path(__file__).resolve().parents[2]
SAMPLE_DIR = ROOT_DIR / "sample_data"
RECOGNITION_SESSIONS: dict[str, dict] = {}
MECHANICS_SESSIONS: dict[str, dict] = {}


def _port_id_for_terminal(component_type: str, terminal: str) -> str | None:
    if terminal in {"a", "b", "left", "right", "top", "bottom", "positive", "negative"}:
        if component_type == "battery":
            if terminal == "positive":
                return "right"
            if terminal == "negative":
                return "left"
        if component_type in {"resistor", "lamp", "ammeter", "voltmeter"}:
            if terminal in {"a", "left"}:
                return "left"
            if terminal in {"b", "right"}:
                return "right"
        if component_type == "switch":
            if terminal == "a":
                return "top"
            if terminal == "b":
                return "bottom"
    return None


def _snap_component_ports_to_topology(scene: dict) -> dict:
    components = {item["id"]: item for item in scene.get("components", [])}
    node_points = {
        item["id"]: {"x": float(item["x"]), "y": float(item["y"])}
        for item in scene.get("components", [])
        if item.get("type") == "junction"
    }
    connections = scene.get("circuit_topology", {}).get("connections", [])

    for connection in connections:
        component_id = connection.get("component_id")
        terminal = connection.get("terminal")
        node_id = connection.get("node_id")
        component = components.get(component_id)
        node = node_points.get(node_id)
        if not component or not node:
            continue
        component_type = component.get("type", "")
        if component_type not in {"resistor", "lamp", "ammeter", "voltmeter"}:
            # Keep source-authored geometry for switch/battery/rheostat.
            continue
        target_port_id = _port_id_for_terminal(component.get("type", ""), str(terminal))
        if not target_port_id:
            continue
        port = next((p for p in component.get("ports", []) if p.get("id") == target_port_id), None)
        if not port:
            continue
        dx = float(port["x"]) - float(node["x"])
        dy = float(port["y"]) - float(node["y"])
        if (dx * dx + dy * dy) ** 0.5 > 120.0:
            # Prevent long-distance teleport that distorts layout.
            continue
        port["x"] = node["x"]
        port["y"] = node["y"]

    for component in scene.get("components", []):
        if component.get("type") not in {"resistor", "lamp"}:
            continue
        left = next((p for p in component.get("ports", []) if p.get("id") in {"left", "a"}), None)
        right = next((p for p in component.get("ports", []) if p.get("id") in {"right", "b"}), None)
        if not left or not right:
            continue
        dx = abs(float(left["x"]) - float(right["x"]))
        dy = abs(float(left["y"]) - float(right["y"]))
        if dx >= dy:
            height = max(18.0, float(component.get("height", 24.0)))
            component["x"] = min(float(left["x"]), float(right["x"]))
            component["y"] = (float(left["y"]) + float(right["y"])) / 2.0 - height / 2.0
            component["width"] = max(24.0, dx)
            component["height"] = height
        else:
            width = max(18.0, float(component.get("width", 24.0)))
            component["x"] = (float(left["x"]) + float(right["x"])) / 2.0 - width / 2.0
            component["y"] = min(float(left["y"]), float(right["y"]))
            component["width"] = width
            component["height"] = max(24.0, dy)
    return scene


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

    @app.post("/api/scenes/import-json")
    def import_scene_json(payload: dict):
        from backend.app.vision.recognition import simulate_recognized_scene

        scene = payload.get("scene")
        state = payload.get("state") or {}
        if not scene:
            raise HTTPException(status_code=400, detail="scene is required")
        scene = _snap_component_ports_to_topology(scene)
        try:
            validated_scene = SceneDocument.model_validate(scene).model_dump()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"invalid scene json: {exc}") from exc

        effective_state = {
            "switch_closed": bool(state.get("switch_closed", False)),
            "battery_voltage": float(state.get("battery_voltage", 6.0)),
            "resistor_value": float(state.get("resistor_value", 10.0)),
            "rheostat_total": float(state.get("rheostat_total", 20.0)),
            "rheostat_ratio": float(state.get("rheostat_ratio", 0.5)),
        }

        if validated_scene["id"] == "figure-1":
            simulation = simulate_figure1_scene(validated_scene, effective_state)
        else:
            simulation = simulate_recognized_scene(validated_scene, effective_state)
        return {
            "scene": validated_scene,
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
        from backend.app.vision.pipeline import preprocess_image

        file_bytes = await file.read()
        preprocessing = preprocess_image(file_bytes)
        image_id = file.filename.rsplit(".", 1)[0] if file.filename else "uploaded-image"
        return {"image_id": image_id, "preprocessing": preprocessing}

    @app.post("/api/recognize")
    async def recognize_uploaded_image(file: UploadFile = File(...)):
        from backend.app.vision.recognition import recognize_clean_circuit

        file_bytes = await file.read()
        try:
            payload = recognize_clean_circuit(file_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        session_id = uuid4().hex
        session_payload = {
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        RECOGNITION_SESSIONS[session_id] = session_payload
        return session_payload

    @app.post("/api/recognize/{session_id}/confirm")
    def confirm_recognition(session_id: str, payload: dict):
        from backend.app.vision.recognition import apply_recognition_confirmation

        session_payload = RECOGNITION_SESSIONS.get(session_id)
        if session_payload is None:
            raise HTTPException(status_code=404, detail="recognition session not found")
        updates = payload.get("updates", {})
        try:
            confirmed = apply_recognition_confirmation(session_payload, updates)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        session_payload["scene"] = confirmed["scene"]
        session_payload["state"] = confirmed["state"]
        session_payload["simulation"] = confirmed["simulation"]
        session_payload["needs_confirmation"] = False
        session_payload["issues"] = []
        session_payload["topology_warnings"] = []
        return {
            "session_id": session_id,
            "scene": confirmed["scene"],
            "state": confirmed["state"],
            "simulation": confirmed["simulation"],
        }

    @app.post("/api/mechanics/recognize")
    async def recognize_mechanics(
        problem_text: str = Form(""),
        solution_text: str = Form(""),
        final_answers: str = Form(""),
        image: Optional[UploadFile] = File(default=None),
    ):
        image_bytes = await image.read() if image is not None else None
        payload = recognize_mechanics_problem(
            problem_text=problem_text,
            solution_text=solution_text,
            final_answers=final_answers,
            image_bytes=image_bytes,
            image_filename=image.filename if image is not None else None,
        )
        session_id = uuid4().hex
        session_payload = {
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        MECHANICS_SESSIONS[session_id] = session_payload
        return session_payload

    @app.post("/api/mechanics/{session_id}/confirm")
    def confirm_mechanics(session_id: str, payload: dict):
        session_payload = MECHANICS_SESSIONS.get(session_id)
        if session_payload is None:
            raise HTTPException(status_code=404, detail="mechanics session not found")
        confirmed = apply_mechanics_confirmation(session_payload, payload.get("updates", {}))
        session_payload.update(confirmed)
        return {
            "session_id": session_id,
            "problem_representation": confirmed["problem_representation"],
            "candidate_models": confirmed["candidate_models"],
            "selected_model": confirmed["selected_model"],
            "solution_model": confirmed["solution_model"],
            "conflict_items": confirmed["conflict_items"],
            "simulation": confirmed["simulation"],
            "needs_confirmation": confirmed["needs_confirmation"],
            "confidence_breakdown": confirmed["confidence_breakdown"],
            "issues": confirmed["issues"],
        }

    @app.post("/api/mechanics/{session_id}/generate-scene")
    def generate_mechanics_scene_endpoint(session_id: str):
        session_payload = MECHANICS_SESSIONS.get(session_id)
        if session_payload is None:
            raise HTTPException(status_code=404, detail="mechanics session not found")
        return generate_mechanics_scene(session_payload)

    @app.post("/api/mechanics/{session_id}/simulate")
    def simulate_mechanics_scene_endpoint(session_id: str, payload: dict):
        session_payload = MECHANICS_SESSIONS.get(session_id)
        if session_payload is None:
            raise HTTPException(status_code=404, detail="mechanics session not found")
        stage_id = payload.get("stage_id") or "slope"
        progress = float(payload.get("progress", 0.0))
        return simulate_mechanics_scene(
            session_payload,
            stage_id=stage_id,
            progress=progress,
        )

    @app.post("/api/detect")
    def detect(payload: dict):
        from backend.app.vision.pipeline import detect_circuit_from_image_id

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
        from backend.app.vision.pipeline import detect_circuit_from_image_id

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
