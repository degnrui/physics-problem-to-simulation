import { useEffect, useMemo, useRef, useState } from "react";
import {
  MechanicsRecognitionPayload,
  MechanicsRuntimePayload,
  MechanicsScenePayload,
  confirmMechanicsProblem,
  generateMechanicsScene,
  recognizeMechanicsProblem,
  simulateMechanicsScene
} from "./lib/api";

const SAMPLE_PROBLEM = `17. 某兴趣小组设计了一个传送装置，AB是倾角为30°的斜轨道，BC是以恒定速率v0顺时针转动的水平传送带，靠近C端有半径为R、质量为M置于光滑水平面上的可动半圆弧轨道。现有一质量为m的物块，从AB上距B点L的P点由静止下滑，经传送带末端C点滑入圆弧轨道。物块与传送带间的动摩擦因数为μ，其余接触面均光滑。已知R=0.36m，L=1.6m，v0=5m/s，m=0.2kg，M=1.8kg，μ=0.25。求物块滑到B点处的速度大小、从B运动到C过程中摩擦力对其做的功、在传送带上滑动过程中产生的滑痕长度、即将离开圆弧轨道最高点的瞬间受到轨道的压力大小。`;

const SAMPLE_SOLUTION = `滑块由P点到B点由动能定理得 mgsin30°L = 1/2 mv^2，解得 v=4m/s。物块滑上传送带后做匀加速运动直至与传送带共速，摩擦力对其做功 Wf = 1/2 mv0^2 - 1/2 mv^2 = 0.9J。加速度为 a=μg=2.5m/s^2，加速时间 t=(v0-v)/a=0.4s，滑痕长度 Δx=v0 t - (v0+v)t/2 = 0.2m。物块开始进入圆弧轨道到到达即将最高点由水平方向动量守恒和机械能守恒可知，1/2 mv0^2 = 1/2 mv1^2 + 1/2 Mv2^2 + 2mgR，解得 v1=0.8m/s。对滑块在最高点由牛顿第二定律得 F+mg = m(v1-v2)^2/R，解得 F=3N。`;

const SAMPLE_ANSWERS = "4m/s;0.9J;0.2m;3N";

function stageEmoji(stageId: string) {
  switch (stageId) {
    case "slope":
      return "A";
    case "belt":
      return "B";
    case "arc_entry":
      return "C";
    case "arc_top":
      return "D";
    default:
      return "·";
  }
}

