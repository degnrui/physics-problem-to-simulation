const actionItems = [
  { id: "upload", label: "上传附件", icon: "clip" },
  { id: "template", label: "教学模板", icon: "stack" },
  { id: "mode", label: "模式选择", icon: "spark" },
  { id: "type", label: "simulation 类型", icon: "orbit" },
];

function ActionGlyph({ kind }: { kind: "clip" | "stack" | "spark" | "orbit" }) {
  if (kind === "clip") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="action-glyph">
        <path d="M8.5 12.5 14.8 6.2a3 3 0 1 1 4.2 4.3L10.9 18.6a4.5 4.5 0 0 1-6.4-6.4l8.4-8.3" />
      </svg>
    );
  }

  if (kind === "stack") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="action-glyph">
        <path d="M12 4 20 8 12 12 4 8 12 4Z" />
        <path d="M4 12 12 16 20 12" />
        <path d="M4 16 12 20 20 16" />
      </svg>
    );
  }

  if (kind === "spark") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="action-glyph">
        <path d="M12 4 13.5 8.5 18 10 13.5 11.5 12 16 10.5 11.5 6 10 10.5 8.5 12 4Z" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="action-glyph">
      <circle cx="12" cy="12" r="2.2" />
      <path d="M12 3.8v3.1M12 17.1v3.1M3.8 12h3.1M17.1 12h3.1M6.3 6.3l2.2 2.2M15.5 15.5l2.2 2.2M17.7 6.3l-2.2 2.2M8.5 15.5l-2.2 2.2" />
    </svg>
  );
}

export function TooltipActionIcons() {
  return (
    <div className="flex items-center gap-2">
      {actionItems.map((item) => (
        <button key={item.id} type="button" className="icon-tooltip-button" title={item.label} aria-label={item.label}>
          <ActionGlyph kind={item.icon as "clip" | "stack" | "spark" | "orbit"} />
        </button>
      ))}
    </div>
  );
}
