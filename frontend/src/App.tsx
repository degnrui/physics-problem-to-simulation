import { useState } from "react";
import { ProblemInput } from "./components/ProblemInput";
import { PipelinePreview } from "./components/PipelinePreview";
import { submitProblem, type ProblemToSimulationResponse } from "./lib/api";

const SAMPLE_PROBLEM =
  "如图所示电路中，电源电压保持不变，滑动变阻器滑片向右移动时，电流表示数减小，电压表示数增大。请分析电路连接方式，并说明各物理量变化。";

export default function App() {
  const [text, setText] = useState(SAMPLE_PROBLEM);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProblemToSimulationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    try {
      const response = await submitProblem(text);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Scaffold v0.1</p>
        <h1>Physics Problem to Simulation</h1>
        <p className="subtitle">
          第一版开发壳，先稳定题目到结构化模型与 scene 的转换通路。
        </p>
      </header>

      <div className="grid">
        <ProblemInput value={text} onChange={setText} onSubmit={handleSubmit} loading={loading} />
        <section className="panel">
          <h2>Simulation Area</h2>
          <p>这里预留给后续的可交互 simulation 渲染器。</p>
          <div className="placeholder">scene renderer placeholder</div>
          {error ? <p className="error">{error}</p> : null}
        </section>
        <PipelinePreview title="Structured Problem" data={result?.structured_problem ?? {}} />
        <PipelinePreview title="Physics Model" data={result?.physics_model ?? {}} />
        <PipelinePreview title="Scene" data={result?.scene ?? {}} />
      </div>
    </main>
  );
}

