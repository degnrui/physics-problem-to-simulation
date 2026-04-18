import { formatTimestamp } from "../../lib/studio";
import type { ArtifactItem, StudioMessage } from "../../types/studio";
import { ArtifactCard } from "./ArtifactCard";

interface ConversationContentPanelProps {
  title: string;
  subtitle: string;
  messages: StudioMessage[];
  artifact: ArtifactItem | null;
  activeArtifactId: string | null;
  activeVersionLabel: string;
  followUpValue: string;
  onFollowUpChange: (value: string) => void;
  onSubmitFollowUp: () => void;
  onOpenArtifact: () => void;
}

export function ConversationContentPanel({
  title,
  subtitle,
  messages,
  artifact,
  activeArtifactId,
  activeVersionLabel,
  followUpValue,
  onFollowUpChange,
  onSubmitFollowUp,
  onOpenArtifact,
}: ConversationContentPanelProps) {
  return (
    <section className="studio-center-panel">
      <div className="space-y-3">
        <p className="section-kicker">Current Conversation</p>
        <h1 className="font-display text-[1.9rem] font-semibold leading-[1.08] tracking-[-0.04em] text-[color:var(--studio-ink)]">
          {title}
        </h1>
        <p className="max-w-[52rem] text-[0.98rem] leading-8 text-[color:var(--studio-text-muted)]">{subtitle}</p>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto pr-1">
        {messages.map((message) => {
          if (message.kind === "artifact" && artifact) {
            return (
              <ArtifactCard
                key={message.id}
                artifact={artifact}
                active={activeArtifactId === artifact.id}
                activeVersionLabel={activeVersionLabel}
                onOpen={onOpenArtifact}
              />
            );
          }

          return (
            <article key={message.id} className={message.role === "user" ? "message-bubble user" : "message-bubble"}>
              <div className="flex items-center justify-between gap-3">
                <span className="text-[0.78rem] uppercase tracking-[0.16em] text-[color:var(--studio-text-subtle)]">
                  {message.role === "user" ? "Teacher" : message.role === "assistant" ? "Studio" : "Context"}
                </span>
                <span className="text-[0.72rem] text-[color:var(--studio-text-subtle)]">{formatTimestamp(message.createdAt)}</span>
              </div>
              <p className="mt-3 whitespace-pre-wrap text-[0.98rem] leading-8 text-[color:var(--studio-ink)]">
                {message.text}
              </p>
            </article>
          );
        })}
      </div>

      <div className="surface-panel mt-2 grid gap-4 px-5 py-5">
        <div className="space-y-2">
          <p className="text-sm font-medium text-[color:var(--studio-ink)]">继续修改</p>
          <p className="text-[0.82rem] leading-7 text-[color:var(--studio-text-muted)]">
            重大逻辑或教学结构问题默认从这里发起，右侧 runtime 主要承担验证和局部微调。
          </p>
        </div>
        <textarea
          value={followUpValue}
          onChange={(event) => onFollowUpChange(event.target.value)}
          className="studio-input min-h-[120px] resize-none"
          placeholder="继续描述你想调整的物理逻辑、课堂节奏、讲评顺序或视觉表达。"
        />
        <div className="flex justify-end">
          <button
            type="button"
            className="primary-action-button"
            disabled={!followUpValue.trim()}
            onClick={onSubmitFollowUp}
          >
            生成新版本
          </button>
        </div>
      </div>
    </section>
  );
}
