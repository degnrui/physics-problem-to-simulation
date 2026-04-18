import type { StagePresentation } from "../../types/studio";
import { GenerationTaskCard } from "./GenerationTaskCard";

interface GenerationStagePlayerProps {
  stage: StagePresentation;
  percent: number;
}

export function GenerationStagePlayer({ stage, percent }: GenerationStagePlayerProps) {
  return (
    <section className="flex min-h-screen flex-col justify-center px-8 py-10 lg:px-12">
      <div className="mx-auto flex w-full max-w-[58rem] flex-col gap-8">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="section-kicker">Generation Transition</p>
            <p className="text-sm leading-7 text-[color:var(--studio-text-muted)]">
              一次只突出一个当前任务，不使用纵向步骤打勾列表。
            </p>
          </div>
          <p className="text-sm font-medium text-[color:var(--studio-accent-ink)]">{stage.progressLabel}</p>
        </div>

        <div className="stage-progress-strip">
          <div className="h-full rounded-full bg-[color:var(--studio-accent)] transition-[width] duration-500" style={{ width: `${percent}%` }} />
        </div>

        <GenerationTaskCard stage={stage} percent={percent} />
      </div>
    </section>
  );
}
