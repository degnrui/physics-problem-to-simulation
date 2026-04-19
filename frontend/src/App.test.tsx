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

function mockFetchWithRunState() {
  let deleted = false;

  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);

    if (url.endsWith("/api/problem-to-simulation/runs")) {
      return createJsonResponse({
        items: deleted
          ? []
          : [
              {
                run_id: "run-1",
                title: "双绳弹力位移演示",
                status: "completed",
                updated_at: "2026-04-18T15:00:00Z",
                problem_family: "elastic-motion",
                model_family: "双绳弹力模型",
                simulation_mode: "interactive",
                export_ready: true,
              },
            ],
      });
    }

    if (url.endsWith("/api/problem-to-simulation/runs/run-1") && init?.method === "DELETE") {
      deleted = true;
      return createJsonResponse({
        run_id: "run-1",
        deleted: true,
      });
    }

    if (url.endsWith("/api/problem-to-simulation/runs/run-1/result")) {
      return createJsonResponse({
        run_id: "run-1",
        planner: { model_family: "双绳弹力模型" },
        task_plan: {},
        problem_profile: { summary: "双绳弹力位移演示" },
        physics_model: { key_relation: "F=2Tcosθ" },
        teaching_plan: { objective: "理解回复力与位移的关系" },
        scene_spec: {
          scene_type: "elastic-motion",
          template_id: "elastic-restoring-motion-v1",
          controls: [],
          parameters: {
            derived_quantities: {
              "合力方向": "始终指向平衡位置",
            },
          },
        },
        simulation_spec: {
          template_id: "elastic-restoring-motion-v1",
        },
        simulation_blueprint: {},
        renderer_payload: null,
        delivery_bundle: {
          teacher_script: ["观察合力方向", "比较位移与回复力变化"],
          observation_targets: ["回复力", "摩擦耗能"],
        },
        validation_report: {
          export_ready: true,
          ready_for_delivery: true,
        },
        task_log: [],
      });
    }

    if (url.endsWith("/api/problem-to-simulation/runs/run-1")) {
      return createJsonResponse({
        run_id: "run-1",
        status: "completed",
        current_stage: "编译 simulation",
        current_step_index: 4,
        total_steps: 5,
        percent: 100,
        started_at: "2026-04-18T14:58:00Z",
        updated_at: "2026-04-18T15:00:00Z",
        finished_at: "2026-04-18T15:00:00Z",
        steps: [
          { id: "summary", label: "需求摘要", status: "completed", artifacts_written: [], error: "" },
          { id: "model", label: "物理模型", status: "completed", artifacts_written: [], error: "" },
          { id: "teaching", label: "教学动作", status: "completed", artifacts_written: [], error: "" },
          { id: "layout", label: "页面内容", status: "completed", artifacts_written: [], error: "" },
          { id: "compile", label: "编译 simulation", status: "completed", artifacts_written: ["simulation-runtime.html"], error: "" },
        ],
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

describe("simulation studio shell", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("renders the home input stage without a preview panel", async () => {
    mockFetchWithRunState();
    window.history.pushState({}, "", "/");

    render(<App />);

    expect(await screen.findByText("ClassSim")).toBeInTheDocument();
    expect(screen.queryByText(/teacher simulation studio/i)).not.toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "把物理题目转成可教学的 simulation" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByLabelText("模板入口")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("生成模式")).not.toBeInTheDocument();
    expect(screen.queryByTestId("preview-panel")).not.toBeInTheDocument();
    expect(screen.queryByText("双绳弹力位移演示")).not.toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "题目输入" })).toHaveValue(
      "如图所示，两根相同的橡皮绳连接物块，沿 AB 中垂线拉至 O 点后释放。请生成一个适合课堂讲评的 simulation，突出回复力方向、摩擦耗能和教学观察顺序。",
    );
  });

  it("starts a run directly from the home stage with the starter prompt", async () => {
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
        return createJsonResponse({ items: [] });
      }

      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState({}, "", "/");
    const user = userEvent.setup();

    render(<App />);

    const submitButton = await screen.findByRole("button", { name: "开始生成" });
    expect(submitButton).toBeEnabled();

    await user.click(submitButton);

    await waitFor(() => {
      expect(window.location.pathname).toBe("/simulation/run-new");
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/problem-to-simulation/runs",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("starts a run after entering a custom prompt", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);

      if (url.endsWith("/api/problem-to-simulation/runs") && init?.method === "POST") {
        return createJsonResponse({
          run_id: "run-custom",
          status: "queued",
          route: "/simulation/run-custom",
          status_url: "/api/problem-to-simulation/runs/run-custom",
        });
      }

      if (url.endsWith("/api/problem-to-simulation/runs")) {
        return createJsonResponse({ items: [] });
      }

      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState({}, "", "/");
    const user = userEvent.setup();

    render(<App />);

    const promptInput = screen.getByRole("textbox", { name: "题目输入" });
    await user.clear(promptInput);
    await user.type(promptInput, "请把平抛运动题做成课堂演示 simulation");
    await user.click(screen.getByRole("button", { name: "开始生成" }));

    await waitFor(() => {
      expect(window.location.pathname).toBe("/simulation/run-custom");
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/problem-to-simulation/runs",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          text: "请把平抛运动题做成课堂演示 simulation",
          mode: "llm-assisted",
        }),
      }),
    );
  });

  it("shows an error message when run creation fails", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);

      if (url.endsWith("/api/problem-to-simulation/runs") && init?.method === "POST") {
        return Promise.resolve(
          new Response("backend unavailable", {
            status: 503,
            headers: { "Content-Type": "text/plain" },
          }),
        );
      }

      if (url.endsWith("/api/problem-to-simulation/runs")) {
        return createJsonResponse({ items: [] });
      }

      return Promise.reject(new Error(`Unhandled URL: ${url}`));
    });

    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState({}, "", "/");
    const user = userEvent.setup();

    render(<App />);

    const promptInput = screen.getByRole("textbox", { name: "题目输入" });
    await user.clear(promptInput);
    await user.type(promptInput, "测试失败提示");
    await user.click(screen.getByRole("button", { name: "开始生成" }));

    expect(await screen.findByText("生成失败，请检查后端服务或稍后重试。")).toBeInTheDocument();
    expect(window.location.pathname).toBe("/");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/problem-to-simulation/runs",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("opens the preview panel automatically when a run is completed", async () => {
    mockFetchWithRunState();
    window.history.pushState({}, "", "/simulation/run-1");

    render(<App />);

    expect(await screen.findByTestId("preview-panel")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "simulation-runtime.html" })).toHaveAttribute(
      "data-active",
      "true",
    );
  });

  it("closes and reopens preview from the artifact card", async () => {
    mockFetchWithRunState();
    window.history.pushState({}, "", "/simulation/run-1");
    const user = userEvent.setup();

    render(<App />);

    expect(await screen.findByTestId("preview-panel")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "关闭预览" }));

    await waitFor(() => {
      expect(screen.queryByTestId("preview-panel")).not.toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "simulation-runtime.html" }));

    expect(await screen.findByTestId("preview-panel")).toBeInTheDocument();
  });

  it("updates the rendered html after editing code mode", async () => {
    mockFetchWithRunState();
    window.history.pushState({}, "", "/simulation/run-1");
    const user = userEvent.setup();

    render(<App />);

    expect(await screen.findByTestId("preview-panel")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "代码" }));

    const editor = screen.getByRole("textbox", { name: "HTML 代码编辑器" });
    const nextSource = "<!DOCTYPE html><html lang=\"zh-CN\"><body><main>测试代码预览</main></body></html>";
    await user.clear(editor);
    await user.type(editor, nextSource);

    await user.click(screen.getByRole("button", { name: "预览" }));

    const frame = screen.getByTitle("simulation-runtime.html");
    expect(frame).toHaveAttribute("srcdoc");
    expect(frame.getAttribute("srcdoc")).toContain("测试代码预览");
  });

  it("returns to the home stage when clicking the expanded sidebar brand", async () => {
    mockFetchWithRunState();
    window.history.pushState({}, "", "/simulation/run-1");
    const user = userEvent.setup();

    render(<App />);

    expect(await screen.findByTestId("preview-panel")).toBeInTheDocument();
    expect(screen.getByText("dengrui")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "收起侧边栏" })).toHaveLength(1);
    expect(document.querySelector(".sidebar-conversation-card")).toBeNull();

    await user.click(await screen.findByRole("button", { name: "ClassSim 返回首页" }));

    expect(screen.getByText("ClassSim")).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "把物理题目转成可教学的 simulation" }),
    ).not.toBeInTheDocument();
    expect(window.location.pathname).toBe("/");
  });

  it("shows the quick-action menu on hover and keeps the selected option visible", async () => {
    mockFetchWithRunState();
    window.history.pushState({}, "", "/");
    const user = userEvent.setup();

    render(<App />);

    const trigger = screen.getByRole("button", { name: "添加内容" });
    await user.hover(trigger);
    expect(screen.getByRole("button", { name: "添加照片或文件" })).toBeVisible();
    expect(screen.getByRole("button", { name: "网页搜索" })).toBeVisible();

    await user.click(screen.getByRole("button", { name: "网页搜索" }));
    expect(await screen.findByText("网页搜索")).toBeInTheDocument();

    await user.unhover(trigger);
    await waitFor(() => {
      expect(screen.queryByRole("button", { name: "添加照片或文件" })).not.toBeInTheDocument();
    });
  });

  it("deletes the current conversation and returns to the home stage", async () => {
    const fetchMock = mockFetchWithRunState();
    window.history.pushState({}, "", "/simulation/run-1");
    const user = userEvent.setup();

    render(<App />);

    expect(await screen.findByTestId("preview-panel")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "删除会话 双绳弹力位移演示" }));

    await waitFor(() => {
      expect(window.location.pathname).toBe("/");
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/problem-to-simulation/runs/run-1",
      expect.objectContaining({ method: "DELETE" }),
    );
    expect(screen.getByText("ClassSim")).toBeInTheDocument();
  });
});
