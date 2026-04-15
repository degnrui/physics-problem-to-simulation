interface SimulationHeaderBarProps {
  runId: string;
  title: string;
  status: string;
  exportable: boolean;
  exporting: boolean;
  onBack: () => void;
  onExport: () => void;
}

export function SimulationHeaderBar({
  runId,
  title,
  status,
  exportable,
  exporting,
  onBack,
  onExport,
}: SimulationHeaderBarProps) {
  return (
    <header className="workspace-header">
      <div className="workspace-header-main">
        <button type="button" className="workspace-back-button" onClick={onBack}>
          返回
        </button>
        <div className="workspace-title-block">
          <p className="eyebrow">Simulation Workspace</p>
          <h1>{title}</h1>
          <p className="muted">
            run: <code>{runId}</code>
          </p>
        </div>
      </div>
      <div className="workspace-header-actions">
        <span className={`workspace-status-badge status-${status}`}>{status}</span>
        <button type="button" className="secondary-button" onClick={onExport} disabled={!exportable || exporting}>
          {exporting ? "导出中..." : "导出 HTML"}
        </button>
      </div>
    </header>
  );
}
