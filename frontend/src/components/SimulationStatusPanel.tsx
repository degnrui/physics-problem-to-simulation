import type { RunResultResponse, RunStatusResponse } from "../lib/api";

interface SimulationStatusPanelProps {
  status: RunStatusResponse | null;
  result: RunResultResponse | null;
}

export function SimulationStatusPanel({
  status,
  result,
}: SimulationStatusPanelProps) {
  const deliveryBundle = (result?.delivery_bundle ?? {}) as Record<string, unknown>;
  const observationTargets =
    (deliveryBundle.observation_targets as string[] | undefined) ?? [];
  const teacherScript = (deliveryBundle.teacher_script as string[] | undefined) ?? [];
  const validation = (result?.validation_report ?? {}) as Record<string, unknown>;
  const progressText =
    status?.status === "completed"
      ? "simulation 已就绪，可直接交互与导出。"
      : status?.status === "failed"
        ? "当前 run 失败，保留错误信息与已生成工件。"
        : "主舞台保持在同一路由内持续填充，不再跳转独立处理中页。";

  return (
    <aside className="workspace-status-panel">
      <section className="panel status-panel-block">
        <p className="eyebrow">Workspace State</p>
        <h2>{status?.current_stage ?? status?.status ?? "initializing"}</h2>
        <p className="muted">{progressText}</p>
        <div className="progress-track workspace-progress-track">
          <div className="progress-fill" style={{ width: `${status?.percent ?? 0}%` }} />
        </div>
        <div className="run-meta-grid">
          <article className="summary-chip">
            <span>Status</span>
            <strong>{status?.status ?? "--"}</strong>
          </article>
          <article className="summary-chip">
            <span>Progress</span>
            <strong>{status?.percent ?? 0}%</strong>
          </article>
        </div>
      </section>

      <section className="panel status-panel-block">
        <p className="eyebrow">Teacher Guidance</p>
        <h2>教师说明</h2>
        {teacherScript.length > 0 ? (
          <ul className="plain-list">
            {teacherScript.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="muted">生成阶段先展示当前工作说明，完成后这里会填入教师脚本。</p>
        )}
      </section>

      <section className="panel status-panel-block">
        <p className="eyebrow">Validation</p>
        <h2>验证摘要</h2>
        {result ? (
          <ul className="plain-list">
            <li>ready_for_delivery: {String(validation.ready_for_delivery ?? false)}</li>
            <li>export_ready: {String(validation.export_ready ?? false)}</li>
            <li>observation_targets: {observationTargets.length}</li>
          </ul>
        ) : (
          <p className="muted">结果未就绪时，这里展示 run 状态与即将生成的诊断信息。</p>
        )}
      </section>
    </aside>
  );
}
