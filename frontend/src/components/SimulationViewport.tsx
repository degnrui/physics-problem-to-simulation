import { useEffect, useMemo, useState } from "react";
import { ForceScenePreview } from "./ForceScenePreview";

interface SimulationViewportProps {
  sceneSpec: Record<string, unknown>;
  simulationSpec: Record<string, unknown> | null;
  rendererPayload: Record<string, unknown> | null;
  deliveryBundle: Record<string, unknown> | null;
}

interface ControlConfig {
  id?: string;
  label?: string;
  min?: number;
  max?: number;
  step?: number;
}

interface TracePoint {
  t: number;
  x: number;
  force: number;
  kinetic: number;
  elastic: number;
  thermal: number;
  total: number;
}

export function SimulationViewport({
  sceneSpec,
  simulationSpec,
  rendererPayload,
  deliveryBundle,
}: SimulationViewportProps) {
  const payloadScene =
    (rendererPayload?.scene_spec as Record<string, unknown> | undefined) ?? sceneSpec;
  const payloadSimulation =
    (rendererPayload?.simulation_spec as Record<string, unknown> | undefined) ?? simulationSpec ?? {};
  const sceneType = typeof payloadScene.scene_type === "string" ? payloadScene.scene_type : "";

  if (sceneType === "elastic-motion") {
    return (
      <ElasticMotionSimulation
        sceneSpec={payloadScene}
        simulationSpec={payloadSimulation}
        deliveryBundle={deliveryBundle ?? {}}
      />
    );
  }

  if (sceneType === "projectile-motion") {
    return (
      <ProjectileSimulation
        sceneSpec={payloadScene}
        simulationSpec={payloadSimulation}
        deliveryBundle={deliveryBundle ?? {}}
      />
    );
  }

  return <ForceScenePreview scene={payloadScene} />;
}

