import json
from pathlib import Path
from typing import Any, Dict


def render_export_html(final_package: Dict[str, Any]) -> str:
    compile_delivery = final_package.get("compile_delivery", {})
    payload = {
        "run_profiling": final_package.get("run_profiling"),
        "structured_task_model": final_package.get("structured_task_model"),
        "physics_model": final_package.get("physics_model"),
        "simulation_spec_generation": final_package.get("simulation_spec_generation"),
        "compile_delivery": compile_delivery,
        "final_validation": final_package.get("final_validation"),
    }
    boot = json.dumps(payload, ensure_ascii=False)
    title = "Physics Problem to Simulation Export"
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>
      :root {{
        color-scheme: light;
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        --bg: #f4f2eb;
        --panel: rgba(255, 255, 255, 0.86);
        --line: #d7dcea;
        --text: #203047;
        --muted: #5d6a7e;
        --brand: #244f7b;
        --soft: #eef4fb;
      }}
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; background: linear-gradient(180deg, #faf8f0 0%, #eef4fb 100%); color: var(--text); }}
      .shell {{ max-width: 1280px; margin: 0 auto; padding: 32px 20px 48px; display: grid; gap: 20px; }}
      .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 24px; padding: 20px; box-shadow: 0 18px 44px rgba(42,59,87,0.08); }}
      h1, h2, h3 {{ margin: 0; }}
      p {{ line-height: 1.7; }}
      .header {{ display: flex; justify-content: space-between; gap: 16px; align-items: start; }}
      .badge {{ padding: 8px 12px; border-radius: 999px; background: var(--soft); color: var(--brand); font-weight: 700; font-size: 12px; }}
      .grid {{ display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.9fr); gap: 18px; }}
      .card-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }}
      .card {{ border: 1px solid var(--line); border-radius: 18px; padding: 14px; background: #fff; }}
      .list {{ margin: 0; padding-left: 18px; }}
      .code {{ white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 13px; background: #fbfcfe; border: 1px solid var(--line); border-radius: 16px; padding: 14px; }}
    </style>
  </head>
  <body>
    <div class="shell">
      <section class="panel">
        <div class="header">
          <div>
            <p style="margin:0;color:var(--muted);text-transform:uppercase;letter-spacing:.12em;font-size:12px;">Offline Export</p>
            <h1>Physics Problem to Simulation</h1>
            <p id="subtitle"></p>
          </div>
          <span class="badge" id="componentKey"></span>
        </div>
      </section>
      <section class="grid">
        <div class="panel">
          <h2>Simulation Contract</h2>
          <div class="card-grid" id="summaryCards"></div>
          <h3 style="margin-top:16px;">Required Panels</h3>
          <ul class="list" id="panelList"></ul>
        </div>
        <div class="panel">
          <h2>Teacher Guidance</h2>
          <ul class="list" id="teacherScript"></ul>
          <h3 style="margin-top:16px;">Observation Targets</h3>
          <ul class="list" id="observationTargets"></ul>
        </div>
      </section>
      <section class="panel">
        <h2>Simulation Payload</h2>
        <div class="code" id="payload"></div>
      </section>
    </div>
    <script>
      const data = {boot};
      const compileDelivery = data.compile_delivery || {{}};
      const rendererPayload = compileDelivery.renderer_payload || {{}};
      const deliveryBundle = compileDelivery.delivery_bundle || {{}};
      const simulationBlueprint = compileDelivery.simulation_blueprint || {{}};
      const specGeneration = data.simulation_spec_generation || {{}};
      const simulationSpec = specGeneration.simulation_spec || {{}};
      const sceneSpec = specGeneration.scene_spec || {{}};
      const finalValidation = data.final_validation || {{}};
      document.getElementById("subtitle").textContent =
        (rendererPayload.hero_panel && rendererPayload.hero_panel.subtitle) ||
        "把物理题转成可讲授、可演示、可验证的教学 simulation 成品。";
      document.getElementById("componentKey").textContent =
        rendererPayload.component_key || "simulation-export";
      const cards = [
        ["Scene", sceneSpec.scene_type || "unknown"],
        ["Template", simulationSpec.template_id || sceneSpec.template_id || "unknown"],
        ["Renderer", rendererPayload.component_key || simulationSpec.renderer_mode || "unknown"],
        ["Export", (deliveryBundle.export_mode || "single-file-html")],
        ["Score", String(finalValidation.score || "--")],
      ];
      document.getElementById("summaryCards").innerHTML = cards
        .map(([label, value]) => `<div class="card"><strong>${{label}}</strong><p>${{value}}</p></div>`)
        .join("");
      document.getElementById("panelList").innerHTML = Object.entries(deliveryBundle.panel_contract || {{}})
        .map(([key, value]) => `<li><strong>${{key}}</strong> - ${{Array.isArray(value.content) ? value.content.join(", ") : value.content || ""}}</li>`)
        .join("");
      document.getElementById("teacherScript").innerHTML = (deliveryBundle.teacher_script || [])
        .map((item) => `<li>${{item}}</li>`)
        .join("");
      document.getElementById("observationTargets").innerHTML = (deliveryBundle.observation_targets || [])
        .map((item) => `<li>${{item}}</li>`)
        .join("");
      document.getElementById("payload").textContent = JSON.stringify(
        {{
          simulationBlueprint,
          sceneSpec,
          simulationSpec,
          finalValidation,
          raw: data,
        }},
        null,
        2,
      );
    </script>
  </body>
</html>
"""


def write_export_html(exports_dir: Path, final_package: Dict[str, Any]) -> Path:
    exports_dir.mkdir(parents=True, exist_ok=True)
    path = exports_dir / "simulation.html"
    path.write_text(render_export_html(final_package), encoding="utf-8")
    return path