function chartPath(points: Array<{ x: number; y: number }>, width: number, height: number) {
  if (points.length === 0) {
    return "";
  }
  const xMin = Math.min(...points.map((point) => point.x));
  const xMax = Math.max(...points.map((point) => point.x));
  const yMin = Math.min(...points.map((point) => point.y));
  const yMax = Math.max(...points.map((point) => point.y));
  return points
    .map((point, index) => {
      const x = ((point.x - xMin) / Math.max(xMax - xMin, 1e-6)) * width;
      const y = height - ((point.y - yMin) / Math.max(yMax - yMin, 1e-6)) * height;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

function TeachingScene({
  scene,
  runtime
}: {
  scene: MechanicsScenePayload["scene"];
  runtime: MechanicsRuntimePayload | null;
}) {
  const block = runtime?.frame.actors.block;
  const belt = runtime?.frame.actors.belt;
  const arc = runtime?.frame.actors.arc;
  const overlayEntries = Object.entries(runtime?.frame.overlays ?? {});
  const currentStage = runtime?.stage.id ?? scene.stages[0]?.id;

  return (
    <div className="theater-shell">
      <div className="theater-caption">
        <div>
          <p className="panel-kicker">Teaching Simulation</p>
          <h2>{scene.title}</h2>
        </div>
        <div className="overlay-pills">
          {overlayEntries.slice(0, 3).map(([key, value]) => (
            <span key={key}>{String(value)}</span>
          ))}
        </div>
      </div>
      <svg className="teaching-canvas" viewBox={`0 0 ${scene.canvas.width} ${scene.canvas.height}`}>
        <defs>
          <linearGradient id="deckGlow" x1="0%" x2="100%">
            <stop offset="0%" stopColor="#ffecd1" />
            <stop offset="100%" stopColor="#ffd166" />
          </linearGradient>
          <linearGradient id="arcGlow" x1="0%" x2="100%">
            <stop offset="0%" stopColor="#0f766e" />
            <stop offset="100%" stopColor="#5eead4" />
          </linearGradient>
        </defs>
        <rect width={scene.canvas.width} height={scene.canvas.height} rx="36" fill="#fffdf7" />
        <path d="M 76 146 L 332 286" stroke={currentStage === "slope" ? "#d1495b" : "#111827"} strokeWidth="8" fill="none" strokeLinecap="round" />
        <rect x="332" y="286" width="324" height="42" rx="20" fill="url(#deckGlow)" stroke="#111827" strokeWidth="6" />
        <path d="M 796 286 A 122 122 0 0 1 796 42" stroke="url(#arcGlow)" strokeWidth="8" fill="none" strokeLinecap="round" />
        <circle
          cx={Number(block?.x ?? 84)}
          cy={Number(block?.y ?? 152)}
          r="18"
          fill="#d1495b"
          stroke="#111827"
          strokeWidth="4"
        />
        <circle cx={796} cy={286} r="7" fill="#0f766e" />
        <circle cx={Number(arc?.cx ?? 796)} cy="286" r="12" fill="#0f766e" opacity="0.18" />
        <text x="110" y="130" className="canvas-label">AB</text>
        <text x="470" y="274" className="canvas-label">BC</text>
        <text x="828" y="126" className="canvas-label">R</text>
        <text x="394" y="354" className="canvas-metric">
          传送带偏移 {Number(belt?.offset ?? 0).toFixed(1)}
        </text>
        {currentStage === "arc_top" ? (
          <>
            <line x1="796" y1="164" x2="796" y2="104" stroke="#2563eb" strokeWidth="5" />
            <line x1="796" y1="164" x2="796" y2="228" stroke="#111827" strokeWidth="5" />
            <text x="812" y="110" className="canvas-force">F</text>
            <text x="812" y="232" className="canvas-force">mg</text>
          </>
        ) : null}
      </svg>
      <div className="annotation-strip">
        {(runtime?.frame.annotations ?? []).map((item) => (
          <article key={item.key} className={`annotation-chip annotation-${item.emphasis}`}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </div>
    </div>
  );
}

function LessonRail({
  scene,
  runtime,
  stageId,
  onSelectStage
}: {
  scene: MechanicsScenePayload["scene"];
  runtime: MechanicsRuntimePayload | null;
  stageId: string;
  onSelectStage: (stageId: string) => void;
}) {
  const panel = scene.lesson_panels.find((item) => item.stage_id === stageId) ?? scene.lesson_panels[0];
  return (
    <aside className="lesson-rail">
      <section className="rail-card">
        <p className="panel-kicker">Stages</p>
        <div className="stage-stack">
          {scene.stages.map((stage) => (
            <button
              key={stage.id}
              className={stage.id === stageId ? "stage-pill stage-pill-active" : "stage-pill"}
              onClick={() => onSelectStage(stage.id)}
            >
              <span className="stage-index">{stageEmoji(stage.id)}</span>
              <span>
                <strong>{stage.title}</strong>
                <small>{stage.prompt}</small>
              </span>
            </button>
          ))}
        </div>
      </section>
      <section className="rail-card rail-card-lesson">
        <p className="panel-kicker">Lesson Panel</p>
        <h3>{panel?.headline}</h3>
        <p className="lesson-question">{panel?.question}</p>
        <p className="lesson-takeaway">{panel?.takeaway}</p>
        <ul className="lesson-points">
          {(panel?.bullets ?? []).map((bullet) => (
            <li key={bullet}>{bullet}</li>
          ))}
        </ul>
      </section>
      <section className="rail-card">
        <p className="panel-kicker">Live Checks</p>
        <div className="rail-metrics">
          <div>
            <span>Stage</span>
            <strong>{runtime?.stage.title ?? scene.stages[0]?.title}</strong>
          </div>
          <div>
            <span>Progress</span>
            <strong>{Math.round((runtime?.frame.progress ?? 0) * 100)}%</strong>
          </div>
          <div>
            <span>Belt Speed</span>
            <strong>{String(runtime?.frame.overlays.belt_speed ?? "5 m/s")}</strong>
          </div>
        </div>
      </section>
    </aside>
  );
}

function Charts({
  runtime
}: {
  runtime: MechanicsRuntimePayload | null;
}) {
  const charts = runtime?.frame.chart_series ?? [];
  return (
    <section className="charts-grid">
      {charts.map((chart) => (
        <article key={chart.id} className="chart-card">
          <div className="chart-head">
            <div>
              <p className="panel-kicker">Linked Chart</p>
              <h3>{chart.label}</h3>
            </div>
            <span>{chart.unit}</span>
          </div>
          <svg viewBox="0 0 240 120" className="chart-svg">
            <rect x="0" y="0" width="240" height="120" rx="18" fill="#fff9ef" />
            <path d={chartPath(chart.points, 220, 92)} transform="translate(10 14)" fill="none" stroke="#d1495b" strokeWidth="4" />
          </svg>
        </article>
      ))}
    </section>
  );
}

export function App() {
  const [problemText, setProblemText] = useState(SAMPLE_PROBLEM);
  const [solutionText, setSolutionText] = useState(SAMPLE_SOLUTION);
  const [finalAnswers, setFinalAnswers] = useState(SAMPLE_ANSWERS);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [session, setSession] = useState<MechanicsRecognitionPayload | null>(null);
  const [scenePayload, setScenePayload] = useState<MechanicsScenePayload | null>(null);
  const [runtime, setRuntime] = useState<MechanicsRuntimePayload | null>(null);
  const [selectedStage, setSelectedStage] = useState("slope");
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const playbackRef = useRef<number | null>(null);

  const answerCards = useMemo(() => {
    if (!session?.simulation) {
      return [];
    }
    return Object.values(session.simulation.answers);
  }, [session]);

  async function refreshRuntime(nextStage = selectedStage, nextProgress = progress) {
    if (!session) {
      return;
    }
    const payload = await simulateMechanicsScene(session.session_id, {
      stageId: nextStage,
      progress: nextProgress
    });
    setRuntime(payload);
  }

  async function handleGenerate() {
    try {
      setLoading(true);
      setError("");
      setIsPlaying(false);
      const recognized = await recognizeMechanicsProblem({
        problemText,
        solutionText,
        finalAnswers,
        imageFile
      });
      setSession(recognized);
      const generatedScene = await generateMechanicsScene(recognized.session_id);
      setScenePayload(generatedScene);
      const initialStage = generatedScene.scene.stages[0]?.id ?? "slope";
      setSelectedStage(initialStage);
      setProgress(0);
      const firstFrame = await simulateMechanicsScene(recognized.session_id, {
        stageId: initialStage,
        progress: 0
      });
      setRuntime(firstFrame);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : String(requestError));
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm() {
    if (!session) {
      return;
    }
    try {
      setLoading(true);
      const confirmed = await confirmMechanicsProblem(session.session_id, {
        selected_model_id: session.selected_model?.id
      });
      setSession(confirmed);
      const generatedScene = await generateMechanicsScene(confirmed.session_id);
      setScenePayload(generatedScene);
      await refreshRuntime(selectedStage, progress);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : String(requestError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!isPlaying || !session) {
      return;
    }
    playbackRef.current = window.setInterval(() => {
      setProgress((current) => {
        const next = current + 0.08;
        if (next >= 1) {
          setIsPlaying(false);
          return 1;
        }
        return next;
      });
    }, 220);
    return () => {
      if (playbackRef.current) {
        window.clearInterval(playbackRef.current);
      }
    };
  }, [isPlaying, session]);

  useEffect(() => {
    if (!session || !scenePayload) {
      return;
    }
    refreshRuntime(selectedStage, progress).catch((requestError) => {
      setError(requestError instanceof Error ? requestError.message : String(requestError));
    });
  }, [selectedStage, progress]);

  const currentStage = scenePayload?.scene.stages.find((item) => item.id === selectedStage);

  return (
    <main className="workbench-shell">
      <header className="hero-band">
        <div>
          <p className="hero-kicker">Problem → Harness → Teaching Simulation</p>
          <h1>教师工作台</h1>
          <p className="hero-copy">
            GAI 负责抽取物理模型，harness 负责约束、校验、scene 编译与讲解 runtime。上传题干与解析后，平台直接生成可讲解的力学仿真。
          </p>
        </div>
        <div className="hero-status">
          <span>{session?.execution_mode ?? "dev_proxy"}</span>
          <strong>{session?.selected_model?.title ?? "等待生成"}</strong>
        </div>
      </header>

      <section className="composer-grid">
        <article className="composer-card composer-card-wide">
          <div className="card-head">
            <div>
              <p className="panel-kicker">Inputs</p>
              <h2>题目与解析</h2>
            </div>
            <button className="primary-button" onClick={handleGenerate} disabled={loading}>
              {loading ? "生成中..." : "生成 simulation"}
            </button>
          </div>
          <div className="composer-fields">
            <label>
              <span>题目文本</span>
              <textarea value={problemText} onChange={(event) => setProblemText(event.target.value)} />
            </label>
            <label>
              <span>解析文本</span>
              <textarea value={solutionText} onChange={(event) => setSolutionText(event.target.value)} />
            </label>
          </div>
          <div className="composer-inline">
            <label>
              <span>答案串</span>
              <input value={finalAnswers} onChange={(event) => setFinalAnswers(event.target.value)} />
            </label>
            <label>
              <span>题目截图</span>
              <input type="file" accept="image/*" onChange={(event) => setImageFile(event.target.files?.[0] ?? null)} />
            </label>
          </div>
          {error ? <p className="error-banner">{error}</p> : null}
        </article>

        <article className="composer-card">
          <p className="panel-kicker">Validation</p>
          <h2>答案对齐</h2>
          <div className="answer-grid">
            {answerCards.map((item) => (
              <div key={item.key} className="answer-card">
                <span>{item.label}</span>
                <strong>{item.display_value}</strong>
              </div>
            ))}
          </div>
          {session?.needs_confirmation ? (
            <div className="warning-box">
              <p>当前链路检测到冲突或低置信度，需要教师确认后再放行。</p>
              <button onClick={handleConfirm} className="secondary-button" disabled={loading}>
                以当前模型确认
              </button>
            </div>
          ) : (
            <div className="confidence-box">
              <span>校验状态</span>
              <strong>通过</strong>
              <small>模型、答案与仿真结果已对齐。</small>
            </div>
          )}
        </article>
      </section>

      <section className="workbench-grid">
        <div className="presentation-column">
          {scenePayload ? <TeachingScene scene={scenePayload.scene} runtime={runtime} /> : <div className="empty-stage">生成后在这里看到讲解型 simulation。</div>}
          {runtime ? <Charts runtime={runtime} /> : null}
        </div>

        {scenePayload ? (
          <LessonRail
            scene={scenePayload.scene}
            runtime={runtime}
            stageId={selectedStage}
            onSelectStage={(stageId) => {
              setSelectedStage(stageId);
              setProgress(0);
              setIsPlaying(false);
            }}
          />
        ) : (
          <aside className="lesson-rail">
            <section className="rail-card">
              <p className="panel-kicker">Playback</p>
              <h3>等待生成</h3>
              <p>生成后这里会显示阶段切换、讲解要点和联动图表。</p>
            </section>
          </aside>
        )}
      </section>

      <section className="timeline-card">
        <div className="card-head">
          <div>
            <p className="panel-kicker">Playback</p>
            <h2>{currentStage?.title ?? "阶段控制"}</h2>
          </div>
          <div className="transport-group">
            <button className="secondary-button" onClick={() => setIsPlaying((value) => !value)} disabled={!scenePayload}>
              {isPlaying ? "暂停" : "播放"}
            </button>
            <button className="secondary-button" onClick={() => setProgress(0)} disabled={!scenePayload}>
              回到阶段开头
            </button>
          </div>
        </div>
        <input
          className="timeline-slider"
          type="range"
          min={0}
          max={100}
          value={Math.round(progress * 100)}
          onChange={(event) => {
            setIsPlaying(false);
            setProgress(Number(event.target.value) / 100);
          }}
          disabled={!scenePayload}
        />
        <div className="timeline-notes">
          {(scenePayload?.scene.playback_steps ?? []).map((step) => (
            <article key={step.stage_id} className={step.stage_id === selectedStage ? "timeline-note timeline-note-active" : "timeline-note"}>
              <strong>{stageEmoji(step.stage_id)}</strong>
              <span>{step.headline}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="inspector-grid">
        <article className="inspector-card">
          <p className="panel-kicker">Artifacts</p>
          <h2>Harness & Executor</h2>
          <pre>{JSON.stringify(session?.executor_run?.tool_trace ?? [], null, 2)}</pre>
        </article>
        <article className="inspector-card">
          <p className="panel-kicker">Verification</p>
          <h2>护栏与审计</h2>
          <pre>{JSON.stringify(session?.verification_report ?? {}, null, 2)}</pre>
        </article>
        <article className="inspector-card">
          <p className="panel-kicker">Logs</p>
          <h2>Runtime</h2>
          <pre>{JSON.stringify(runtime?.frame.overlays ?? {}, null, 2)}</pre>
        </article>
      </section>
    </main>
  );
}
