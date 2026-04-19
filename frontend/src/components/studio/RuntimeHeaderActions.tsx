import type { ArtifactVersion, RuntimeView } from "../../types/studio";

interface RuntimeHeaderActionsProps {
  versions: ArtifactVersion[];
  activeVersionId: string | null;
  runtimeView: RuntimeView;
  downloading: boolean;
  onChangeVersion: (versionId: string) => void;
  onChangeRuntimeView: (view: RuntimeView) => void;
  onRequestEdit: () => void;
  onToggleFullscreen: () => void;
  onDownload: () => void;
  onClose: () => void;
}

export function RuntimeHeaderActions({
  versions,
  activeVersionId,
  runtimeView,
  downloading,
  onChangeVersion,
  onChangeRuntimeView,
  onRequestEdit,
  onToggleFullscreen,
  onDownload,
  onClose,
}: RuntimeHeaderActionsProps) {
  return (
    <div className="runtime-toolbar">
      <div className="runtime-toolbar-actions">
        <div className="flex items-center gap-2">
          <button type="button" className="toolbar-button" onClick={() => onChangeRuntimeView("preview")} data-active={runtimeView === "preview"}>
            预览
          </button>
          <button type="button" className="toolbar-button" onClick={() => onChangeRuntimeView("code")} data-active={runtimeView === "code"}>
            代码
          </button>
        </div>

        <button type="button" className="toolbar-button" onClick={onRequestEdit}>
          编辑
        </button>
        <button type="button" className="toolbar-button" onClick={onToggleFullscreen}>
          全屏
        </button>
        <button type="button" className="toolbar-button" onClick={onDownload}>
          {downloading ? "下载中..." : "下载"}
        </button>
        <label className="toolbar-select" aria-label="版本">
          <select
            id="runtime-version-select"
            name="runtime-version-select"
            value={activeVersionId ?? ""}
            onChange={(event) => onChangeVersion(event.target.value)}
          >
            {versions.map((version) => (
              <option key={version.id} value={version.id}>
                {version.label}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="toolbar-close-button" onClick={onClose}>
          关闭预览
        </button>
      </div>
    </div>
  );
}
