import { useEffect, useRef, useState } from "react";

const actionItems = [
  { id: "upload", label: "添加照片或文件", icon: "clip" },
  { id: "search", label: "网页搜索", icon: "search" },
] as const;

type ActionKind = "plus" | "clip" | "search";

function ActionGlyph({ kind }: { kind: ActionKind }) {
  if (kind === "plus") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="action-glyph">
        <path d="M12 5v14M5 12h14" />
      </svg>
    );
  }

  if (kind === "clip") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="action-glyph">
        <path d="M8.5 12.5 14.8 6.2a3 3 0 1 1 4.2 4.3L10.9 18.6a4.5 4.5 0 0 1-6.4-6.4l8.4-8.3" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="action-glyph">
      <circle cx="11" cy="11" r="5.5" />
      <path d="M15.4 15.4 19 19" />
    </svg>
  );
}

export function TooltipActionIcons() {
  const [selectedAction, setSelectedAction] = useState<(typeof actionItems)[number] | null>(null);
  const [hovered, setHovered] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const closeTimeoutRef = useRef<number | null>(null);

  const menuVisible = hovered || expanded;
  const handleSelectAction = (item: (typeof actionItems)[number]) => {
    if (closeTimeoutRef.current) {
      window.clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
    setSelectedAction(item);
    setHovered(false);
    setExpanded(false);
  };

  useEffect(() => {
    return () => {
      if (closeTimeoutRef.current) {
        window.clearTimeout(closeTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div
      className="quick-action-shell"
      onMouseEnter={() => {
        if (closeTimeoutRef.current) {
          window.clearTimeout(closeTimeoutRef.current);
          closeTimeoutRef.current = null;
        }
        setHovered(true);
      }}
      onMouseLeave={() => {
        if (closeTimeoutRef.current) {
          window.clearTimeout(closeTimeoutRef.current);
        }
        closeTimeoutRef.current = window.setTimeout(() => {
          setHovered(false);
          setExpanded(false);
          closeTimeoutRef.current = null;
        }, 90);
      }}
    >
      <div className="quick-action-trigger-row">
        <button
          type="button"
          className="quick-action-trigger"
          aria-label="添加内容"
          aria-expanded={menuVisible}
          onClick={() => setExpanded((value) => !value)}
        >
          <ActionGlyph kind="plus" />
        </button>
        {selectedAction ? <span className="quick-action-selection">{selectedAction.label}</span> : null}
      </div>

      {menuVisible ? (
        <div className="quick-action-menu" data-visible={menuVisible}>
          {actionItems.map((item) => (
            <button
              key={item.id}
              type="button"
              className="quick-action-option"
              onMouseDown={() => handleSelectAction(item)}
              onClick={() => handleSelectAction(item)}
            >
              <span className="quick-action-option-icon">
                <ActionGlyph kind={item.icon} />
              </span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