function ElasticMotionSimulation({
  sceneSpec,
  simulationSpec,
  deliveryBundle,
}: {
  sceneSpec: Record<string, unknown>;
  simulationSpec: Record<string, unknown>;
  deliveryBundle: Record<string, unknown>;
}) {
  const controls = (sceneSpec.controls as ControlConfig[] | undefined) ?? [];
  const parameters = (sceneSpec.parameters as Record<string, unknown> | undefined) ?? {};
  const optionAnalysis = (parameters.option_analysis as Record<string, string> | undefined) ?? {};
  const derived = (parameters.derived_quantities as Record<string, string> | undefined) ?? {};
  const teacherScript = (deliveryBundle.teacher_script as string[] | undefined) ?? [];
  const observationTargets =
    (deliveryBundle.observation_targets as string[] | undefined) ?? [];

  const lConfig = controls.find((control) => control.id === "L");
  const muConfig = controls.find((control) => control.id === "mu");

  const [distance, setDistance] = useState(1.25);
  const [mu, setMu] = useState(0.4);
  const [speed, setSpeed] = useState(1);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [showForce, setShowForce] = useState(true);
  const [showVelocity, setShowVelocity] = useState(true);
  const [showEnergy, setShowEnergy] = useState(true);

  const trace = useMemo(() => buildElasticTrace(distance, mu), [distance, mu]);
  const maxTime = trace[trace.length - 1]?.t ?? 0;

  useEffect(() => {
    if (!playing || trace.length === 0) {
      return;
    }

    const timer = window.setInterval(() => {
      setTime((value) => {
        const next = value + 0.04 * speed;
        if (next >= maxTime) {
          setPlaying(false);
          return maxTime;
        }
        return next;
      });
    }, 40);

    return () => window.clearInterval(timer);
  }, [playing, maxTime, speed, trace.length]);

  useEffect(() => {
    setTime(0);
    setPlaying(false);
  }, [distance, mu]);

  const current = useMemo(() => nearestTracePoint(trace, time), [trace, time]);
  const geometry = useMemo(() => buildElasticGeometry(distance, mu, current.x), [distance, mu, current.x]);

  return (
    <section className="panel simulation-lab">
      <div className="simulation-header">
        <div>
          <h2>Simulation Viewport</h2>
          <p className="muted">对称弹力合成、阻尼回复与功能量讲评实验室</p>
        </div>
        <span className="template-badge">
          {String(simulationSpec.template_id ?? sceneSpec.template_id ?? "elastic-restoring-motion-v1")}
        </span>
      </div>

      <div className="lab-layout">
        <div className="lab-left">
          <div className="canvas-container-card">
            <svg viewBox="0 0 640 360" className="elastic-canvas" role="img" aria-label="双橡皮绳阻尼振动仿真">
              <line x1="120" y1="54" x2="120" y2="306" className="axis-line" />
              <circle cx="120" cy="78" r="7" className="anchor-dot" />
              <circle cx="120" cy="282" r="7" className="anchor-dot" />
              <rect x="104" y="162" width="32" height="36" className="center-block" rx="4" />
              <text x="98" y="60" className="canvas-label">A</text>
              <text x="98" y="182" className="canvas-label">C</text>
              <text x="98" y="304" className="canvas-label">B</text>

              <line x1="120" y1="78" x2={geometry.blockX} y2="180" className="band-line" />
              <line x1="120" y1="282" x2={geometry.blockX} y2="180" className="band-line" />
              <line x1="120" y1="180" x2={geometry.originX} y2="180" className="guide-line" />
              <circle cx={geometry.originX} cy="180" r="5" className="origin-dot" />

              <rect x={geometry.blockX - 22} y="158" width="44" height="44" className="moving-block" rx="6" />
              <text x={geometry.originX + 10} y="196" className="canvas-label">O</text>

              {showForce ? (
                <>
                  <line
                    x1={geometry.blockX}
                    y1="180"
                    x2={geometry.blockX - Math.max(40, current.force * 18)}
                    y2="180"
                    className="vector-line restoring-vector"
                  />
                  <line
                    x1={geometry.blockX}
                    y1="180"
                    x2={geometry.blockX + Math.max(18, mu * 70)}
                    y2="180"
                    className="vector-line friction-vector"
                  />
                  <text x={geometry.blockX - 116} y="160" className="vector-label">回复力</text>
                  <text x={geometry.blockX + 12} y="160" className="vector-label">摩擦力</text>
                </>
              ) : null}

              {showVelocity ? (
                <>
                  <line
                    x1={geometry.blockX}
                    y1="214"
                    x2={geometry.blockX + Math.max(0, current.x > 0 ? -current.x * 28 : current.x * -28)}
                    y2="214"
                    className="vector-line velocity-vector"
                  />
                  <text x={geometry.blockX + 12} y="236" className="vector-label">速度</text>
                </>
              ) : null}
            </svg>
          </div>

          <div className="charts-grid">
            <ChartCard title="回复力 vs 位移 (F-x)">
              <SimpleLineChart
                points={trace.map((point) => ({ x: point.x, y: point.force }))}
                currentX={current.x}
                currentY={current.force}
                lineClassName="chart-line force-chart-line"
              />
            </ChartCard>

            <ChartCard title="能量转化 (E-t)">
              <SimpleMultiLineChart
                points={trace}
                currentT={current.t}
                showEnergy={showEnergy}
              />
            </ChartCard>
          </div>
        </div>

        <aside className="lab-right">
          <section className="control-section-card">
            <div className="section-title">播放与回放</div>
            <div className="playback-controls">
              <button type="button" onClick={() => setPlaying((value) => !value)}>
                {playing ? "暂停" : "开始"}
              </button>
              <button type="button" className="secondary-button" onClick={() => { setPlaying(false); setTime(0); }}>
                重置
              </button>
            </div>
            <div className="seek-container">
              <div className="time-display">
                <span>进度 / 回放</span>
                <span>t = {current.t.toFixed(2)} s</span>
              </div>
              <input
                type="range"
                min={0}
                max={maxTime}
                step={0.01}
                value={time}
                onChange={(event) => { setPlaying(false); setTime(Number(event.target.value)); }}
              />
            </div>
            <div className="slider-group">
              <div className="slider-label">
                <span>播放速度</span>
                <span>{speed.toFixed(1)}x</span>
              </div>
              <input type="range" min={0.2} max={3} step={0.1} value={speed} onChange={(event) => setSpeed(Number(event.target.value))} />
            </div>
          </section>

          <section className="control-section-card">
            <div className="section-title">初始设定</div>
            <div className="slider-group">
              <div className="slider-label">
                <span>{lConfig?.label ?? "初始拉开距离 L"}</span>
                <span>{distance.toFixed(2)} m</span>
              </div>
              <input
                type="range"
                min={lConfig?.min ?? 0.2}
                max={lConfig?.max ?? 2.5}
                step={lConfig?.step ?? 0.1}
                value={distance}
                onChange={(event) => setDistance(Number(event.target.value))}
              />
            </div>
            <div className="slider-group">
              <div className="slider-label">
                <span>{muConfig?.label ?? "动摩擦因数 μ"}</span>
                <span>{mu.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min={muConfig?.min ?? 0}
                max={muConfig?.max ?? 0.8}
                step={muConfig?.step ?? 0.05}
                value={mu}
                onChange={(event) => setMu(Number(event.target.value))}
              />
            </div>
          </section>

          <section className="control-section-card">
            <div className="section-title">可视化工具</div>
            <label className="checkbox-label">
              <input type="checkbox" checked={showForce} onChange={() => setShowForce((value) => !value)} />
              显示合回复力
            </label>
            <label className="checkbox-label">
              <input type="checkbox" checked={showVelocity} onChange={() => setShowVelocity((value) => !value)} />
              显示速度
            </label>
            <label className="checkbox-label">
              <input type="checkbox" checked={showEnergy} onChange={() => setShowEnergy((value) => !value)} />
              验证能量变化
            </label>
          </section>

          <section className="control-section-card">
            <div className="section-title">教学焦点</div>
            <p className="muted">回复力约与 `2Fcosθ` 对应，位置越远，沿 CO 指向 C 的合力越明显。</p>
            <p className="muted">机械能会因摩擦逐步减少，因此不是简谐运动。</p>
            {observationTargets.length > 0 ? (
              <ul className="plain-list">
                {observationTargets.map((target) => (
                  <li key={target}>{target}</li>
                ))}
              </ul>
            ) : null}
          </section>

          <section className="control-section-card">
            <div className="section-title">关键关系</div>
            <ul className="plain-list">
              {Object.entries(derived).map(([key, value]) => (
                <li key={key}>
                  <strong>{key}</strong> {value}
                </li>
              ))}
            </ul>
          </section>

          <section className="control-section-card">
            <div className="section-title">选项辨析</div>
            <div className="option-grid">
              {Object.entries(optionAnalysis).map(([option, result]) => (
                <div className="option-pill" key={option}>
                  <strong>{option}</strong>
                  <span>{result}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="control-section-card">
            <div className="section-title">教师脚本</div>
            <ul className="plain-list">
              {teacherScript.map((line, index) => (
                <li key={`${index}-${line}`}>{line}</li>
              ))}
            </ul>
          </section>
        </aside>
      </div>
    </section>
  );
}

function ProjectileSimulation({
  sceneSpec,
  simulationSpec,
  deliveryBundle,
}: {
  sceneSpec: Record<string, unknown>;
  simulationSpec: Record<string, unknown>;
  deliveryBundle: Record<string, unknown>;
}) {
  const parameters = (sceneSpec.parameters as Record<string, unknown> | undefined) ?? {};
  const derived = (parameters.derived_quantities as Record<string, string> | undefined) ?? {};
  const optionAnalysis = (parameters.option_analysis as Record<string, string> | undefined) ?? {};
  const teacherScript = (deliveryBundle.teacher_script as string[] | undefined) ?? [];
  const [height, setHeight] = useState(1.2);
  const t = Math.sqrt((2 * height) / 9.8);
  const vx = 1.8;
  const x = vx * t;
  const vy = 9.8 * t;
  const angle = Math.atan(vy / vx) * 180 / Math.PI;

  return (
    <section className="panel simulation-lab">
      <div className="simulation-header">
        <div>
          <h2>Simulation Viewport</h2>
          <p className="muted">平抛轨迹与击板速度方向演示</p>
        </div>
        <span className="template-badge">
          {String(simulationSpec.template_id ?? sceneSpec.template_id ?? "projectile-board-impact-v1")}
        </span>
      </div>

      <div className="lab-layout">
        <div className="lab-left">
          <div className="canvas-container-card projectile-board-card">
            <div className="projectile-stage">
              <div className="projectile-ramp" />
              <div className="projectile-table" />
              <div className="projectile-ball" />
              <div className="projectile-board" style={{ transform: `translateY(${height * 24}px)` }} />
              <div className="projectile-arc" />
            </div>
          </div>
          <div className="charts-grid">
            <ChartCard title="飞行时间 / 水平距离">
              <div className="metric-stack">
                <p>飞行时间 t = {t.toFixed(2)} s</p>
                <p>水平距离 x = {x.toFixed(2)} m</p>
                <p>竖直分速度 vy = {vy.toFixed(2)} m/s</p>
                <p>撞击方向角 = {angle.toFixed(1)}°</p>
              </div>
            </ChartCard>
            <ChartCard title="关键关系">
              <ul className="plain-list">
                {Object.entries(derived).map(([key, value]) => (
                  <li key={key}>
                    <strong>{key}</strong> {value}
                  </li>
                ))}
              </ul>
            </ChartCard>
          </div>
        </div>

        <aside className="lab-right">
          <section className="control-section-card">
            <div className="section-title">参数控制</div>
            <div className="slider-group">
              <div className="slider-label">
                <span>木板高度 h</span>
                <span>{height.toFixed(2)} m</span>
              </div>
              <input type="range" min={0.2} max={2.5} step={0.1} value={height} onChange={(event) => setHeight(Number(event.target.value))} />
            </div>
          </section>
          <section className="control-section-card">
            <div className="section-title">选项辨析</div>
            <div className="option-grid">
              {Object.entries(optionAnalysis).map(([option, result]) => (
                <div className="option-pill" key={option}>
                  <strong>{option}</strong>
                  <span>{result}</span>
                </div>
              ))}
            </div>
          </section>
          <section className="control-section-card">
            <div className="section-title">教师脚本</div>
            <ul className="plain-list">
              {teacherScript.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </section>
        </aside>
      </div>
    </section>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="chart-card">
      <div className="chart-title">{title}</div>
      <div className="chart-inner">{children}</div>
    </div>
  );
}

function SimpleLineChart({
  points,
  currentX,
  currentY,
  lineClassName,
}: {
  points: Array<{ x: number; y: number }>;
  currentX: number;
  currentY: number;
  lineClassName: string;
}) {
  const width = 320;
  const height = 200;
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const polyline = points
    .map((point) => `${scale(point.x, minX, maxX, 30, width - 20)},${scale(point.y, minY, maxY, height - 20, 20)}`)
    .join(" ");
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="chart-svg">
      <line x1="30" y1={height - 20} x2={width - 20} y2={height - 20} className="chart-axis" />
      <line x1="30" y1="20" x2="30" y2={height - 20} className="chart-axis" />
      <polyline fill="none" points={polyline} className={lineClassName} />
      <circle
        cx={scale(currentX, minX, maxX, 30, width - 20)}
        cy={scale(currentY, minY, maxY, height - 20, 20)}
        r="5"
        className="chart-marker"
      />
    </svg>
  );
}

function SimpleMultiLineChart({
  points,
  currentT,
  showEnergy,
}: {
  points: TracePoint[];
  currentT: number;
  showEnergy: boolean;
}) {
  const width = 320;
  const height = 200;
  const minT = 0;
  const maxT = points[points.length - 1]?.t ?? 1;
  const energyValues = points.flatMap((point) => [point.elastic, point.kinetic, point.thermal, point.total]);
  const minE = 0;
  const maxE = Math.max(...energyValues, 1);

  const buildPolyline = (selector: (point: TracePoint) => number) =>
    points
      .map((point) => `${scale(point.t, minT, maxT, 30, width - 20)},${scale(selector(point), minE, maxE, height - 20, 20)}`)
      .join(" ");

  const current = nearestTracePoint(points, currentT);

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="chart-svg">
      <line x1="30" y1={height - 20} x2={width - 20} y2={height - 20} className="chart-axis" />
      <line x1="30" y1="20" x2="30" y2={height - 20} className="chart-axis" />
      <polyline fill="none" points={buildPolyline((point) => point.elastic)} className="chart-line elastic-chart-line" />
      <polyline fill="none" points={buildPolyline((point) => point.kinetic)} className="chart-line kinetic-chart-line" />
      <polyline fill="none" points={buildPolyline((point) => point.thermal)} className="chart-line thermal-chart-line" />
      {showEnergy ? (
        <polyline fill="none" points={buildPolyline((point) => point.total)} className="chart-line total-chart-line" />
      ) : null}
      <circle
        cx={scale(current.t, minT, maxT, 30, width - 20)}
        cy={scale(current.total, minE, maxE, height - 20, 20)}
        r="5"
        className="chart-marker"
      />
    </svg>
  );
}

function buildElasticTrace(distance: number, mu: number): TracePoint[] {
  const amplitude = distance;
  const damping = 0.12 + mu * 0.55;
  const omega = 2.2;
  const samples: TracePoint[] = [];
  const totalEnergy = 0.9 * amplitude * amplitude + 0.8;

  for (let step = 0; step <= 320; step += 1) {
    const t = step * 0.025;
    const envelope = Math.exp(-damping * t);
    const x = amplitude * envelope * Math.cos(omega * t);
    const v = amplitude * envelope * (-omega * Math.sin(omega * t) - damping * Math.cos(omega * t));
    const force = Math.abs(x) * 1.8;
    const kinetic = Math.max(0, 0.5 * v * v);
    const elastic = Math.max(0, 0.9 * x * x);
    const stored = kinetic + elastic;
    const thermal = Math.max(0, totalEnergy - stored);
    samples.push({
      t,
      x,
      force,
      kinetic,
      elastic,
      thermal,
      total: totalEnergy,
    });
  }

  return samples;
}

function buildElasticGeometry(distance: number, mu: number, x: number) {
  const normalized = Math.max(0.16, Math.min(0.88, distance / 2.5));
  const originX = 120 + normalized * 210;
  const displacementRatio = distance === 0 ? 0 : x / distance;
  const blockX = 120 + normalized * 210 + displacementRatio * 170;
  const dampingRatio = Math.min(1, mu / 0.8);
  return {
    originX,
    blockX,
    dampingRatio,
  };
}

function nearestTracePoint(trace: TracePoint[], time: number): TracePoint {
  return (
    trace.reduce((closest, point) => {
      return Math.abs(point.t - time) < Math.abs(closest.t - time) ? point : closest;
    }, trace[0]) ?? {
      t: 0,
      x: 0,
      force: 0,
      kinetic: 0,
      elastic: 0,
      thermal: 0,
      total: 0,
    }
  );
}

function scale(value: number, inMin: number, inMax: number, outMin: number, outMax: number) {
  if (inMax - inMin === 0) {
    return (outMin + outMax) / 2;
  }
  const ratio = (value - inMin) / (inMax - inMin);
  return outMin + ratio * (outMax - outMin);
}
