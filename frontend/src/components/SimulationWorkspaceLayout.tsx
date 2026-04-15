import { PipelinePreview } from "./PipelinePreview";
import { SimulationHeaderBar } from "./SimulationHeaderBar";
import { SimulationStageRail } from "./SimulationStageRail";
import { SimulationStatusPanel } from "./SimulationStatusPanel";
import { SimulationViewport } from "./SimulationViewport";
import { StageLogList } from "./StageLogList";
import type { RunResultResponse, RunStatusResponse } from "../lib/api";

type InspectorTabId = "summary" | "artifacts" | "validation" | "logs";

interface SimulationWorkspaceLayoutProps {
  runId: string;
  status: RunStatusResponse | null;
  result: RunResultResponse | null;
  error: string | null;
  exporting: boolean;
  activeTab: InspectorTabId;
  onBack: () => void;
  onExport: () => void;
  onChangeTab: (tab: InspectorTabId) => void;
}

export function SimulationWorkspaceLayout({
  runId,
  status,
  result,
  error,
  exporting,
  activeTab,
  onBack,
  onExport,
  onChangeTab,
}: SimulationWorkspaceLayoutProps) {
  const rendererPayload = (result?.renderer_payload ?? {}) as Record<string, unknown>;
  const deliveryBundle = (result?.delivery_bundle ?? {}) as Record<string, unknown>;
  const title =
    String(
      (result?.problem_profile?.summary as string | undefined)
        ?? result?.planner?.model_family
        ?? "Simulation Workspace",
    ).slice(0, 48);

  return (
    <main className="workspace-shell">
      <SimulationHeaderBar
        runId={runId}
        title={title}
        status={status?.status ?? "initializing"}
        exportable={Boolean(result?.validation_report?.export_ready)}
        exporting={exporting}
        onBack={onBack}
        onExport={onExport}
      />

      <section className="workspace-grid">
        <SimulationStageRail
          steps={status?.steps ?? []}
          currentStage={status?.current_stage ?? "initializing"}
        />

        <section className="workspace-center">
          <section className="workspace-canvas panel">
            <div className="workspace-canvas-header">
              <div>
                <p className="eyebrow">Main Stage</p>
                <h2>Simulation Stage</h2>
              </div>
              <span className={`workspace-status-badge status-${status?.status ?? "initializing"}`}>
                {status?.status ?? "initializing"}
              </span>
            </div>
            {status?.status !== "completed" ? (
              <div className="workspace-stage-placeholder">
                <div className="placeholder-grid" />
                <div className="placeholder-copy">
                  <h3>Simulation 主舞台正在构建</h3>
                  <p className="muted">
                    当前阶段：{status?.current_stage ?? "initializing"}。页面不跳转，左侧 rail 和右侧状态会持续更新。
                  </p>
                </div>
              </div>
            ) : (
              <SimulationViewport
                sceneSpec={result?.scene_spec ?? {}}
                simulationSpec={result?.simulation_spec ?? null}
                rendererPayload={result?.renderer_payload ?? null}
                deliveryBundle={result?.delivery_bundle ?? null}
              />
            )}
            {error ? <p className="error">{error}</p> : null}
          </section>

          <section className="workspace-inspector panel">
            <div className="inspector-header">
              <div>
                <p className="eyebrow">Inspector</p>
                <h2>辅助信息层</h2>
              </div>
              <p className="muted inspector-meta">默认退居二线，不压过主 simulation 舞台。</p>
            </div>
            <div className="inspector-tabs" role="tablist" aria-label="Inspector tabs">
              {["summary", "artifacts", "validation", "logs"].map((id) => (
                <button
                  type="button"
                  key={id}
                  className={id === activeTab ? "inspector-tab active" : "inspector-tab"}
                  onClick={() => onChangeTab(id as InspectorTabId)}
                >
                  {id}
                </button>
              ))}
            </div>
            <div className="inspector-content">
              {activeTab === "summary" ? (
                <div className="artifact-grid">
                  <PipelinePreview compact title="Planner" data={result?.planner ?? {}} />
                  <PipelinePreview compact title="Problem Profile" data={result?.problem_profile ?? {}} />
                  <PipelinePreview compact title="Teaching Plan" data={result?.teaching_plan ?? {}} />
                </div>
              ) : null}
              {activeTab === "artifacts" ? (
                <div className="artifact-grid artifact-grid-wide">
                  <PipelinePreview compact title="Physics Model" data={result?.physics_model ?? {}} />
                  <PipelinePreview compact title="Scene Spec" data={result?.scene_spec ?? {}} />
                  <PipelinePreview compact title="Simulation Spec" data={result?.simulation_spec ?? {}} />
                  <PipelinePreview compact title="Renderer Payload" data={rendererPayload} />
                  <PipelinePreview compact title="Delivery Bundle" data={deliveryBundle} />
                </div>
              ) : null}
              {activeTab === "validation" ? (
                <div className="artifact-grid">
                  <PipelinePreview compact title="Simulation Blueprint" data={result?.simulation_blueprint ?? {}} />
                  <PipelinePreview compact title="Validation Report" data={result?.validation_report ?? {}} />
                </div>
              ) : null}
              {activeTab === "logs" ? <StageLogList compact logs={result?.task_log ?? []} /> : null}
            </div>
          </section>
        </section>

        <SimulationStatusPanel status={status} result={result} />
      </section>
    </main>
  );
}
