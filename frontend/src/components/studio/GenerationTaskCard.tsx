import type { StagePresentation } from "../../types/studio";

interface GenerationTaskCardProps {
  stage: StagePresentation;
  percent: number;
}

export function GenerationTaskCard({ stage, percent }: GenerationTaskCardProps) {
  return (
    <article className="generation-task-card">
      <div className="generation-card-mark">{stage.glyph}</div>
      <div className="space-y-3">
        <p className="section-kicker">{stage.progressLabel}</p>
        <h2 className="font-display text-[2rem] font-semibold leading-[1.05] tracking-[-0.04em] text-[color:var(--studio-ink)]">
          {stage.title}
        </h2>
        <p className="max-w-[38rem] text-[1rem] leading-8 text-[color:var(--studio-text-muted)]">{stage.description}</p>
        <p className="max-w-[34rem] text-[0.95rem] leading-7 text-[color:var(--studio-text-subtle)]">{stage.detail}</p>
      </div>
      <div className="surface-soft mt-6 grid gap-3 px-5 py-4 text-left">
        <div className="flex items-center justify-between text-sm text-[color:var(--studio-text-muted)]">
          <span>当前进度</span>
          <span>{percent}%</span>
        </div>
        <div className="h-2 rounded-full bg-[color:var(--studio-line-soft)]">
          <div className="h-2 rounded-full bg-[color:var(--studio-accent)] transition-[width] duration-500" style={{ width: `${percent}%` }} />
        </div>
      </div>
    </article>
  );
}
