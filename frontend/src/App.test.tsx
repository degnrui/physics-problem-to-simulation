import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";

function createJsonResponse(payload: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(payload), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    }),
  );
}

function mockFetchWithNewContract() {
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);

    if (url.endsWith("/api/problem-to-simulation/runs") && init?.method === "POST") {
      return createJsonResponse({
        run_id: "run-new",
        status: "queued",
        route: "/simulation/run-new",
        status_url: "/api/problem-to-simulation/runs/run-new",
      });
    }

    if (url.endsWith("/api/problem-to-simulation/runs")) {
      return createJsonResponse({
        items: [
          {
            run_id: "run-1",
            title: "new_simulation",
            status: "completed",
            updated_at: "2026-04-20T09:00:00Z",
            input_profile: "problem_only",
            request_mode: "new_simulation",
          },
        ],
      });
    }

    if (url.endsWith("/api/problem-to-simulation/runs/run-1/result")) {
      return createJsonResponse({
        run_id: "run-1",
        run_state: {
          request_mode: "new_simulation",
          request_profile: { topic_hint: "high-school-physics" },
          workflow_plan: [
            "request_analysis",
            "domain_grounding",
            "instructional_modeling",
            "simulation_design",
            "runtime_package_assembly",
            "code_generation",
            "runtime_validation",
          ],
          active_stage: "completed",
          stage_status: {
            request_analysis: { name: "request_analysis", status: "approved", attempts: 1, score: 100, issues: [] },
            domain_grounding: { name: "domain_grounding", status: "approved", attempts: 1, score: 100, issues: [] },
            instructional_modeling: { name: "instructional_modeling", status: "approved", attempts: 1, score: 100, issues: [] },
            simulation_design: { name: "simulation_design", status: "approved", attempts: 1, score: 100, issues: [] },
            runtime_package_assembly: { name: "runtime_package_assembly", status: "approved", attempts: 1, score: 100, issues: [] },
            code_generation: { name: "code_generation", status: "approved", attempts: 2, score: 100, issues: [] },
            runtime_validation: { name: "runtime_validation", status: "approved", attempts: 1, score: 100, issues: [] },
          },
        },
        artifacts: {
          code_generation: {
            primary_file: "simulation.html",
          },
        },
        approved_artifacts: {
          request_analysis: { input_profile: "problem_only" },
          simulation_design: {
            title: "Physics Runtime Studio",
            controls: [{ id: "play" }],
            charts: [{ id: "state-chart" }],
          },
        },
        runtime_package: {
          required_features: ["canvas", "play", "pause", "reset", "measurement-panel"],
        },
        generated_files: {
          "simulation.html": "<html><body><canvas id='simulation-canvas'></canvas><button>play</button></body></html>",
        },
        delivery_runtime: {
          primary_file: "simulation.html",
          html: "<html><body><canvas id='simulation-canvas'></canvas><button>play</button><button>pause</button><button>reset</button><input type='range' /><section id='measurement-panel'>measurement</section></body></html>",
        },
        execution_trace: [
          { timestamp: "2026-04-20T09:00:00Z", stage: "code_generation", event: "generated" },
          { timestamp: "2026-04-20T09:00:01Z", stage: "runtime_validation", event: "approved" },
        ],
      });
    }

    if (url.endsWith("/api/problem-to-simulation/runs/run-1")) {
      return createJsonResponse({
        run_id: "run-1",
        status: "completed",
        active_stage: "completed",
        workflow_plan: [
          "request_analysis",
          "domain_grounding",
          "instructional_modeling",
          "simulation_design",
          "runtime_package_assembly",
          "code_generation",
          "runtime_validation",
        ],
        stage_status: {
          request_analysis: { name: "request_analysis", status: "approved", attempts: 1, score: 100, issues: [] },
          runtime_validation: { name: "runtime_validation", status: "approved", attempts: 1, score: 100, issues: [] },
        },
        started_at: "2026-04-20T08:59:00Z",
        updated_at: "2026-04-20T09:00:01Z",
        finished_at: "2026-04-20T09:00:01Z",
      });
    }

    if (url.endsWith("/api/problem-to-simulation/runs/run-new")) {
      return createJsonResponse({
        run_id: "run-new",
        status: "queued",
        active_stage: "queued",
        workflow_plan: [],
        stage_status: {},
        started_at: "2026-04-20T09:00:00Z",
        updated_at: "2026-04-20T09:00:00Z",
        finished_at: null,
      });
    }

    if (url.endsWith("/export-html")) {
      return createJsonResponse({
        run_id: "run-1",
        export_mode: "single-file-html",
        download_url: "/download/run-1",
        path: "/exports/run-1.html",
      });
    }

    return Promise.reject(new Error(`Unhandled URL: ${url}`));
  });

  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("app with the new backend contract", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("starts a run from the home page", async () => {
    const fetchMock = mockFetchWithNewContract();
    window.history.pushState({}, "", "/");
    const user = userEvent.setup();

    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Start Run" }));

    await waitFor(() => {
      expect(window.location.pathname).toBe("/simulation/run-new");
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/problem-to-simulation/runs",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("renders stage status, approved artifacts, execution trace, and runtime preview from the new contract", async () => {
    mockFetchWithNewContract();
    window.history.pushState({}, "", "/simulation/run-1");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Workflow Plan" })).toBeInTheDocument();
    expect(screen.getAllByText("request_analysis").length).toBeGreaterThan(0);
    expect(screen.getAllByText("simulation_design").length).toBeGreaterThan(0);
    expect(screen.getByRole("heading", { name: "Approved Artifacts" })).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("Physics Runtime Studio"))).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Execution Trace" })).toBeInTheDocument();
    expect(screen.getAllByText("code_generation").length).toBeGreaterThan(0);
    expect(screen.getByRole("heading", { name: "Runtime Preview" })).toBeInTheDocument();
    expect(screen.getByTitle("delivery-runtime")).toHaveAttribute("srcdoc", expect.stringContaining("simulation-canvas"));
    expect(screen.queryByText("compile_delivery")).not.toBeInTheDocument();
    expect(screen.queryByText("renderer_payload")).not.toBeInTheDocument();
    expect(screen.queryByText("delivery_bundle")).not.toBeInTheDocument();
  });
});
