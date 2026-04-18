import { buildHtmlSource } from "../../lib/studio";
import type { ArtifactVersion, InlineEditTarget, RuntimeView } from "../../types/studio";
import { InlineEditOverlay } from "./InlineEditOverlay";
import { RuntimeHeaderActions } from "./RuntimeHeaderActions";
import { SimulationRuntimePanel } from "./SimulationRuntimePanel";

interface PreviewPanelProps {
  versions: ArtifactVersion[];
  activeVersion: ArtifactVersion;
  runtimeView: RuntimeView;
  downloading: boolean;
  inlineEditTarget: InlineEditTarget | null;
  onChangeVersion: (versionId: string) => void;
  onChangeRuntimeView: (view: RuntimeView) => void;
  onRequestEdit: (target: InlineEditTarget) => void;
  onRequestPrimaryEdit: () => void;
  onToggleFullscreen: () => void;
  onDownload: () => void;
  onClose: () => void;
  onCancelInlineEdit: () => void;
  onSaveDirectEdit: (value: string) => void;
  onSaveAiEdit: (prompt: string) => void;
}

export function PreviewPanel({
  versions,
  activeVersion,
  runtimeView,
  downloading,
  inlineEditTarget,
  onChangeVersion,
  onChangeRuntimeView,
  onRequestEdit,
  onRequestPrimaryEdit,
  onToggleFullscreen,
  onDownload,
  onClose,
  onCancelInlineEdit,
  onSaveDirectEdit,
  onSaveAiEdit,
}: PreviewPanelProps) {
  return (
    <aside className="preview-panel" data-testid="preview-panel">
      <div className="relative flex h-full min-h-screen flex-col">
        <RuntimeHeaderActions
          versions={versions}
          activeVersionId={activeVersion.id}
          runtimeView={runtimeView}
          downloading={downloading}
          onChangeVersion={onChangeVersion}
          onChangeRuntimeView={onChangeRuntimeView}
          onRequestEdit={onRequestPrimaryEdit}
          onToggleFullscreen={onToggleFullscreen}
          onDownload={onDownload}
          onClose={onClose}
        />

        <div className="relative min-h-0 flex-1 overflow-y-auto px-5 py-5">
          {runtimeView === "preview" ? (
            <SimulationRuntimePanel document={activeVersion.document} onRequestEdit={onRequestEdit} />
          ) : (
            <pre className="code-preview-shell">{buildHtmlSource(activeVersion)}</pre>
          )}

          {runtimeView === "preview" && inlineEditTarget ? (
            <InlineEditOverlay
              target={inlineEditTarget}
              onCancel={onCancelInlineEdit}
              onSaveDirect={onSaveDirectEdit}
              onSaveAi={onSaveAiEdit}
            />
          ) : null}
        </div>
      </div>
    </aside>
  );
}
