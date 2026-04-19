from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def export_delivery_runtime(exports_dir: Path, delivery_runtime: Dict[str, Any]) -> Path:
    exports_dir.mkdir(parents=True, exist_ok=True)
    path = exports_dir / "simulation.html"
    path.write_text(str(delivery_runtime.get("html", "")), encoding="utf-8")
    return path
