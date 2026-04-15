import { useEffect, useMemo, useRef, useState } from "react";
import {
  Figure1Payload,
  Figure1Scene,
  Figure1SceneComponent,
  Figure1Simulation,
  Figure1State,
  ImagePreview,
  MechanicsRecognitionPayload,
  RecognitionPayload,
  SceneWire,
  applyFigure1Edit,
  confirmMechanicsProblem,
  confirmRecognizedScene,
  fetchFigure1Scene,
  fetchSamples,
  importSceneBundle,
  recognizeMechanicsProblem,
  recognizeCircuitImage,
  simulateFigure1
} from "./lib/api";

function sliderHandleX(rheostat: Figure1SceneComponent | undefined, ratio: number) {
  if (!rheostat) {
    return 0;
  }
  const left = rheostat.ports.find((port) => port.id === "left");
  const right = rheostat.ports.find((port) => port.id === "right");
  if (!left || !right) {
    return rheostat.x + rheostat.width * ratio;
  }
  return left.x + (right.x - left.x) * ratio;
}

function meterAngle(value: number, maxValue: number) {
  const normalized = Math.min(Math.max(value / Math.max(maxValue, 1e-6), 0), 1);
  return -120 + normalized * 120;
}

function rotatePointer(cx: number, cy: number, angle: number) {
  return `rotate(${angle} ${cx} ${cy})`;
}

function buildPortMap(scene: Figure1Scene) {
  const map = new Map<string, { x: number; y: number }>();
  scene.components.forEach((component) => {
    if (component.type === "junction") {
      map.set(component.id, { x: component.x, y: component.y });
    }
    component.ports.forEach((port) => {
      map.set(`${component.id}.${port.id}`, { x: port.x, y: port.y });
    });
  });
  return map;
}

function getPort(scene: Figure1Scene, ref: string) {
  const map = buildPortMap(scene);
  return map.get(ref);
}

function resolveWirePoints(scene: Figure1Scene, wire: SceneWire) {
  const portMap = buildPortMap(scene);
  return [portMap.get(wire.start_ref), ...wire.bends, portMap.get(wire.end_ref)].filter(
    Boolean
  ) as Array<{ x: number; y: number }>;
}

function renderImagePreview(preview: ImagePreview) {
  if ("svg" in preview && preview.svg) {
    return (
      <div className="reference-preview" dangerouslySetInnerHTML={{ __html: preview.svg }} />
    );
  }
  return (
    <div className="reference-preview">
      <img src={preview.data_url} alt="识别输入" className="uploaded-preview" />
    </div>
  );
}

type StageProps = {
  scene: Figure1Scene;
  state: Figure1State;
  simulation: Figure1Simulation;
  showDebugOverlay: boolean;
  onToggleSwitch: () => void;
  onSliderPointerDown: () => void;
};

