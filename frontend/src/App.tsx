import { useEffect, useRef, useState } from "react";
import {
  Figure1Payload,
  Figure1Scene,
  Figure1SceneComponent,
  Figure1State,
  Figure1Simulation,
  applyFigure1Edit,
  fetchFigure1Scene,
  fetchSamples,
  simulateFigure1
} from "./lib/api";

function sliderHandleX(rheostat: Figure1SceneComponent, ratio: number) {
  return rheostat.x + rheostat.width * ratio;
}

function meterAngle(value: number, maxValue: number) {
  const normalized = Math.min(Math.max(value / maxValue, 0), 1);
  return -120 + normalized * 120;
}

function rotatePointer(cx: number, cy: number, angle: number) {
  return `rotate(${angle} ${cx} ${cy})`;
}

type StageProps = {
  scene: Figure1Scene;
  state: Figure1State;
  simulation: Figure1Simulation;
  onToggleSwitch: () => void;
  onSliderPointerDown: () => void;
};

function CircuitStage({
  scene,
  state,
  simulation,
  onToggleSwitch,
  onSliderPointerDown
}: StageProps) {
  const componentMap = Object.fromEntries(
    scene.components.map((component) => [component.id, component])
  ) as Record<string, Figure1SceneComponent>;
  const highlighted = new Set(simulation.visual_state.highlighted_wires);
  const rheostat = componentMap.rheostat;
  const sliderX = sliderHandleX(rheostat, state.rheostat_ratio);
  const ammeter = componentMap.ammeter;
  const voltmeter = componentMap.voltmeter;
  const ammeterValue = simulation.meter_results.ammeter;
  const voltmeterValue = simulation.meter_results.voltmeter;

  return (
    <svg
      className="circuit-stage"
      viewBox={`0 0 ${scene.canvas.width} ${scene.canvas.height}`}
      role="img"
      aria-label="图 1 复刻式电路 simulation"
    >
      <rect width={scene.canvas.width} height={scene.canvas.height} fill="#fffef9" rx="30" />

      {scene.wires
        .filter((wire) => wire.role !== "pointer")
        .map((wire) => (
          <polyline
            key={wire.id}
            points={wire.points.map((point) => `${point.x},${point.y}`).join(" ")}
            fill="none"
            stroke={highlighted.has(wire.id) ? "#f97316" : "#111827"}
            strokeWidth={highlighted.has(wire.id) ? 8 : 6}
            strokeLinejoin="round"
            strokeLinecap="round"
          />
        ))}

      {scene.components
        .filter((component) => component.type === "junction")
        .map((component) => (
          <circle
            key={component.id}
            cx={component.x}
            cy={component.y}
            r={11}
            fill={simulation.visual_state.energized ? "#f97316" : "#111827"}
          />
        ))}

      <g
        className="switch-hitbox"
        onClick={onToggleSwitch}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            onToggleSwitch();
          }
        }}
      >
        <circle cx="92" cy="360" r="14" fill="#ffffff" stroke="#111827" strokeWidth="6" />
        <line x1="92" y1="373" x2="92" y2="305" stroke="#111827" strokeWidth="6" />
        <line
          x1="92"
          y1="347"
          x2={state.switch_closed ? 92 : 32}
          y2={state.switch_closed ? 470 : 470}
          stroke={state.switch_closed ? "#f97316" : "#111827"}
          strokeWidth="6"
          strokeLinecap="round"
        />
      </g>

      <g>
        <line x1="166" y1="598" x2="166" y2="678" stroke="#111827" strokeWidth="6" />
        <line x1="197" y1="580" x2="197" y2="696" stroke="#111827" strokeWidth="6" />
      </g>

      <g>
        <rect
          x={componentMap.resistor.x}
          y={componentMap.resistor.y}
          width={componentMap.resistor.width}
          height={componentMap.resistor.height}
          fill="#ffffff"
          stroke="#111827"
          strokeWidth="6"
        />
        <text x="505" y="396" className="stage-label stage-label-resistor">
          R
        </text>
      </g>

      <g>
        <rect
          x={rheostat.x}
          y={rheostat.y}
          width={rheostat.width}
          height={rheostat.height}
          fill="#ffffff"
          stroke="#111827"
          strokeWidth="6"
        />
        <line
          x1={sliderX}
          y1="540"
          x2={sliderX}
          y2={rheostat.y}
          stroke="#111827"
          strokeWidth="6"
        />
        <path
          d={`M ${sliderX} ${rheostat.y} L ${sliderX - 18} ${rheostat.y - 42}`}
          fill="none"
          stroke="#111827"
          strokeWidth="6"
          strokeLinecap="round"
        />
        <circle
          className="slider-handle"
          cx={sliderX}
          cy={rheostat.y - 18}
          r="16"
          fill="#f97316"
          stroke="#111827"
          strokeWidth="4"
          onPointerDown={onSliderPointerDown}
        />
        <text x="364" y="598" className="stage-label stage-label-rheostat">
          P
        </text>
      </g>

      {componentMap.voltmeter.enabled ? (
        <g>
          <circle
            cx={voltmeter.x + voltmeter.width / 2}
            cy={voltmeter.y + voltmeter.height / 2}
            r={voltmeter.width / 2}
            fill="#ffffff"
            stroke="#111827"
            strokeWidth="8"
          />
          <line
            x1={voltmeter.x + voltmeter.width / 2}
            y1={voltmeter.y + voltmeter.height / 2}
            x2={voltmeter.x + voltmeter.width / 2}
            y2={voltmeter.y + 34}
            stroke="#111827"
            strokeWidth="4"
            transform={rotatePointer(
              voltmeter.x + voltmeter.width / 2,
              voltmeter.y + voltmeter.height / 2,
              meterAngle(voltmeterValue, state.battery_voltage || 1)
            )}
          />
          <text x="528" y="158" className="stage-meter-symbol">
            V
          </text>
          <text x="522" y="214" className="stage-meter-value">
            {voltmeterValue.toFixed(2)} V
          </text>
        </g>
      ) : null}

      {componentMap.ammeter.enabled ? (
        <g>
          <circle
            cx={ammeter.x + ammeter.width / 2}
            cy={ammeter.y + ammeter.height / 2}
            r={ammeter.width / 2}
            fill="#ffffff"
            stroke="#111827"
            strokeWidth="8"
          />
          <line
            x1={ammeter.x + ammeter.width / 2}
            y1={ammeter.y + ammeter.height / 2}
            x2={ammeter.x + ammeter.width / 2}
            y2={ammeter.y + 30}
            stroke="#111827"
            strokeWidth="4"
            transform={rotatePointer(
              ammeter.x + ammeter.width / 2,
              ammeter.y + ammeter.height / 2,
              meterAngle(ammeterValue, 1)
            )}
          />
          <text x="719" y="484" className="stage-meter-symbol">
            A
          </text>
          <text x="702" y="536" className="stage-meter-value">
            {ammeterValue.toFixed(2)} A
          </text>
        </g>
      ) : null}
    </svg>
  );
}

