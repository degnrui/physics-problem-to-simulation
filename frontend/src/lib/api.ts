export function resolveApiBase() {
  const configuredBase = import.meta.env.VITE_API_BASE;
  if (configuredBase && typeof configuredBase === "string") {
    return configuredBase.replace(/\/$/, "");
  }
  return "/api";
}

const API_BASE = resolveApiBase();

export interface RunStep {
  id: string;
  label: string;
  status: string;
  artifacts_written: string[];
  error: string;
  execution_mode?: string;
  model_name?: string;
  validation_passed?: boolean;
}

export interface RunStatusResponse {
  run_id: string;
  status: string;
  current_stage: string;
  current_step_index: number;
  total_steps: number;
  percent: number;
  started_at: string | null;
  updated_at: string | null;
  finished_at: string | null;
  steps: RunStep[];
}

export interface RunResultResponse {
  run_id: string;
  planner: Record<string, unknown>;
  task_plan: Record<string, unknown>;
  problem_profile: Record<string, unknown>;
  physics_model: Record<string, unknown>;
  teaching_plan: Record<string, unknown>;
  scene_spec: Record<string, unknown> | null;
  simulation_spec: Record<string, unknown> | null;
  simulation_blueprint: Record<string, unknown> | null;
  renderer_payload: Record<string, unknown> | null;
  delivery_bundle: Record<string, unknown> | null;
  validation_report: Record<string, unknown>;
  task_log: Array<Record<string, unknown>>;
}

export interface RunCreateResponse {
  run_id: string;
  status: string;
  route: string;
  status_url: string;
}

export interface RunListItem {
  run_id: string;
  title: string;
  status: string;
  updated_at: string | null;
  problem_family: string;
  model_family: string;
  simulation_mode: string;
  export_ready: boolean;
}

export interface RunListResponse {
  items: RunListItem[];
}

export interface ExportHtmlResponse {
  run_id: string;
  export_mode: "single-file-html";
  download_url: string;
  path: string;
}

export interface RunDeleteResponse {
  run_id: string;
  deleted: boolean;
}

async function handleJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }
  return response.json();
}

export async function createRun(text: string): Promise<RunCreateResponse> {
  const response = await fetch(`${API_BASE}/problem-to-simulation/runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, mode: "llm-assisted" }),
  });
  return handleJson<RunCreateResponse>(response);
}

export async function getRunStatus(runId: string): Promise<RunStatusResponse> {
  const response = await fetch(`${API_BASE}/problem-to-simulation/runs/${runId}`);
  return handleJson<RunStatusResponse>(response);
}

export async function listRuns(): Promise<RunListResponse> {
  const response = await fetch(`${API_BASE}/problem-to-simulation/runs`);
  return handleJson<RunListResponse>(response);
}

export async function getRunResult(runId: string): Promise<RunResultResponse> {
  const response = await fetch(`${API_BASE}/problem-to-simulation/runs/${runId}/result`);
  return handleJson<RunResultResponse>(response);
}

export async function deleteRun(runId: string): Promise<RunDeleteResponse> {
  const response = await fetch(`${API_BASE}/problem-to-simulation/runs/${runId}`, {
    method: "DELETE",
  });
  return handleJson<RunDeleteResponse>(response);
}

export async function getRunArtifact(
  runId: string,
  artifactName: string,
): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/problem-to-simulation/runs/${runId}/artifacts/${artifactName}`);
  return handleJson<Record<string, unknown>>(response);
}

export async function createHtmlExport(runId: string): Promise<ExportHtmlResponse> {
  const response = await fetch(`${API_BASE}/problem-to-simulation/runs/${runId}/export-html`, {
    method: "POST",
  });
  return handleJson<ExportHtmlResponse>(response);
}

export function exportDownloadUrl(runId: string): string {
  return `${API_BASE}/problem-to-simulation/runs/${runId}/export-html`;
}
