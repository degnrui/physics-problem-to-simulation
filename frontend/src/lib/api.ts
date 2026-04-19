export function resolveApiBase() {
  const configuredBase = import.meta.env.VITE_API_BASE;
  if (configuredBase && typeof configuredBase === "string") {
    return configuredBase.replace(/\/$/, "");
  }
  return "/api";
}

const API_BASE = resolveApiBase();

export interface StageStatus {
  name: string;
  status: string;
  attempts: number;
  score: number;
  issues: Array<Record<string, unknown>>;
}

export interface RunStatusResponse {
  run_id: string;
  status: string;
  active_stage: string;
  workflow_plan: string[];
  stage_status: Record<string, StageStatus>;
  started_at: string | null;
  updated_at: string | null;
  finished_at: string | null;
}

export interface RunResultResponse {
  run_id: string;
  run_state: {
    request_mode: string;
    request_profile: Record<string, unknown>;
    workflow_plan: string[];
    active_stage: string;
    stage_status: Record<string, StageStatus>;
  };
  artifacts: Record<string, Record<string, unknown>>;
  approved_artifacts: Record<string, Record<string, unknown>>;
  runtime_package: Record<string, unknown> | null;
  generated_files: Record<string, string>;
  delivery_runtime: { primary_file: string; html: string } | null;
  execution_trace: Array<Record<string, unknown>>;
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
  input_profile: string;
  request_mode: string;
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
