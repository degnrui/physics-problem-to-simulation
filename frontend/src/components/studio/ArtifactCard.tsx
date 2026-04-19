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
      <div className="artifact-card-inline">
        <h3 className="truncate text-[0.95rem] font-semibold text-[color:var(--studio-ink)]">{artifact.name}</h3>
        <span className="artifact-card-version">{activeVersionLabel}</span>
      </div>
    </button>
  );
}
