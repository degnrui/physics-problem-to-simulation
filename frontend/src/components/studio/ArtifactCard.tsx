import type { ArtifactItem } from "../../types/studio";

interface ArtifactCardProps {
  artifact: ArtifactItem;
  active: boolean;
  activeVersionLabel: string;
  onOpen: () => void;
}

export function ArtifactCard({ artifact, active, activeVersionLabel, onOpen }: ArtifactCardProps) {
  return (
    <button
      type="button"
      className={active ? "artifact-card-button active" : "artifact-card-button"}
      onClick={onOpen}
      aria-label={artifact.name}
      data-active={String(active)}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1 text-left">
          <p className="text-[0.75rem] uppercase tracking-[0.18em] text-[color:var(--studio-text-subtle)]">Artifact</p>
          <h3 className="text-[1rem] font-semibold text-[color:var(--studio-ink)]">{artifact.name}</h3>
          <p className="max-w-[34rem] text-sm leading-7 text-[color:var(--studio-text-muted)]">{artifact.summary}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className="secondary-chip">{artifact.fileType}</span>
          <span className="text-[0.75rem] text-[color:var(--studio-text-subtle)]">{activeVersionLabel}</span>
        </div>
      </div>
    </button>
  );
}
