import type { RunStep } from "../lib/api";

interface SimulationStageRailProps {
  steps: RunStep[];
  currentStage: string;
}

export function SimulationStageRail({ steps, currentStage }: SimulationStageRailProps) {
  return (
    <aside className="workspace-stage-rail panel">
      <div className="workspace-rail-header">
        <p className="eyebrow">Pipeline</p>
        <h2>Simulation Stages</h2>
      </div>
      <div className="workspace-stage-list">
        {steps.map((step, index) => (
          <article key={step.id} className={`workspace-stage-card step-status-${step.status}`}>
            <div className="workspace-stage-title">
              <span className="stage-index">{index + 1}</span>
              <div>
                <h3>{step.label}</h3>
                <p className="muted">
                  {step.artifacts_written.length > 0 ? step.artifacts_written.join(", ") : "artifact pending"}
                </p>
              </div>
            </div>
            <div className="workspace-stage-footer">
              <span className={`step-status-pill status-${step.status}`}>{step.status}</span>
              <span className="muted">
                {step.execution_mode || (currentStage === step.label ? currentStage : "rule-based")}
              </span>
            </div>
            {step.error ? <p className="error">{step.error}</p> : null}
          </article>
        ))}
      </div>
    </aside>
  );
}