function CircuitStage({
  scene,
  state,
  simulation,
  showDebugOverlay,
  onToggleSwitch,
  onSliderPointerDown
}: StageProps) {
  const highlighted = new Set(simulation.visual_state.highlighted_wires);
  const activeComponents = scene.components.filter((component) => component.enabled !== false);
  const resistors = activeComponents.filter((component) => component.type === "resistor");
  const rheostat = activeComponents.find((component) => component.type === "rheostat");
  const battery = activeComponents.find((component) => component.type === "battery");
  const switchComponent = activeComponents.find((component) => component.type === "switch");
  const lamps = activeComponents.filter((component) => component.type === "lamp");
  const ammeters = activeComponents.filter((component) => component.type === "ammeter");
  const voltmeters = activeComponents.filter((component) => component.type === "voltmeter");
  const sliderX = sliderHandleX(rheostat, state.rheostat_ratio);

  const switchPivot = getPort(scene, `${switchComponent?.id ?? "switch"}.pivot`);
  const switchTop = getPort(scene, `${switchComponent?.id ?? "switch"}.top`);
  const switchBottom = getPort(scene, `${switchComponent?.id ?? "switch"}.bottom`);
  const switchOpen = getPort(scene, `${switchComponent?.id ?? "switch"}.open_contact`);
  const switchClosed = getPort(scene, `${switchComponent?.id ?? "switch"}.closed_contact`);
  const batteryLeft = getPort(scene, `${battery?.id ?? "battery"}.left`);
  const batteryRight = getPort(scene, `${battery?.id ?? "battery"}.right`);
  const batteryCenterY = batteryLeft?.y ?? batteryRight?.y ?? (battery?.y ?? 600) + 40;
  const shortOffset = Number(battery?.metadata?.short_plate_offset ?? "42");
  const longOffset = Number(battery?.metadata?.long_plate_offset ?? "82");
  const batteryPlateX1 = (batteryLeft?.x ?? (battery?.x ?? 180)) + shortOffset;
  const batteryPlateX2 = (batteryLeft?.x ?? (battery?.x ?? 180)) + longOffset;

  return (
    <svg
      className="circuit-stage"
      viewBox={`0 0 ${scene.canvas.width} ${scene.canvas.height}`}
      role="img"
      aria-label="电路 simulation 舞台"
    >
      <rect width={scene.canvas.width} height={scene.canvas.height} fill="#fffef9" rx="30" />

      {scene.wires.map((wire) => {
        const points = resolveWirePoints(scene, wire);
        if (points.length < 2) {
          return null;
        }
        return (
          <polyline
            key={wire.id}
            points={points.map((point) => `${point.x},${point.y}`).join(" ")}
            fill="none"
            stroke={highlighted.has(wire.id) ? "#f97316" : "#111827"}
            strokeWidth={highlighted.has(wire.id) ? 8 : 6}
            strokeLinejoin="round"
            strokeLinecap="round"
          />
        );
      })}

      {activeComponents
        .filter((component) => component.type === "junction")
        .map((component) => (
          <circle
            key={component.id}
            cx={component.x}
            cy={component.y}
            r={8}
            fill={simulation.visual_state.energized ? "#f97316" : "#111827"}
          />
        ))}

      {switchComponent ? (
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
          <circle
            cx={switchPivot?.x ?? switchComponent.x + switchComponent.width / 2}
            cy={switchPivot?.y ?? switchComponent.y + switchComponent.height / 2}
            r="14"
            fill="#ffffff"
            stroke="#111827"
            strokeWidth="6"
          />
          <line
            x1={switchBottom?.x ?? switchComponent.x + switchComponent.width / 2}
            y1={switchBottom?.y ?? switchComponent.y + switchComponent.height}
            x2={switchTop?.x ?? switchComponent.x + switchComponent.width / 2}
            y2={switchTop?.y ?? switchComponent.y}
            stroke="#111827"
            strokeWidth="6"
          />
          <line
            x1={(switchPivot?.x ?? switchComponent.x) + 1}
            y1={(switchPivot?.y ?? switchComponent.y) - 13}
            x2={state.switch_closed ? switchClosed?.x ?? switchComponent.x : switchOpen?.x ?? switchComponent.x - 48}
            y2={state.switch_closed ? switchClosed?.y ?? switchComponent.y : switchOpen?.y ?? switchComponent.y + 48}
            stroke={state.switch_closed ? "#f97316" : "#111827"}
            strokeWidth="6"
            strokeLinecap="round"
          />
        </g>
      ) : null}

      {battery ? (
        <g>
          <line
            x1={batteryPlateX1}
            y1={batteryCenterY - 40}
            x2={batteryPlateX1}
            y2={batteryCenterY + 40}
            stroke="#111827"
            strokeWidth="6"
          />
          <line
            x1={batteryPlateX2}
            y1={batteryCenterY - 58}
            x2={batteryPlateX2}
            y2={batteryCenterY + 58}
            stroke="#111827"
            strokeWidth="6"
          />
          <line
            x1={batteryLeft?.x ?? battery.x}
            y1={batteryCenterY}
            x2={batteryPlateX1}
            y2={batteryCenterY}
            stroke="#111827"
            strokeWidth="6"
            strokeLinecap="round"
          />
          <line
            x1={batteryPlateX2}
            y1={batteryCenterY}
            x2={batteryRight?.x ?? battery.x + battery.width}
            y2={batteryCenterY}
            stroke="#111827"
            strokeWidth="6"
            strokeLinecap="round"
          />
        </g>
      ) : null}

      {resistors.map((component) => (
        <g key={component.id}>
          <rect
            x={component.x}
            y={component.y}
            width={component.width}
            height={component.height}
            fill="#ffffff"
            stroke="#111827"
            strokeWidth="6"
          />
          <text x={component.x + component.width / 2 - 8} y={component.y + component.height + 86} className="stage-label stage-label-resistor">
            {component.label ?? "R"}
          </text>
        </g>
      ))}

      {rheostat ? (
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
            y1={rheostat.y - 80}
            x2={sliderX}
            y2={rheostat.y}
            stroke="#111827"
            strokeWidth="6"
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
          <text x={rheostat.x - 26} y={rheostat.y - 34} className="stage-label stage-label-rheostat">
            {rheostat.label ?? "P"}
          </text>
        </g>
      ) : null}

      {lamps.map((component) => (
        <g key={component.id}>
          <circle
            cx={component.x + component.width / 2}
            cy={component.y + component.height / 2}
            r={component.width / 2}
            fill="#ffffff"
            stroke="#111827"
            strokeWidth="6"
          />
          <line
            x1={component.x + component.width * 0.25}
            y1={component.y + component.height * 0.25}
            x2={component.x + component.width * 0.75}
            y2={component.y + component.height * 0.75}
            stroke="#111827"
            strokeWidth="4"
          />
          <line
            x1={component.x + component.width * 0.75}
            y1={component.y + component.height * 0.25}
            x2={component.x + component.width * 0.25}
            y2={component.y + component.height * 0.75}
            stroke="#111827"
            strokeWidth="4"
          />
          <text x={component.x + component.width + 8} y={component.y - 4} className="stage-label">
            {component.label ?? "L"}
          </text>
        </g>
      ))}

      {voltmeters.map((component, index) => (
        <g key={component.id}>
          <circle
            cx={component.x + component.width / 2}
            cy={component.y + component.height / 2}
            r={component.width / 2}
            fill="#ffffff"
            stroke="#111827"
            strokeWidth="8"
          />
          <line
            x1={component.x + component.width / 2}
            y1={component.y + component.height / 2}
            x2={component.x + component.width / 2}
            y2={component.y + 34}
            stroke="#111827"
            strokeWidth="4"
            transform={rotatePointer(
              component.x + component.width / 2,
              component.y + component.height / 2,
              meterAngle(simulation.meter_results.voltmeter, Math.max(state.battery_voltage, 1))
            )}
          />
          <text x={component.x + component.width / 2 - 16} y={component.y + component.height / 2 + 16} className="stage-meter-symbol">
            V
          </text>
          {index === 0 ? (
            <text x={component.x - 6} y={component.y + component.height + 26} className="stage-meter-value">
              {simulation.meter_results.voltmeter.toFixed(2)} V
            </text>
          ) : null}
        </g>
      ))}

      {ammeters.map((component, index) => (
        <g key={component.id}>
          <circle
            cx={component.x + component.width / 2}
            cy={component.y + component.height / 2}
            r={component.width / 2}
            fill="#ffffff"
            stroke="#111827"
            strokeWidth="8"
          />
          <line
            x1={component.x + component.width / 2}
            y1={component.y + component.height / 2}
            x2={component.x + component.width / 2}
            y2={component.y + 30}
            stroke="#111827"
            strokeWidth="4"
            transform={rotatePointer(
              component.x + component.width / 2,
              component.y + component.height / 2,
              meterAngle(simulation.meter_results.ammeter, 1)
            )}
          />
          <text x={component.x + component.width / 2 - 14} y={component.y + component.height / 2 + 14} className="stage-meter-symbol">
            A
          </text>
          {index === 0 ? (
            <text x={component.x - 8} y={component.y + component.height + 26} className="stage-meter-value">
              {simulation.meter_results.ammeter.toFixed(2)} A
            </text>
          ) : null}
        </g>
      ))}

      {showDebugOverlay
        ? activeComponents.flatMap((component) =>
            component.ports.map((port) => (
              <g key={`${component.id}-${port.id}`}>
                <circle cx={port.x} cy={port.y} r={6} fill="#0ea5e9" />
                <text x={port.x + 8} y={port.y - 8} className="debug-label">
                  {component.id}.{port.id}
                </text>
              </g>
            ))
          )
        : null}
    </svg>
  );
}

