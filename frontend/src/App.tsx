import { useEffect, useState } from "react";
import {
  createRun,
  getRunResult,
  getRunStatus,
  listRuns,
  type RunListItem,
  type RunResultResponse,
  type RunStatusResponse,
} from "./lib/api";

const SAMPLE_PROBLEM =
  "如图所示，两根相同的橡皮绳连接物块，沿 AB 中垂线拉至 O 点后释放。请生成一个适合课堂讲评的 simulation，突出回复力方向、摩擦耗能和教学观察顺序。";

type RouteState = { name: "home" } | { name: "conversation"; runId: string };

function parseRoute(pathname: string): RouteState {
  const segments = pathname.split("/").filter(Boolean);
  if (segments[0] === "simulation" && segments[1]) {
    return { name: "conversation", runId: segments[1] };
  }
  return { name: "home" };
}

function navigateTo(path: string) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function summarizeArtifact(value: unknown): string {
  if (value === null || value === undefined) {
    return "empty";
  }
  if (typeof value === "string") {
    return value;
  }
  if (Array.isArray(value)) {
    return value.slice(0, 3).map((item) => summarizeArtifact(item)).join(", ");
  }
  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    if (typeof record.title === "string") {
      return record.title;
    }
    if (typeof record.request_mode === "string") {
      return record.request_mode;
    }
    return Object.keys(record).slice(0, 4).join(", ");
  }
  return String(value);
}

