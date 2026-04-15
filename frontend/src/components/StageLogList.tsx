interface StageLogListProps {
  logs: Array<Record<string, unknown>>;
  compact?: boolean;
}

export function StageLogList({ logs, compact = false }: StageLogListProps) {
  return (
    <section className={compact ? "artifact-log-shell" : "panel"}>
      <h2>Stage Logs</h2>
      {logs.length === 0 ? (
        <p className="muted">运行完成后，这里会显示 harness 全链路日志。</p>
      ) : (
        <div className="log-list">
          {logs.map((log, index) => (
            <article className="log-card" key={`${String(log.task_id ?? index)}-${index}`}>
              <p className="log-eyebrow">{String(log.task_type ?? "unknown-stage")}</p>
              <h3>{String(log.output_digest ?? "No digest")}</h3>
              <p>{String(log.input_summary ?? "")}</p>
              <p className="muted">next: {String(log.next_task ?? "end")}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
