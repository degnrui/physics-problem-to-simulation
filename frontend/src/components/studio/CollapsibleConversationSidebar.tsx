import { formatTimestamp } from "../../lib/studio";
import type { ConversationSummary } from "../../types/studio";
import { StudioBrand } from "./StudioBrand";

interface CollapsibleConversationSidebarProps {
  conversations: ConversationSummary[];
  selectedConversationId: string | null;
  query: string;
  onQueryChange: (value: string) => void;
  onSelectConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  onReturnHome: () => void;
  onCollapse: () => void;
}

function SidebarGlyph({ kind }: { kind: "collapse" | "search" | "plus" | "message" }) {
  if (kind === "collapse") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="rail-glyph">
        <rect x="5" y="4" width="14" height="16" rx="3" />
        <path d="M10 4v16M8 9h.01M8 12h.01M8 15h.01" />
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

  if (kind === "plus") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="rail-glyph">
        <path d="M12 5v14M5 12h14" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="sidebar-message-glyph">
      <path d="M6.5 7.2A3.2 3.2 0 0 1 9.6 4h4.8a3.2 3.2 0 0 1 3.1 3.2v5.1a3.2 3.2 0 0 1-3.1 3.2H10l-4 3v-3.3A3.2 3.2 0 0 1 3 12.3V7.2a3.2 3.2 0 0 1 3.5 0Z" />
      <path d="M8.8 9.5h6.4M8.8 12.5h4.2" />
    </svg>
  );
}

export function CollapsibleConversationSidebar({
  conversations,
  selectedConversationId,
  query,
  onQueryChange,
  onSelectConversation,
  onNewConversation,
  onReturnHome,
  onCollapse,
}: CollapsibleConversationSidebarProps) {
  return (
    <aside className="conversation-sidebar">
      <div className="sidebar-top-shell">
        <div className="flex items-start justify-between gap-4">
          <button
            type="button"
            className="sidebar-brand-button"
            onClick={onReturnHome}
            aria-label="ClassSim 返回首页"
          >
            <StudioBrand compact />
          </button>
          <button
            type="button"
            className="sidebar-utility-button with-tooltip"
            onClick={onCollapse}
            aria-label="收起侧边栏"
            data-tooltip="收起侧边栏"
          >
            <SidebarGlyph kind="collapse" />
          </button>
        </div>

        <button type="button" className="sidebar-action-row" onClick={onNewConversation}>
          <span className="sidebar-action-icon">
            <SidebarGlyph kind="plus" />
          </span>
          <span>新建会话</span>
        </button>

        <label className="sidebar-search-shell" aria-label="搜索会话">
          <span className="sidebar-search-icon" aria-hidden="true">
            <SidebarGlyph kind="search" />
          </span>
          <input
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            className="sidebar-search-input"
            placeholder="搜索当前会话"
          />
        </label>
      </div>

      <div className="sidebar-section-header">
        <span>最近会话</span>
        <span className="text-[0.74rem] text-[color:var(--studio-text-subtle)]">{conversations.length}</span>
      </div>

      <div className="sidebar-conversation-list min-h-0 flex-1 overflow-y-auto pr-1">
        {conversations.length === 0 ? (
          <div className="px-1 py-4 text-sm leading-7 text-[color:var(--studio-text-muted)]">
            还没有可切换的会话。先从首页输入一个新的教学任务。
          </div>
        ) : (
          conversations.map((conversation) => {
            const active = selectedConversationId === conversation.id;
            return (
              <button
                key={conversation.id}
                type="button"
                className="sidebar-conversation-row"
                data-active={active}
                onClick={() => onSelectConversation(conversation.id)}
              >
                <div className="flex items-start gap-3">
                  <span className="sidebar-message-mark">
                    <SidebarGlyph kind="message" />
                  </span>
                  <div className="min-w-0 flex-1 space-y-1 text-left">
                    <p className="line-clamp-1 text-[1rem] font-semibold leading-7 text-[color:var(--studio-ink)]">
                      {conversation.title}
                    </p>
                    <div className="flex items-center justify-between gap-3 text-[0.75rem] text-[color:var(--studio-text-subtle)]">
                      <span className="truncate">{conversation.modelFamily || "Simulation"}</span>
                      <span>{formatTimestamp(conversation.updatedAt)}</span>
                    </div>
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>

      <div className="sidebar-account-card">
        <div className="flex items-center gap-3">
          <div className="sidebar-avatar">师</div>
          <div>
            <p className="text-[1rem] font-semibold text-[color:var(--studio-ink)]">教师账户</p>
            <p className="text-[0.78rem] text-[color:var(--studio-text-muted)]">ClassSim workspace</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