export function App() {
  const [samples, setSamples] = useState<Array<{ id: string; title: string; status: string }>>([]);
  const [payload, setPayload] = useState<Figure1Payload | null>(null);
  const [scene, setScene] = useState<Figure1Scene | null>(null);
  const [state, setState] = useState<Figure1State | null>(null);
  const [simulation, setSimulation] = useState<Figure1Simulation | null>(null);
  const [loading, setLoading] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string>("");
  const stageWrapRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    fetchSamples().then(setSamples);
    fetchFigure1Scene()
      .then((result) => {
        setPayload(result);
        setScene(result.scene);
        setState(result.state);
        setSimulation(result.simulation);
      })
      .catch((reason) => {
        setError(String(reason));
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!scene || !state) {
      return;
    }
    const handle = window.setTimeout(() => {
      simulateFigure1(scene, state)
        .then((result) => setSimulation(result))
        .catch((reason) => setError(String(reason)));
    }, isDragging ? 30 : 120);
    return () => window.clearTimeout(handle);
  }, [scene, state, isDragging]);

  useEffect(() => {
    if (!isDragging || !scene) {
      return;
    }
    const move = (event: PointerEvent) => {
      const wrap = stageWrapRef.current;
      if (!wrap) {
        return;
      }
      const svg = wrap.querySelector("svg");
      if (!svg) {
        return;
      }
      const bounds = svg.getBoundingClientRect();
      const ratio = Math.min(Math.max((event.clientX - bounds.left) / bounds.width, 0), 1);
      setState((current) => (current ? { ...current, rheostat_ratio: ratio } : current));
    };
    const up = () => setIsDragging(false);
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, [isDragging, scene]);

  const updateNumber = (field: keyof Figure1State, value: string) => {
    const numeric = Number(value);
    setState((current) => (current ? { ...current, [field]: numeric } : current));
  };

  const toggleComponent = async (componentId: string, enabled: boolean) => {
    if (!scene || !state) {
      return;
    }
    const result = await applyFigure1Edit(scene, state, {
      action: enabled ? "restore_component" : "remove_component",
      component_id: componentId
    });
    setScene(result.scene);
    setState(result.state);
    setSimulation(result.simulation);
  };

  if (loading || !scene || !state || !simulation || !payload) {
    return <main className="loading-shell">正在加载图 1 simulation...</main>;
  }

  const removableComponents = scene.components.filter(
    (component) => component.capabilities.removable
  );

  return (
    <main className="sim-app">
      <header className="sim-hero">
        <div>
          <p className="sim-kicker">Figure 1 Simulation</p>
          <h1>图 1 复刻式交互电路</h1>
          <p className="sim-description">
            点击开关、拖动滑片、修改电源与电阻参数，电流表和电压表会在图上实时显示数值。
          </p>
        </div>
        <div className="sample-summary">
          {samples.map((sample) => (
            <span
              key={sample.id}
              className={`sample-tag ${sample.status === "ready" ? "sample-tag-live" : ""}`}
            >
              {sample.title}
            </span>
          ))}
        </div>
      </header>

      <section className="sim-layout">
        <div className="stage-card">
          <div className="stage-toolbar">
            <div>
              <h2>电路舞台</h2>
              <p>布局按照图 1 复刻，主交互直接发生在电路图上。</p>
            </div>
            <button onClick={() => setState((current) => current && { ...current, switch_closed: !current.switch_closed })}>
              {state.switch_closed ? "断开开关" : "闭合开关"}
            </button>
          </div>
          <div className="stage-wrap" ref={stageWrapRef}>
            <CircuitStage
              scene={scene}
              state={state}
              simulation={simulation}
              onToggleSwitch={() =>
                setState((current) => current && { ...current, switch_closed: !current.switch_closed })
              }
              onSliderPointerDown={() => setIsDragging(true)}
            />
          </div>
        </div>

        <aside className="control-card">
          <section className="control-section">
            <h2>控制面板</h2>
            <div className="metric-grid">
              <div className="metric">
                <span>电流表 A</span>
                <strong>{simulation.meter_results.ammeter.toFixed(2)} A</strong>
              </div>
              <div className="metric">
                <span>电压表 V</span>
                <strong>{simulation.meter_results.voltmeter.toFixed(2)} V</strong>
              </div>
            </div>
          </section>

          <section className="control-section">
            <h3>数值调节</h3>
            <label>
              电源电压
              <input
                type="number"
                min="0"
                step="0.5"
                value={state.battery_voltage}
                onChange={(event) => updateNumber("battery_voltage", event.target.value)}
              />
            </label>
            <label>
              固定电阻 R
              <input
                type="number"
                min="0.1"
                step="0.5"
                value={state.resistor_value}
                onChange={(event) => updateNumber("resistor_value", event.target.value)}
              />
            </label>
            <label>
              滑变总阻值 P
              <input
                type="number"
                min="0.1"
                step="0.5"
                value={state.rheostat_total}
                onChange={(event) => updateNumber("rheostat_total", event.target.value)}
              />
            </label>
            <label>
              滑片位置
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={state.rheostat_ratio}
                onChange={(event) =>
                  setState((current) =>
                    current ? { ...current, rheostat_ratio: Number(event.target.value) } : current
                  )
                }
              />
            </label>
          </section>

          <section className="control-section">
            <h3>元件显隐</h3>
            {removableComponents.map((component) => (
              <label key={component.id} className="toggle-row">
                <span>{component.label ?? component.id}</span>
                <input
                  type="checkbox"
                  checked={component.enabled}
                  onChange={(event) => toggleComponent(component.id, event.target.checked)}
                />
              </label>
            ))}
          </section>

          <section className="control-section">
            <h3>原图参考</h3>
            <div
              className="reference-preview"
              dangerouslySetInnerHTML={{ __html: payload.reference_image.svg }}
            />
          </section>

          <details className="debug-panel">
            <summary>调试信息</summary>
            <pre>{JSON.stringify({ state, simulation }, null, 2)}</pre>
          </details>

          {error ? <p className="error-text">{error}</p> : null}
        </aside>
      </section>
    </main>
  );
}
