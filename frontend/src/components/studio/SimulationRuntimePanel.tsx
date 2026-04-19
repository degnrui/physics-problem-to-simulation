import { useEffect, useMemo, useRef, useState } from "react";
import type { EditableFieldId, InlineEditTarget, RuntimeDocument } from "../../types/studio";

interface SimulationRuntimePanelProps {
  document: RuntimeDocument;
  fullscreen?: boolean;
  onRequestEdit: (target: InlineEditTarget) => void;
}

interface RuntimeControls {
  distance: number;
  friction: number;
  speed: number;
}

export function SimulationRuntimePanel({
  document,
  fullscreen = false,
  onRequestEdit,
}: SimulationRuntimePanelProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [controls, setControls] = useState<RuntimeControls>({
    distance: 1.2,
    friction: 0.24,
    speed: 1,
  });
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0.18);

  useEffect(() => {
    if (!playing) {
      return undefined;
    }

    const timer = window.setInterval(() => {
      setProgress((value) => {
        const next = value + 0.012 * controls.speed;
        return next > 1 ? 0 : next;
      });
    }, 40);

    return () => window.clearInterval(timer);
  }, [controls.speed, playing]);

  const derived = useMemo(() => {
    const damping = Math.exp(-progress * (0.8 + controls.friction));
    const oscillation = Math.cos(progress * Math.PI * 2.5 * controls.speed);
    const offset = controls.distance * 92 * damping * oscillation;
    const restoringForce = Math.abs(offset) * 0.18 + 24;
    const energy = Math.max(0.12, damping);
    return { offset, restoringForce, energy };
  }, [controls.distance, controls.friction, controls.speed, progress]);

  function handleRequestEdit(
    event: React.MouseEvent<HTMLButtonElement>,
    field: EditableFieldId,
    label: string,
    value: string,
  ) {
    const rect = event.currentTarget.getBoundingClientRect();
    const containerRect = containerRef.current?.getBoundingClientRect();
    if (!containerRect) {
      return;
    }

    onRequestEdit({
      field,
      label,
      value,
      anchor: {
        top: rect.bottom - containerRect.top + 10,
        left: Math.max(16, rect.left - containerRect.left),
      },
    });
  }

  return (
    <div ref={containerRef} className={fullscreen ? "runtime-panel fullscreen" : "runtime-panel"}>
      <section className="runtime-card runtime-card-scene">
        <div className="runtime-section-header">
          <div className="space-y-2">
            <div className="runtime-panel-heading">
              <span className="runtime-section-marker" aria-hidden="true" />
              <h2 className="runtime-section-title">课堂演示</h2>
            </div>
            <button
              type="button"
              className="runtime-editable text-left text-[0.95rem] leading-7 text-[color:var(--studio-text-muted)]"
              onClick={(event) => handleRequestEdit(event, "subtitle", "说明", document.subtitle)}
            >
              {document.subtitle}
            </button>
          </div>
          <div className="runtime-scene-badge">{document.sceneLabel}</div>
        </div>

        <div className="runtime-canvas-shell">
          <svg viewBox="0 0 720 420" className="runtime-canvas" role="img" aria-label="simulation runtime">
            <defs>
              <linearGradient id="trackGlow" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="rgba(82,120,104,0.08)" />
                <stop offset="100%" stopColor="rgba(82,120,104,0.16)" />
              </linearGradient>
            </defs>

            <rect x="60" y="96" width="600" height="248" rx="28" fill="url(#trackGlow)" />
            <line x1="140" y1="210" x2="580" y2="210" stroke="rgba(65,79,82,0.22)" strokeWidth="4" strokeLinecap="round" />
            <circle cx="180" cy="210" r="12" fill="rgba(68,86,88,0.55)" />
            <circle cx="540" cy="210" r="12" fill="rgba(68,86,88,0.55)" />
            <text x="171" y="184" fill="rgba(46,61,68,0.78)" fontSize="18">A</text>
            <text x="532" y="184" fill="rgba(46,61,68,0.78)" fontSize="18">B</text>
            <text x="346" y="184" fill="rgba(46,61,68,0.62)" fontSize="16">平衡位置 C</text>

            <line x1="180" y1="210" x2={360 + derived.offset} y2="210" stroke="rgba(92,111,113,0.48)" strokeWidth="6" strokeLinecap="round" />
            <line x1="540" y1="210" x2={360 + derived.offset} y2="210" stroke="rgba(92,111,113,0.48)" strokeWidth="6" strokeLinecap="round" />
            <rect x={334 + derived.offset} y="184" width="52" height="52" rx="10" fill="rgba(33,57,66,0.92)" />
            <line
              x1={360 + derived.offset}
              y1="160"
              x2={360 + derived.offset - derived.restoringForce}
              y2="160"
              stroke="rgba(78,129,110,0.96)"
              strokeWidth="6"
              strokeLinecap="round"
            />
            <polygon
              points={`${360 + derived.offset - derived.restoringForce},160 ${370 + derived.offset - derived.restoringForce},154 ${370 + derived.offset - derived.restoringForce},166`}
              fill="rgba(78,129,110,0.96)"
            />
            <text x={364 + derived.offset - derived.restoringForce - 84} y="144" fill="rgba(62,107,90,0.95)" fontSize="14">
              合回复力
            </text>

            <line
              x1={360 + derived.offset}
              y1="274"
              x2={360 + derived.offset + 52 * controls.friction}
              y2="274"
              stroke="rgba(180,120,92,0.85)"
              strokeWidth="5"
              strokeLinecap="round"
            />
            <text x={370 + derived.offset + 18 * controls.friction} y="296" fill="rgba(140,98,73,0.92)" fontSize="14">
              摩擦
            </text>
          </svg>

          <div className="grid gap-3 md:grid-cols-3">
            <MetricTile label="位移幅度" value={`${controls.distance.toFixed(2)} m`} />
            <MetricTile label="摩擦系数" value={controls.friction.toFixed(2)} />
            <MetricTile label="保留能量" value={`${Math.round(derived.energy * 100)} %`} />
          </div>
        </div>
      </section>

      <section className="runtime-card">
        <div className="runtime-panel-heading">
          <span className="runtime-section-marker" aria-hidden="true" />
          <h2 className="runtime-section-title">实验设置</h2>
        </div>

        <div className="grid gap-4">
          <RuntimeSlider
            name="runtime-distance"
            label="初始拉开距离 L"
            value={controls.distance}
            min={0.4}
            max={1.8}
            step={0.05}
            display={`${controls.distance.toFixed(2)} m`}
            onChange={(value) => setControls((current) => ({ ...current, distance: value }))}
          />
          <RuntimeSlider
            name="runtime-friction"
            label="动摩擦因数 μ"
            value={controls.friction}
            min={0}
            max={0.6}
            step={0.02}
            display={controls.friction.toFixed(2)}
            onChange={(value) => setControls((current) => ({ ...current, friction: value }))}
          />
          <RuntimeSlider
            name="runtime-speed"
            label="回放速度"
            value={controls.speed}
            min={0.5}
            max={2.6}
            step={0.1}
            display={`${controls.speed.toFixed(1)}x`}
            onChange={(value) => setControls((current) => ({ ...current, speed: value }))}
          />

          <div className="flex gap-2">
            <button type="button" className="secondary-chip flex-1 justify-center" onClick={() => setPlaying((value) => !value)}>
              {playing ? "暂停" : "播放"}
            </button>
            <button
              type="button"
              className="secondary-chip flex-1 justify-center"
              onClick={() => {
                setPlaying(false);
                setProgress(0.18);
              }}
            >
              重置
            </button>
          </div>
        </div>
      </section>

      <section className="runtime-card">
        <div className="runtime-panel-heading">
          <span className="runtime-section-marker" aria-hidden="true" />
          <h2 className="runtime-section-title">教学提示</h2>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <button
            type="button"
            className="runtime-editable runtime-note-card text-left"
            onClick={(event) => handleRequestEdit(event, "objective", "教学目标", document.objective)}
          >
            <p className="runtime-side-label">教学目标</p>
            <p className="mt-2 text-sm leading-7 text-[color:var(--studio-ink)]">{document.objective}</p>
          </button>

          <button
            type="button"
            className="runtime-editable runtime-note-card text-left"
            onClick={(event) => handleRequestEdit(event, "focusArea", "观察重点", document.focusArea)}
          >
            <p className="runtime-side-label">观察重点</p>
            <p className="mt-2 text-sm leading-7 text-[color:var(--studio-ink)]">{document.focusArea}</p>
          </button>
        </div>

        <button
          type="button"
          className="runtime-editable runtime-callout-card text-left"
          onClick={(event) => handleRequestEdit(event, "callout", "课堂提醒", document.callout)}
        >
          <p className="runtime-side-label">课堂提醒</p>
          <p className="mt-2 text-sm leading-7 text-[color:var(--studio-ink)]">{document.callout}</p>
        </button>
      </section>

      <section className="runtime-card">
        <div className="runtime-panel-heading">
          <span className="runtime-section-marker" aria-hidden="true" />
          <h2 className="runtime-section-title">讲评顺序</h2>
        </div>

        <p className="text-sm leading-7 text-[color:var(--studio-text-muted)]">{document.motionHint}</p>
        <p className="text-sm leading-7 text-[color:var(--studio-ink)]">{document.equation}</p>

        <ul className="runtime-checklist">
          {document.observationTargets.slice(0, 3).map((target) => (
            <li key={target}>
              <span className="runtime-check-dot" aria-hidden="true" />
              <span>{target}</span>
            </li>
          ))}
          {document.teacherScript.slice(0, 2).map((line) => (
            <li key={line}>
              <span className="runtime-check-dot accent" aria-hidden="true" />
              <span>{line}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[22px] border border-[color:var(--studio-line)] bg-[color:var(--studio-surface-strong)] px-4 py-4">
      <p className="text-[0.74rem] uppercase tracking-[0.16em] text-[color:var(--studio-text-subtle)]">{label}</p>
      <p className="mt-2 text-[1rem] font-semibold text-[color:var(--studio-ink)]">{value}</p>
    </div>
  );
}

function RuntimeSlider({
  name,
  label,
  value,
  min,
  max,
  step,
  display,
  onChange,
}: {
  name: string;
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  display: string;
  onChange: (value: number) => void;
}) {
  return (
    <label className="space-y-3">
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="text-[color:var(--studio-text-muted)]">{label}</span>
        <span className="font-medium text-[color:var(--studio-ink)]">{display}</span>
      </div>
      <input
        id={name}
        name={name}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full accent-[color:var(--studio-accent-ink)]"
      />
    </label>
  );
}