export function App() {
  const [samples, setSamples] = useState<Array<{ id: string; title: string; status: string }>>([]);
  const [payload, setPayload] = useState<Figure1Payload | null>(null);
  const [scene, setScene] = useState<Figure1Scene | null>(null);
  const [state, setState] = useState<Figure1State | null>(null);
  const [simulation, setSimulation] = useState<Figure1Simulation | null>(null);
  const [pendingRecognition, setPendingRecognition] = useState<RecognitionPayload | null>(null);
  const [mechanicsSession, setMechanicsSession] = useState<MechanicsRecognitionPayload | null>(null);
  const [pendingComponentEdits, setPendingComponentEdits] = useState<Record<string, { id: string; type?: string; value?: number; enabled?: boolean }>>({});
  const [mechanicsProblemText, setMechanicsProblemText] = useState("");
  const [mechanicsSolutionText, setMechanicsSolutionText] = useState("");
  const [mechanicsFinalAnswers, setMechanicsFinalAnswers] = useState("");
  const [mechanicsImage, setMechanicsImage] = useState<File | null>(null);
  const [jsonBundleInput, setJsonBundleInput] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [showDebugOverlay, setShowDebugOverlay] = useState(true);
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
    if (!scene || !state || pendingRecognition) {
      return;
    }
    const handle = window.setTimeout(() => {
      simulateFigure1(scene, state)
        .then((result) => setSimulation(result))
        .catch((reason) => setError(String(reason)));
    }, isDragging ? 30 : 120);
    return () => window.clearTimeout(handle);
  }, [scene, state, isDragging, pendingRecognition]);

  useEffect(() => {
    if (!isDragging || !scene) {
      return;
    }
    const rheostat = scene.components.find((component) => component.type === "rheostat");
    if (!rheostat) {
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

  const onUpload = async (file: File | null) => {
    if (!file) {
      return;
    }
    setError("");
    setPendingComponentEdits({});
    try {
      const result = await recognizeCircuitImage(file);
      setPendingRecognition(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  const applyRecognition = async () => {
    if (!pendingRecognition) {
      return;
    }
    try {
      const updates = {
        component_updates: Object.values(pendingComponentEdits),
        state_updates: [{ key: "switch_closed", value: true }]
      };
      const confirmed = await confirmRecognizedScene(pendingRecognition.session_id, updates);
      setPayload({
        reference_image: pendingRecognition.reference_image,
        scene: confirmed.scene,
        state: confirmed.state,
        simulation: confirmed.simulation
      });
      setScene(confirmed.scene);
      setState(confirmed.state);
      setSimulation(confirmed.simulation);
      setPendingRecognition(null);
      setPendingComponentEdits({});
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  const importJsonBundle = async () => {
    if (!jsonBundleInput.trim()) {
      setError("请先粘贴 JSON。");
      return;
    }
    setError("");
    try {
      const parsed = JSON.parse(jsonBundleInput);
      const imported = await importSceneBundle(parsed.scene ? parsed : { scene: parsed });
      setPayload({
        reference_image: { id: "manual-json-import", svg: "<svg xmlns='http://www.w3.org/2000/svg'></svg>" },
        scene: imported.scene,
        state: imported.state,
        simulation: imported.simulation
      });
      setScene(imported.scene);
      setState(imported.state);
      setSimulation(imported.simulation);
      setPendingRecognition(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  const submitMechanicsProblem = async () => {
    if (!mechanicsProblemText.trim() && !mechanicsImage) {
      setError("请至少提供力学题题干文本或截图。");
      return;
    }
    setError("");
    try {
      const result = await recognizeMechanicsProblem({
        problemText: mechanicsProblemText,
        solutionText: mechanicsSolutionText,
        finalAnswers: mechanicsFinalAnswers,
        imageFile: mechanicsImage
      });
      setMechanicsSession(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  const applyMechanicsSelection = async (modelId: string) => {
    if (!mechanicsSession) {
      return;
    }
    try {
      const result = await confirmMechanicsProblem(mechanicsSession.session_id, {
        selected_model_id: modelId,
        assumption_overrides: modelId === "belt_arc_consistent" ? { belt_reaches_speed: true } : undefined
      });
      setMechanicsSession(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  const currentPreview = pendingRecognition?.reference_image ?? payload?.reference_image;
  const removableComponents = useMemo(
    () => (scene ? scene.components.filter((component) => component.capabilities.removable) : []),
    [scene]
  );

  if (loading) {
    return <main className="loading-shell">正在加载图 1 simulation...</main>;
  }

  if (!scene || !state || !simulation || !payload) {
    return (
      <main className="loading-shell">
        <div>
          <p>页面初始化失败，请确认前后端服务都已启动。</p>
          {error ? <pre className="error-text">{error}</pre> : null}
          <button onClick={() => window.location.reload()}>重试加载</button>
        </div>
      </main>
    );
  }

  return (
    <main className="sim-app">
      <header className="sim-hero">
        <div>
          <p className="sim-kicker">Figure 1 + Recognition V2</p>
          <h1>图 1 闭合修复 + 未知干净电路图识别确认</h1>
          <p className="sim-description">
            舞台连线由端口驱动并做闭合校验；上传未知电路图后先进入确认流程，再应用到可交互 simulation。
          </p>
        </div>
        <div className="sample-summary">
          {samples.map((sample) => (
            <span key={sample.id} className={`sample-tag ${sample.status === "ready" ? "sample-tag-live" : ""}`}>
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
              <p>端口、节点、导线端点可追溯；调试叠加层默认开启便于检查闭合。</p>
            </div>
            <div className="toolbar-actions">
              <label className="debug-toggle">
                <input
                  type="checkbox"
                  checked={showDebugOverlay}
                  onChange={(event) => setShowDebugOverlay(event.target.checked)}
                />
                显示端口
              </label>
              <button onClick={() => setState((current) => current && { ...current, switch_closed: !current.switch_closed })}>
                {state.switch_closed ? "断开开关" : "闭合开关"}
              </button>
            </div>
          </div>
          <div className="stage-wrap" ref={stageWrapRef}>
            <CircuitStage
              scene={scene}
              state={state}
              simulation={simulation}
              showDebugOverlay={showDebugOverlay}
              onToggleSwitch={() => setState((current) => current && { ...current, switch_closed: !current.switch_closed })}
              onSliderPointerDown={() => setIsDragging(true)}
            />
          </div>
        </div>

        <aside className="control-card">
          <section className="control-section">
            <h2>识图上传</h2>
            <label>
              上传干净电路图图片
              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                onChange={(event) => onUpload(event.target.files?.[0] ?? null)}
              />
            </label>
            {pendingRecognition ? (
              <div className="recognition-review">
                <p>
                  识别置信度：<strong>{pendingRecognition.confidence_breakdown.overall.toFixed(2)}</strong>
                </p>
                <p>符号检测：{pendingRecognition.confidence_breakdown.symbol_detection.toFixed(2)}，拓扑重建：{pendingRecognition.confidence_breakdown.topology_reconstruction.toFixed(2)}</p>
                <p>{pendingRecognition.needs_confirmation ? "建议先确认后应用。" : "识别质量较高，可直接应用。"}</p>
                <button onClick={applyRecognition}>确认并应用到舞台</button>
              </div>
            ) : null}
          </section>

          <section className="control-section">
            <h2>力学题双证据校验</h2>
            <label>
              题目截图
              <input
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                onChange={(event) => setMechanicsImage(event.target.files?.[0] ?? null)}
              />
            </label>
            <label>
              题干文本
              <textarea
                rows={6}
                value={mechanicsProblemText}
                onChange={(event) => setMechanicsProblemText(event.target.value)}
                placeholder="粘贴题干文本，首版会优先用文本抽模。"
              />
            </label>
            <label>
              解析文本
              <textarea
                rows={6}
                value={mechanicsSolutionText}
                onChange={(event) => setMechanicsSolutionText(event.target.value)}
                placeholder="粘贴教师解析，用作第二份证据。"
              />
            </label>
            <label>
              参考答案
              <input
                type="text"
                value={mechanicsFinalAnswers}
                onChange={(event) => setMechanicsFinalAnswers(event.target.value)}
                placeholder="例如：4m/s;0.9J;0.2m;3N"
              />
            </label>
            <button onClick={submitMechanicsProblem}>识别并校验力学模型</button>
            {mechanicsSession ? (
              <div className="recognition-review mechanics-review">
                <p>
                  总置信度：<strong>{(mechanicsSession.confidence_breakdown.overall ?? 0).toFixed(2)}</strong>
                </p>
                <p>{mechanicsSession.problem_representation.summary}</p>
                <p>
                  当前模型：<strong>{mechanicsSession.selected_model.title}</strong>
                </p>
                {Object.values(mechanicsSession.simulation.answers).map((answer) => (
                  <p key={answer.key}>
                    {answer.label}：<strong>{answer.display_value}</strong>
                    {answer.expected_value ? ` / 参考 ${answer.expected_value}` : ""}
                  </p>
                ))}
                {mechanicsSession.conflict_items.map((item) => (
                  <p key={item.id} className="error-text">
                    [{item.severity}] {item.message}
                    {item.expected || item.actual
                      ? `（期望 ${item.expected ?? "-"}，当前 ${item.actual ?? "-"}）`
                      : ""}
                  </p>
                ))}
                <div className="mechanics-actions">
                  {mechanicsSession.candidate_models.map((model) => (
                    <button
                      key={model.id}
                      type="button"
                      onClick={() => applyMechanicsSelection(model.id)}
                    >
                      采用 {model.title}
                    </button>
                  ))}
                </div>
                <details className="debug-panel">
                  <summary>展开建模细节</summary>
                  <pre>{JSON.stringify(mechanicsSession, null, 2)}</pre>
                </details>
              </div>
            ) : null}
          </section>

          <section className="control-section">
            <h3>JSON 导入</h3>
            <label>
              粘贴 <code>scene_bundle.json</code>（支持 <code>{"{scene,state}"}</code> 或直接 <code>scene</code>）
              <textarea
                rows={8}
                value={jsonBundleInput}
                onChange={(event) => setJsonBundleInput(event.target.value)}
                placeholder='{"scene": {...}, "state": {...}}'
              />
            </label>
            <button onClick={importJsonBundle}>导入 JSON 并生成 simulation</button>
          </section>

          {pendingRecognition ? (
            <section className="control-section">
              <h3>识别确认</h3>
              {pendingRecognition.issues.map((issue) => (
                <p key={issue.id} className="error-text">
                  [{issue.level}] {issue.message}
                </p>
              ))}
              {pendingRecognition.scene.components
                .filter((component) => component.type !== "junction")
                .slice(0, 10)
                .map((component) => {
                  const patch = pendingComponentEdits[component.id] ?? { id: component.id };
                  return (
                    <div key={component.id} className="toggle-row">
                      <span>{component.label ?? component.id}</span>
                      <select
                        value={patch.type ?? component.type}
                        onChange={(event) =>
                          setPendingComponentEdits((current) => ({
                            ...current,
                            [component.id]: { ...patch, id: component.id, type: event.target.value }
                          }))
                        }
                      >
                        {["battery", "switch", "resistor", "lamp", "ammeter", "voltmeter", "rheostat"].map((item) => (
                          <option key={item} value={item}>
                            {item}
                          </option>
                        ))}
                      </select>
                      <input
                        type="number"
                        step="0.5"
                        value={patch.value ?? component.value ?? 10}
                        onChange={(event) =>
                          setPendingComponentEdits((current) => ({
                            ...current,
                            [component.id]: {
                              ...patch,
                              id: component.id,
                              value: Number(event.target.value)
                            }
                          }))
                        }
                      />
                    </div>
                  );
                })}
            </section>
          ) : null}

          <section className="control-section">
            <h3>当前读数</h3>
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
              <input type="number" min="0" step="0.5" value={state.battery_voltage} onChange={(event) => updateNumber("battery_voltage", event.target.value)} />
            </label>
            <label>
              固定电阻 R
              <input type="number" min="0.1" step="0.5" value={state.resistor_value} onChange={(event) => updateNumber("resistor_value", event.target.value)} />
            </label>
            <label>
              滑变总阻值 P
              <input type="number" min="0.1" step="0.5" value={state.rheostat_total} onChange={(event) => updateNumber("rheostat_total", event.target.value)} />
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
                  setState((current) => (current ? { ...current, rheostat_ratio: Number(event.target.value) } : current))
                }
              />
            </label>
          </section>

          <section className="control-section">
            <h3>元件显隐</h3>
            {removableComponents.map((component) => (
              <label key={component.id} className="toggle-row">
                <span>{component.label ?? component.id}</span>
                <input type="checkbox" checked={component.enabled} onChange={(event) => toggleComponent(component.id, event.target.checked)} />
              </label>
            ))}
          </section>

          <section className="control-section">
            <h3>参考 / 上传预览</h3>
            {currentPreview ? renderImagePreview(currentPreview) : null}
          </section>

          {pendingRecognition ? (
            <details className="debug-panel" open>
              <summary>识别调试信息</summary>
              <pre>{JSON.stringify(pendingRecognition, null, 2)}</pre>
            </details>
          ) : null}

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
