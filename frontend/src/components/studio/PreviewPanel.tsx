import { buildHtmlSource } from "../../lib/studio";
import type { ArtifactVersion, InlineEditTarget, RuntimeView } from "../../types/studio";
import { HtmlRuntimeFrame } from "./HtmlRuntimeFrame";
import { InlineEditOverlay } from "./InlineEditOverlay";
import { RuntimeHeaderActions } from "./RuntimeHeaderActions";

interface PreviewPanelProps {
  versions: ArtifactVersion[];
  activeVersion: ArtifactVersion;
  artifactName: string;
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
  onChangeCode: (value: string) => void;
}

export function PreviewPanel({
  versions,
  activeVersion,
  artifactName,
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
  onChangeCode,
}: PreviewPanelProps) {
  const htmlSource = buildHtmlSource(activeVersion);

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

        <div className="preview-panel-body relative min-h-0 flex-1 px-4 pb-4">
          {runtimeView === "preview" ? (
            <HtmlRuntimeFrame title={artifactName} source={htmlSource} />
          ) : (
            <div className="code-editor-shell">
              <textarea
                id="runtime-code-editor"
                name="runtime-code-editor"
                aria-label="HTML 代码编辑器"
                className="code-editor-textarea"
                spellCheck={false}
                value={htmlSource}
                onChange={(event) => onChangeCode(event.target.value)}
              />
            </div>
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