export default function App() {
  const [route, setRoute] = useState<RouteState>(() => parseRoute(window.location.pathname));
  const [draftPrompt, setDraftPrompt] = useState(SAMPLE_PROBLEM);
  const [creatingRun, setCreatingRun] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [runs, setRuns] = useState<RunListItem[]>([]);
  const [statusMap, setStatusMap] = useState<Record<string, RunStatusResponse | null>>({});
  const [resultMap, setResultMap] = useState<Record<string, RunResultResponse | null>>({});

  useEffect(() => {
    const onPopState = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  useEffect(() => {
    let cancelled = false;
    listRuns()
      .then((payload) => {
        if (!cancelled) {
          setRuns(payload.items);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setRuns([]);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [route]);

  useEffect(() => {
    if (route.name !== "conversation") {
      return undefined;
    }

    let cancelled = false;
    let timer: number | undefined;

    const poll = async () => {
      try {
        const status = await getRunStatus(route.runId);
        if (cancelled) {
          return;
        }
        setStatusMap((current) => ({ ...current, [route.runId]: status }));
        if (status.status === "completed") {
          const result = await getRunResult(route.runId);
          if (!cancelled) {
            setResultMap((current) => ({ ...current, [route.runId]: result }));
          }
          return;
        }
        if (status.status !== "failed") {
          timer = window.setTimeout(poll, 600);
        }
      } catch {
        if (!cancelled) {
          timer = window.setTimeout(poll, 900);
        }
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timer) {
        window.clearTimeout(timer);
      }
    };
  }, [route]);

  async function handleCreateRun() {
    if (!draftPrompt.trim()) {
      return;
    }
    setCreatingRun(true);
    setError(null);
    try {
      const payload = await createRun(draftPrompt.trim());
      navigateTo(payload.route);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Failed to start run");
    } finally {
      setCreatingRun(false);
    }
  }

  const currentStatus = route.name === "conversation" ? statusMap[route.runId] ?? null : null;
  const currentResult = route.name === "conversation" ? resultMap[route.runId] ?? null : null;
  const workflowPlan = currentResult?.run_state.workflow_plan ?? currentStatus?.workflow_plan ?? [];
  const stageStatus = currentResult?.run_state.stage_status ?? currentStatus?.stage_status ?? {};

  return (
    <div className="app-shell">
      <aside className="surface-panel" style={{ width: 280, margin: 24, padding: 20 }}>
        <h2 className="font-display" style={{ marginTop: 0 }}>Runs</h2>
        <button
          className="secondary-chip"
          type="button"
          onClick={() => navigateTo("/")}
          style={{ marginBottom: 16 }}
        >
          New Run
        </button>
        <div style={{ display: "grid", gap: 10 }}>
          {runs.map((item) => (
            <button
              key={item.run_id}
              className="surface-soft"
              type="button"
              style={{ padding: 12, textAlign: "left" }}
              onClick={() => navigateTo(`/simulation/${item.run_id}`)}
            >
              <strong>{item.title}</strong>
              <div>{item.status}</div>
            </button>
          ))}
        </div>
      </aside>

      <main style={{ flex: 1, padding: 24 }}>
        {route.name === "home" ? (
          <section className="surface-panel" style={{ padding: 24 }}>
            <h1 className="font-display">Physics Problem to Simulation</h1>
            <p>Submit a physics prompt and generate a reviewed runtime package.</p>
            <label htmlFor="problem-input" style={{ display: "block", marginBottom: 8 }}>
              Problem Input
            </label>
            <textarea
              id="problem-input"
              aria-label="Problem Input"
              className="studio-input"
              rows={8}
              value={draftPrompt}
              onChange={(event) => setDraftPrompt(event.target.value)}
            />
            <div style={{ marginTop: 16, display: "flex", gap: 12, alignItems: "center" }}>
              <button className="primary-action-button" type="button" onClick={handleCreateRun} disabled={creatingRun}>
                {creatingRun ? "Starting..." : "Start Run"}
              </button>
              {error ? <span>{error}</span> : null}
            </div>
          </section>
        ) : (
          <section style={{ display: "grid", gap: 16 }}>
            <section className="surface-panel" style={{ padding: 20 }}>
              <h1 className="font-display" style={{ marginTop: 0 }}>Run Overview</h1>
              <p>Status: {currentStatus?.status ?? "loading"}</p>
              <p>Active Stage: {currentStatus?.active_stage ?? currentResult?.run_state.active_stage ?? "loading"}</p>
            </section>

            <section className="surface-panel" style={{ padding: 20 }}>
              <h2 className="font-display" style={{ marginTop: 0 }}>Workflow Plan</h2>
              <ul>
                {workflowPlan.map((stage) => {
                  const info = stageStatus[stage];
                  return (
                    <li key={stage}>
                      <strong>{stage}</strong> - {info?.status ?? "pending"} - attempts {info?.attempts ?? 0}
                    </li>
                  );
                })}
              </ul>
            </section>

            <section className="surface-panel" style={{ padding: 20 }}>
              <h2 className="font-display" style={{ marginTop: 0 }}>Approved Artifacts</h2>
              <ul>
                {Object.entries(currentResult?.approved_artifacts ?? {}).map(([name, value]) => (
                  <li key={name}>
                    <strong>{name}</strong>: {summarizeArtifact(value)}
                  </li>
                ))}
              </ul>
            </section>

            <section className="surface-panel" style={{ padding: 20 }}>
              <h2 className="font-display" style={{ marginTop: 0 }}>Current Artifacts</h2>
              <ul>
                {Object.entries(currentResult?.artifacts ?? {}).map(([name, value]) => (
                  <li key={name}>
                    <strong>{name}</strong>: {summarizeArtifact(value)}
                  </li>
                ))}
              </ul>
            </section>

            <section className="surface-panel" style={{ padding: 20 }}>
              <h2 className="font-display" style={{ marginTop: 0 }}>Execution Trace</h2>
              <ul>
                {(currentResult?.execution_trace ?? []).map((entry, index) => {
                  const event = entry as Record<string, unknown>;
                  return (
                  <li key={`${String(event.stage)}-${String(event.event)}-${index}`}>
                    <strong>{String(event.stage)}</strong> - {String(event.event)}
                  </li>
                  );
                })}
              </ul>
            </section>

            <section className="surface-panel" style={{ padding: 20 }}>
              <h2 className="font-display" style={{ marginTop: 0 }}>Runtime Preview</h2>
              <iframe
                title="delivery-runtime"
                style={{ width: "100%", minHeight: 320, border: "1px solid var(--studio-line)" }}
                srcDoc={currentResult?.delivery_runtime?.html ?? ""}
              />
            </section>

            <section className="surface-panel" style={{ padding: 20 }}>
              <h2 className="font-display" style={{ marginTop: 0 }}>Generated Files</h2>
              {Object.entries(currentResult?.generated_files ?? {}).map(([name, content]) => (
                <article key={name} style={{ marginBottom: 16 }}>
                  <h3>{name}</h3>
                  <pre style={{ overflowX: "auto", whiteSpace: "pre-wrap" }}>{content}</pre>
                </article>
              ))}
            </section>
          </section>
        )}
      </main>
    </div>
  );
}
