import { useState } from "react";
import type { InlineEditTarget } from "../../types/studio";

interface InlineEditOverlayProps {
  target: InlineEditTarget;
  onCancel: () => void;
  onSaveDirect: (value: string) => void;
  onSaveAi: (prompt: string) => void;
}

export function InlineEditOverlay({
  target,
  onCancel,
  onSaveDirect,
  onSaveAi,
}: InlineEditOverlayProps) {
  const [directValue, setDirectValue] = useState(target.value);
  const [aiPrompt, setAiPrompt] = useState("");

  return (
    <div
      className="inline-edit-overlay"
      style={{
        top: `${target.anchor.top}px`,
        left: `${target.anchor.left}px`,
      }}
    >
      <div className="space-y-3">
        <div className="space-y-1">
          <p className="text-[0.75rem] uppercase tracking-[0.16em] text-[color:var(--studio-text-subtle)]">Inline Edit</p>
          <h3 className="text-sm font-semibold text-[color:var(--studio-ink)]">{target.label}</h3>
        </div>

        <label className="space-y-2">
          <span className="text-[0.8rem] text-[color:var(--studio-text-muted)]">直接修改</span>
          <input value={directValue} onChange={(event) => setDirectValue(event.target.value)} className="studio-input h-11" />
        </label>
        <button type="button" className="primary-action-button w-full justify-center" onClick={() => onSaveDirect(directValue)}>
          应用文本修改
        </button>

        <label className="space-y-2">
          <span className="text-[0.8rem] text-[color:var(--studio-text-muted)]">AI 描述式修改</span>
          <textarea
            value={aiPrompt}
            onChange={(event) => setAiPrompt(event.target.value)}
            className="studio-input min-h-[88px] resize-none"
            placeholder="例如：把这段说明改得更适合课堂讲评。"
          />
        </label>
        <div className="flex gap-2">
          <button type="button" className="secondary-chip flex-1 justify-center" onClick={onCancel}>
            取消
          </button>
          <button
            type="button"
            className="primary-action-button flex-1 justify-center"
            disabled={!aiPrompt.trim()}
            onClick={() => onSaveAi(aiPrompt)}
          >
            交给 AI 修改
          </button>
        </div>
      </div>
    </div>
  );
}
