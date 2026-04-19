import type { ArtifactItem, StudioMessage } from "../../types/studio";
import { ArtifactCard } from "./ArtifactCard";

interface ConversationContentPanelProps {
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
      <div className="conversation-scroll-region">
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
            <article
              key={message.id}
              className={
                message.role === "user"
                  ? "message-bubble user message-bubble-chat"
                  : "message-bubble assistant message-bubble-chat"
              }
            >
              <p className="whitespace-pre-wrap text-[0.96rem] leading-7 text-[color:var(--studio-ink)]">
                {message.text}
              </p>
            </article>
          );
        })}
      </div>

      <div className="surface-panel conversation-composer px-5 py-5">
        <textarea
          id="conversation-follow-up"
          name="conversation-follow-up"
          value={followUpValue}
          onChange={(event) => onFollowUpChange(event.target.value)}
          className="studio-input conversation-composer-input min-h-[120px] resize-none"
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
