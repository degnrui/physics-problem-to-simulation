import { useEffect, useState } from "react";
import { ProblemInput } from "./components/ProblemInput";
import { RecentSimulationList } from "./components/RecentSimulationList";
import { SimulationWorkspaceLayout } from "./components/SimulationWorkspaceLayout";
import {
  createHtmlExport,
  createRun,
  exportDownloadUrl,
  getRunResult,
  getRunStatus,
  listRuns,
  type RunListItem,
  type RunResultResponse,
  type RunStatusResponse,
} from "./lib/api";

const SAMPLE_PROBLEM =
  "如图所示，两根相同的橡皮绳，一端连接质量为m的物块，另一端固定在水平桌面上的A、B两点。物块处于AB连线的中点C时，橡皮绳为原长。现将物块沿AB中垂线水平拉至桌面上的O点静止释放。已知CO距离为L，物块与桌面间的动摩擦因数为μ，橡皮绳始终处于弹性限度内，不计空气阻力。";

type RouteState = { name: "home" } | { name: "simulation"; runId: string };
type InspectorTabId = "summary" | "artifacts" | "validation" | "logs";

function parseRoute(pathname: string): RouteState {
  const segments = pathname.split("/").filter(Boolean);
  if (segments[0] === "simulation" && segments[1]) {
    return { name: "simulation", runId: segments[1] };
  }
  return { name: "home" };
}

function navigateTo(path: string) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export default function App() {
  const [route, setRoute] = useState<RouteState>(() => parseRoute(window.location.pathname));

  useEffect(() => {
    const onPopState = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  if (route.name === "simulation") {
    return <SimulationWorkspacePage runId={route.runId} onNavigate={navigateTo} />;
  }

  return <SimulationLauncherPage onNavigate={navigateTo} />;
}

function SimulationLauncherPage({ onNavigate }: { onNavigate: (path: string) => void }) {
  const [text, setText] = useState(SAMPLE_PROBLEM);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [recentRuns, setRecentRuns] = useState<RunListItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listRuns()
      .then((payload) => {
        if (!cancelled) {
          setRecentRuns(payload.items);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setListLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    try {
      const response = await createRun(text);
      onNavigate(response.route);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="launcher-shell">
      <header className="launcher-hero">
        <div className="hero-copy">
          <p className="eyebrow">Simulation Launcher</p>
          <h1>Physics Problem to Simulation</h1>
          <p className="subtitle">
            借鉴 OpenMAIC 的信息架构，但主对象固定为 simulation。首页只负责新建和继续，
            真正的生成、交互、验证与导出都进入同一个 simulation workspace。
          </p>
        </div>
        <div className="hero-summary-card">
          <p className="hero-summary-label">Workspace Model</p>
          <h2>单一主舞台</h2>
          <p>提交题目后直接进入 simulation workspace，在同一路由内经历生成中、完成、失败和导出。</p>
        </div>
      </header>

      <section className="launcher-grid">
        <section className="panel launcher-create-panel">
          <p className="eyebrow">New Simulation</p>
          <h2>创建新的 Simulation</h2>
          <ProblemInput value={text} onChange={setText} onSubmit={handleSubmit} loading={loading} />
          {error ? <p className="error">{error}</p> : null}
        </section>

        <RecentSimulationList
          items={recentRuns}
          loading={listLoading}
          onOpen={(runId) => onNavigate(`/simulation/${runId}`)}
        />
      </section>
    </main>
  );
}

function SimulationWorkspacePage({
  runId,
  onNavigate,
}: {
  runId: string;
  onNavigate: (path: string) => void;
}) {
  const [status, setStatus] = useState<RunStatusResponse | null>(null);
  const [result, setResult] = useState<RunResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [activeTab, setActiveTab] = useState<InspectorTabId>("summary");

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;

    async function poll() {
      try {
        const payload = await getRunStatus(runId);
        if (cancelled) {
          return;
        }
        setStatus(payload);
        if (payload.status === "completed") {
          const runResult = await getRunResult(runId);
          if (!cancelled) {
            setResult(runResult);
          }
          return;
        }
        if (payload.status !== "failed") {
          timer = window.setTimeout(poll, 900);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      }
    }

    poll();

    return () => {
      cancelled = true;
      if (timer) {
        window.clearTimeout(timer);
      }
    };
  }, [runId]);

  async function handleExport() {
    setExporting(true);
    setError(null);
    try {
      await createHtmlExport(runId);
      window.location.href = exportDownloadUrl(runId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setExporting(false);
    }
  }

  return (
    <SimulationWorkspaceLayout
      runId={runId}
      status={status}
      result={result}
      error={error}
      exporting={exporting}
      activeTab={activeTab}
      onBack={() => onNavigate("/")}
      onExport={handleExport}
      onChangeTab={setActiveTab}
    />
  );
}
