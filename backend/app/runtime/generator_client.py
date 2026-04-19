from __future__ import annotations

from typing import Any, Dict

from app.config import settings


class RuntimeGeneratorClient:
    def generate(self, runtime_package: Dict[str, Any]) -> Dict[str, Any]:
        design = runtime_package["design_spec"]
        teacher_view = design["pedagogical_views"]["teacher"]
        chart_markup = "".join(
            f'<section class="chart-card" data-chart="{chart["id"]}">{chart["title"]}</section>'
            for chart in design["charts"]
        )
        measurement_markup = "".join(
            f'<section class="measurement-card" data-measurement="{panel["id"]}">{panel["title"]}</section>'
            for panel in design["measurement_panels"]
        )
        control_markup = "".join(
            f'<label class="control" for="{control["id"]}">{control["label"]}</label>'
            f'<input id="{control["id"]}" type="{control["input_type"]}" value="{control["default"]}" />'
            for control in design["controls"]
            if control["id"] not in {"play", "pause", "reset"}
        )
        html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{design["title"]}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 0; background: #f4f6f8; color: #10212b; }}
      main {{ display: grid; gap: 16px; padding: 24px; }}
      .runtime-shell {{ display: grid; grid-template-columns: 2fr 1fr; gap: 16px; }}
      canvas {{ width: 100%; min-height: 320px; background: #dfe9ee; border-radius: 16px; }}
      .panel, .controls {{ background: white; border-radius: 16px; padding: 16px; }}
      .controls-row {{ display: flex; gap: 12px; flex-wrap: wrap; }}
      button {{ padding: 10px 16px; border-radius: 999px; border: none; background: #1b6b73; color: white; }}
      .evidence-grid {{ display: grid; gap: 12px; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    </style>
  </head>
  <body>
    <main data-view="{teacher_view['id']}">
      <header class="panel">
        <h1>{design["title"]}</h1>
        <p>{design["subtitle"]}</p>
      </header>
      <section class="runtime-shell">
        <section class="panel">
          <canvas id="simulation-canvas" aria-label="simulation viewport"></canvas>
          <div class="controls-row">
            <button type="button" data-action="play">play</button>
            <button type="button" data-action="pause">pause</button>
            <button type="button" data-action="reset">reset</button>
          </div>
          <div class="controls">{control_markup}</div>
        </section>
        <aside class="panel">
          <h2>Teacher View</h2>
          <p>{teacher_view["summary"]}</p>
          <div id="measurement-panel">{measurement_markup}</div>
        </aside>
      </section>
      <section class="panel evidence-grid">
        {chart_markup}
      </section>
    </main>
  </body>
</html>"""
        provider = "openai-configured" if settings.llm_enabled else "deterministic-runtime"
        return {
            "files": {"simulation.html": html},
            "generator_metadata": {"provider": provider, "model": settings.openai_model},
            "primary_file": "simulation.html",
        }
