from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict


SAMPLE_DETECTIONS: Dict[str, Dict[str, Any]] = {
    "series_circuit": {
        "metadata": {"image_id": "series_circuit", "title": "Series sample"},
        "components": [
            {
                "id": "V1",
                "type": "voltage_source",
                "bbox": {"x": 30, "y": 30, "width": 25, "height": 50},
                "confidence": 0.98,
                "source": "vision",
            },
            {
                "id": "R1",
                "type": "resistor",
                "bbox": {"x": 110, "y": 40, "width": 80, "height": 25},
                "confidence": 0.96,
                "source": "vision",
            },
        ],
        "wires": [
            {"id": "w1", "points": [[55, 55], [110, 55]], "confidence": 0.92, "source": "vision"},
            {"id": "w2", "points": [[190, 55], [220, 55], [220, 100], [30, 100]], "confidence": 0.9, "source": "vision"},
            {"id": "w3", "points": [[30, 100], [30, 55]], "confidence": 0.91, "source": "vision"},
        ],
        "nodes": [
            {"id": "n1", "x": 55, "y": 55, "source": "vision"},
            {"id": "n0", "x": 30, "y": 100, "source": "vision"},
        ],
        "texts": [],
    },
    "parallel_circuit": {
        "metadata": {"image_id": "parallel_circuit", "title": "Parallel sample"},
        "components": [
            {
                "id": "V1",
                "type": "voltage_source",
                "bbox": {"x": 30, "y": 50, "width": 25, "height": 50},
                "confidence": 0.97,
                "source": "vision",
            },
            {
                "id": "R1",
                "type": "resistor",
                "bbox": {"x": 100, "y": 30, "width": 70, "height": 25},
                "confidence": 0.95,
                "source": "vision",
            },
            {
                "id": "R2",
                "type": "resistor",
                "bbox": {"x": 100, "y": 90, "width": 70, "height": 25},
                "confidence": 0.95,
                "source": "vision",
            },
        ],
        "wires": [
            {"id": "w1", "points": [[55, 75], [100, 75]], "confidence": 0.9, "source": "vision"},
        ],
        "nodes": [
            {"id": "n1", "x": 55, "y": 75, "source": "vision"},
            {"id": "n0", "x": 30, "y": 120, "source": "vision"},
        ],
        "texts": [],
    },
}


def preprocess_image(file_bytes: bytes) -> Dict[str, Any]:
    encoded = base64.b64encode(file_bytes).decode("ascii")
    return {
        "mime_type": "image/svg+xml",
        "image_base64": encoded,
        "steps": ["load", "grayscale_stub", "threshold_stub", "wire_hint_stub"],
    }


def detect_circuit_from_image_id(image_id: str) -> Dict[str, Any]:
    if image_id in SAMPLE_DETECTIONS:
        return SAMPLE_DETECTIONS[image_id]
    raise KeyError(f"Unknown sample image: {image_id}")


def load_sample_image(sample_dir: Path, image_id: str) -> bytes:
    file_path = sample_dir / f"{image_id}.svg"
    return file_path.read_bytes()
