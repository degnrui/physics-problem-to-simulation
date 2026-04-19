import type { ConversationSummary } from "../../types/studio";
import { StudioBrand } from "./StudioBrand";

interface CollapsibleConversationSidebarProps {
  conversations: ConversationSummary[];
  selectedConversationId: string | null;
  query: string;
  onQueryChange: (value: string) => void;
  onSelectConversation: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
  onNewConversation: () => void;
  onReturnHome: () => void;
  onCollapse: () => void;
}

function SidebarGlyph({ kind }: { kind: "collapse" | "search" | "plus" | "message" | "delete" }) {
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

  if (kind === "delete") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true" className="rail-glyph">
        <path d="M9 4.5h6M5.5 7h13M9.5 7V5.8c0-.72.58-1.3 1.3-1.3h2.4c.72 0 1.3.58 1.3 1.3V7M8.1 10.2v7.3M12 10.2v7.3M15.9 10.2v7.3M7.4 19.5h9.2c.6 0 1.1-.46 1.15-1.06L18.5 7H5.5l.75 11.44c.04.6.55 1.06 1.15 1.06Z" />
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
  onDeleteConversation,
  onNewConversation,
  onReturnHome,
  onCollapse,
}: CollapsibleConversationSidebarProps) {
  return (
    <aside className="conversation-sidebar">
      <div className="sidebar-top-shell">
        <div className="sidebar-header-row">
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
          <span>新建聊天</span>
        </button>

        <label className="sidebar-search-shell" aria-label="搜索聊天">
          <span className="sidebar-search-icon" aria-hidden="true">
            <SidebarGlyph kind="search" />
          </span>
          <input
            id="conversation-search"
            name="conversation-search"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            className="sidebar-search-input"
            placeholder="搜索聊天"
          />
        </label>
      </div>

      <div className="sidebar-section-header">
        <span>历史聊天</span>
      </div>

      <div className="sidebar-conversation-list min-h-0 flex-1 overflow-y-auto pr-1">
        {conversations.length === 0 ? null : (
          conversations.map((conversation) => {
            const active = selectedConversationId === conversation.id;
            return (
              <div key={conversation.id} className="sidebar-conversation-entry" data-active={active}>
                <button
                  type="button"
                  className="sidebar-conversation-row"
                  data-active={active}
                  onClick={() => onSelectConversation(conversation.id)}
                >
                  <div className="flex items-start gap-3">
                    <span className="sidebar-message-mark">
                      <SidebarGlyph kind="message" />
                    </span>
                    <div className="min-w-0 flex-1 text-left">
                      <p className="line-clamp-1 text-[0.75rem] font-semibold leading-5 text-[color:var(--studio-ink)]">
                        {conversation.title}
                      </p>
                    </div>
                  </div>
                </button>

                <button
                  type="button"
                  className="sidebar-delete-button with-tooltip"
                  onClick={() => onDeleteConversation(conversation.id)}
                  aria-label={`删除会话 ${conversation.title}`}
                  data-tooltip="删除会话"
                >
                  <SidebarGlyph kind="delete" />
                </button>
              </div>
            );
          })
        )}
      </div>

      <div className="sidebar-account-card">
        <div className="flex items-center gap-3">
          <div className="sidebar-avatar" aria-hidden="true">
            <svg viewBox="0 0 24 24" className="sidebar-avatar-glyph">
              <circle cx="12" cy="8.8" r="3.2" />
              <path d="M6.8 18c.9-2.8 3.2-4.4 5.2-4.4s4.3 1.6 5.2 4.4" />
            </svg>
          </div>
          <div>
            <p className="text-[1rem] font-semibold text-[color:var(--studio-ink)]">dengrui</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
