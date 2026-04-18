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
    <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[color:var(--studio-line)] px-5 py-4">
      <div className="flex items-center gap-2">
        <button type="button" className="toolbar-button" onClick={() => onChangeRuntimeView("preview")} data-active={runtimeView === "preview"}>
          预览
        </button>
        <button type="button" className="toolbar-button" onClick={() => onChangeRuntimeView("code")} data-active={runtimeView === "code"}>
          代码
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button type="button" className="toolbar-button" onClick={onRequestEdit}>
          编辑
        </button>
        <button type="button" className="toolbar-button" onClick={onToggleFullscreen}>
          全屏
        </button>
        <button type="button" className="toolbar-button" onClick={onDownload}>
          {downloading ? "下载中..." : "下载"}
        </button>
        <label className="toolbar-select">
          <span className="text-[0.78rem] uppercase tracking-[0.14em] text-[color:var(--studio-text-subtle)]">版本</span>
          <select value={activeVersionId ?? ""} onChange={(event) => onChangeVersion(event.target.value)}>
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
