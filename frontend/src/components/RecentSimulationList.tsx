import type { RunListItem } from "../lib/api";

interface RecentSimulationListProps {
  items: RunListItem[];
  loading: boolean;
  onOpen: (runId: string) => void;
}

export function RecentSimulationList({
  items,
  loading,
  onOpen,
}: RecentSimulationListProps) {
  return (
    <section className="panel launcher-list-panel">
      <div className="launcher-list-header">
        <div>
          <p className="eyebrow">Recent Simulations</p>
          <h2>继续已有 Simulation</h2>
        </div>
        <p className="muted">按最近更新时间排序。</p>
      </div>
      {loading ? (
        <p className="muted">正在读取最近项目...</p>
      ) : items.length === 0 ? (
        <p className="muted">还没有历史 simulation。先创建一个新的题目工作区。</p>
      ) : (
        <div className="recent-run-list">
          {items.map((item) => (
            <button
              type="button"
              key={item.run_id}
              className="recent-run-card"
              onClick={() => onOpen(item.run_id)}
            >
              <div className="recent-run-top">
                <p className="log-eyebrow">{item.status}</p>
                <span className={`recent-run-pill status-${item.status}`}>{item.simulation_mode}</span>
              </div>
              <h3>{item.title}</h3>
              <p className="muted recent-run-summary">{item.model_family || "unknown-model"}</p>
              <div className="recent-run-meta">
                <span>{item.updated_at ? new Date(item.updated_at).toLocaleString("zh-CN") : "--"}</span>
                <span>{item.export_ready ? "可导出" : "未就绪"}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
