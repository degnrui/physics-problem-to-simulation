import { StudioBrand } from "./StudioBrand";
import { TooltipActionIcons } from "./TooltipActionIcons";

interface HomeInputStageProps {
  value: string;
  loading: boolean;
  errorMessage: string | null;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onReturnHome: () => void;
}

export function HomeInputStage({
  value,
  loading,
  errorMessage,
  onChange,
  onSubmit,
  onReturnHome,
}: HomeInputStageProps) {
  return (
    <section className="home-stage">
      <div className="home-stage-inner">
        <button
          type="button"
          className="home-brand-button"
          onClick={onReturnHome}
          aria-label="ClassSim 返回首页"
        >
          <StudioBrand />
        </button>

        <div className="hero-input-shell">
          <textarea
            id="home-prompt"
            name="home-prompt"
            aria-label="题目输入"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            className="hero-input"
            rows={6}
            placeholder="例如：我想把一道关于弹力与摩擦的高中物理题，转成课堂上可操作、可讲评的 simulation。"
          />

          <div className="hero-toolbar">
            <TooltipActionIcons />
            <button
              type="button"
              className="primary-action-button hero-submit-button"
              onClick={onSubmit}
              disabled={loading || !value.trim()}
            >
              {loading ? "生成中..." : "开始生成"}
            </button>
          </div>

          {errorMessage ? <p className="hero-error-message">{errorMessage}</p> : null}
        </div>
      </div>
    </section>
  );
}
