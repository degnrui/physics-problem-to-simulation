import type { ReactNode } from "react";

interface UtilityRailProps {
  expanded: boolean;
  onToggleSidebar: () => void;
  onNewConversation: () => void;
  onSearchConversation: () => void;
}

function RailGlyph({ kind }: { kind: "sidebar" | "plus" | "search" | "user" }) {
  if (kind === "sidebar") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="rail-glyph">
        <path d="M4 7h16M4 12h16M4 17h16" />
      </svg>
    );
  }

  if (kind === "plus") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="rail-glyph">
        <path d="M12 5v14M5 12h14" />
      </svg>
    );
  }

  if (kind === "search") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="rail-glyph">
        <circle cx="11" cy="11" r="5.5" />
        <path d="M15.4 15.4 19 19" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="rail-glyph">
      <circle cx="12" cy="8.8" r="3.2" />
      <path d="M6.8 18c.9-2.8 3.2-4.4 5.2-4.4s4.3 1.6 5.2 4.4" />
    </svg>
  );
}

function RailButton({
  label,
  onClick,
  children,
}: {
  label: string;
  onClick?: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      className="rail-icon-button with-tooltip"
      onClick={onClick}
      aria-label={label}
      data-tooltip={label}
    >
      {children}
    </button>
  );
}

export function UtilityRail({
  expanded,
  onToggleSidebar,
  onNewConversation,
  onSearchConversation,
}: UtilityRailProps) {
  return (
    <aside className="utility-rail">
      <div className="flex flex-col gap-4">
        <RailButton label={expanded ? "收起侧边栏" : "展开侧边栏"} onClick={onToggleSidebar}>
          <RailGlyph kind="sidebar" />
        </RailButton>
        <RailButton label="新建聊天" onClick={onNewConversation}>
          <RailGlyph kind="plus" />
        </RailButton>
        <RailButton label="搜索聊天" onClick={onSearchConversation}>
          <RailGlyph kind="search" />
        </RailButton>
      </div>

      <RailButton label="教师账户">
        <RailGlyph kind="user" />
      </RailButton>
    </aside>
  );
}
