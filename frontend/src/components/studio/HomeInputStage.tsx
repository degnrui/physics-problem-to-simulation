import { StudioBrand } from "./StudioBrand";
import { TooltipActionIcons } from "./TooltipActionIcons";

interface HomeInputStageProps {
  value: string;
  loading: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onReturnHome: () => void;
}

export function HomeInputStage({ value, loading, onChange, onSubmit, onReturnHome }: HomeInputStageProps) {
  return (
    <section className="flex min-h-screen flex-col justify-center px-8 py-10 lg:px-12">
      <div className="mx-auto flex w-full max-w-[56rem] flex-col items-center text-center">
        <button
          type="button"
          className="home-brand-button"
          onClick={onReturnHome}
          aria-label="ClassSim 返回首页"
        >
          <StudioBrand />
        </button>

        <div className="hero-input-shell mt-10 w-full">
          <textarea
            value={value}
            onChange={(event) => onChange(event.target.value)}
            className="hero-input"
            rows={8}
            placeholder="例如：我想把一道关于弹力与摩擦的高中物理题，转成课堂上可操作、可讲评的 simulation。"
          />

          <div className="mt-5 flex items-end justify-between gap-4">
            <TooltipActionIcons />
            <button
              type="button"
              className="primary-action-button"
              onClick={onSubmit}
              disabled={loading || !value.trim()}
            >
              {loading ? "生成中..." : "开始生成"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
