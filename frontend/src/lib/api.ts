export type PortSpec = {
  id: string;
  x: number;
  y: number;
};

export type Figure1SceneComponent = {
  id: string;
  type: string;
  label?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  enabled: boolean;
  value?: number | null;
  metadata?: Record<string, string>;
  capabilities: {
    editable_value: boolean;
    toggleable: boolean;
    removable: boolean;
    slider_range?: { min_ratio: number; max_ratio: number } | null;
  };
  ports: PortSpec[];
};

export type SceneWire = {
  id: string;
  role: string;
  start_ref: string;
  end_ref: string;
  bends: Array<{ x: number; y: number }>;
};

export type Figure1Scene = {
  id: string;
  title: string;
  canvas: { width: number; height: number };
  components: Figure1SceneComponent[];
  wires: SceneWire[];
  meter_anchors: Array<{ component_id: string; x: number; y: number }>;
  symbol_layout?: Record<string, unknown>;
  ports_and_wires?: Record<string, unknown>;
  circuit_topology?: Record<string, unknown>;
  debug?: Record<string, string>;
};

export type Figure1State = {
  switch_closed: boolean;
  battery_voltage: number;
  resistor_value: number;
  rheostat_total: number;
  rheostat_ratio: number;
};

export type Figure1Simulation = {
  meter_results: { ammeter: number; voltmeter: number };
  component_states: {
    switch: { state: string };
    battery: { value: number };
    resistor: { value: number };
    rheostat: { total: number; ratio: number; effective_resistance: number };
  };
  visual_state: {
    energized: boolean;
    highlighted_wires: string[];
    meter_visibility: Record<string, boolean>;
  };
  summary: {
    source_voltage: number;
    total_current: number;
    resistor_voltage: number;
    rheostat_voltage: number;
  };
  physics: Record<string, unknown>;
};

export type ImagePreview =
  | { id: string; svg: string; data_url?: never }
  | { id: string; data_url: string; svg?: never };

export type RecognitionPayload = {
  session_id: string;
  created_at: string;
  reference_image: ImagePreview;
  scene: Figure1Scene;
  state: Figure1State;
  simulation: Figure1Simulation;
  detections: {
    line_segments: number;
    circles: number;
    rectangles: number;
    confidence: number;
  };
  needs_confirmation: boolean;
  confidence_breakdown: {
    overall: number;
    symbol_detection: number;
    topology_reconstruction: number;
  };
  topology_warnings: string[];
  unsupported_symbols: string[];
  issues: Array<{ id: string; level: "warning" | "error"; message: string; target?: string }>;
};

export type Figure1Payload = {
  reference_image: ImagePreview;
  scene: Figure1Scene;
  state: Figure1State;
  simulation: Figure1Simulation;
};

export type MechanicsProblemRepresentation = {
  summary: string;
  objects: Array<{ id: string; label: string; category: string }>;
  known_quantities: Array<{ symbol: string; value?: number; unit?: string; text?: string }>;
  constraints: string[];
  geometry: string[];
  assumptions: string[];
  goals: string[];
  stages: string[];
};

export type MechanicsCandidateModel = {
  id: string;
  title: string;
  confidence: number;
  state_variables: string[];
  governing_laws: string[];
  assumptions: Record<string, boolean>;
  notes: string[];
};

export type MechanicsSolutionModel = {
  available: boolean;
  answer_map: Record<string, string>;
  laws: string[];
  steps: Array<{ id: string; prompt: string; law?: string; conclusion?: string; evidence?: string }>;
};

export type MechanicsConflictItem = {
  id: string;
  kind: string;
  severity: "warning" | "error";
  message: string;
  target?: string;
  expected?: string;
  actual?: string;
  recommendation?: string;
};

export type MechanicsSimulation = {
  model_id: string;
  answers: Record<
    string,
    {
      key: string;
      label: string;
      value: number;
      unit: string;
      display_value: string;
      expected_value?: string;
      matches_reference?: boolean | null;
    }
  >;
  stage_results: Record<string, unknown>;
  summary: Record<string, unknown>;
};

export type MechanicsTeachingScene = {
  scene_id: string;
  title: string;
  canvas: { width: number; height: number; background?: string };
  actors: Array<{
    id: string;
    kind: string;
    label: string;
    geometry: Record<string, number>;
    style: Record<string, string | number>;
  }>;
  stages: Array<{
    id: string;
    title: string;
    prompt: string;
    focus: string[];
    duration: number;
  }>;
  annotations: Array<{
    key: string;
    stage_id: string;
    label: string;
    value: string;
    emphasis: string;
  }>;
  charts: Array<{
    id: string;
    label: string;
    unit: string;
    points: Array<{ x: number; y: number }>;
  }>;
  lesson_panels: Array<{
    stage_id: string;
    headline: string;
    question: string;
    takeaway: string;
    bullets: string[];
  }>;
  controls: Array<{ id: string; label: string; kind: string }>;
  playback_steps: Array<{ stage_id: string; checkpoint: number; headline: string }>;
};

export type MechanicsRuntimeFrame = {
  progress: number;
  actors: Record<string, Record<string, string | number>>;
  overlays: Record<string, string | number>;
  annotations: Array<{ key: string; label: string; value: string; emphasis: string }>;
  chart_series: MechanicsTeachingScene["charts"];
};

export type MechanicsRecognitionPayload = {
  session_id: string;
  created_at: string;
  reference_image: ImagePreview;
  problem_representation: MechanicsProblemRepresentation;
  candidate_models: MechanicsCandidateModel[];
  selected_model: MechanicsCandidateModel;
  solution_model: MechanicsSolutionModel;
  conflict_items: MechanicsConflictItem[];
  simulation: MechanicsSimulation;
  needs_confirmation: boolean;
  confidence_breakdown: Record<string, number>;
  issues: Array<{ id: string; level: "warning" | "error"; message: string; target?: string }>;
  harness?: Record<string, unknown>;
  executor_run?: {
    executor: string;
    tool_trace: Array<{ tool: string; summary: string; artifact_key: string }>;
    intermediate_artifacts: Record<string, unknown>;
    runtime_warnings?: Array<{ code: string; message: string }>;
  };
  verification_report?: Record<string, unknown>;
  final_simulation_spec?: MechanicsSimulation;
  execution_mode?: string;
};

export type MechanicsScenePayload = {
  scene: MechanicsTeachingScene;
  verification_report: Record<string, unknown>;
  final_simulation_spec: MechanicsSimulation;
};

export type MechanicsRuntimePayload = {
  scene: MechanicsTeachingScene;
  stage: MechanicsTeachingScene["stages"][number];
  frame: MechanicsRuntimeFrame;
  verification_report: Record<string, unknown>;
};

const API_ROOT = "/api";

export async function fetchSamples(): Promise<
  Array<{ id: string; title: string; status: string }>
> {
  const response = await fetch(`${API_ROOT}/samples`);
  return response.json();
}

export async function fetchFigure1Scene(): Promise<Figure1Payload> {
  const response = await fetch(`${API_ROOT}/scenes/figure-1`);
  return response.json();
}

export async function simulateFigure1(
  scene: Figure1Scene,
  state: Figure1State
): Promise<Figure1Simulation> {
  const response = await fetch(`${API_ROOT}/scenes/figure-1/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scene, state })
  });
  return response.json();
}

export async function applyFigure1Edit(
  scene: Figure1Scene,
  state: Figure1State,
  edit: { action: string; component_id: string }
): Promise<{ scene: Figure1Scene; state: Figure1State; simulation: Figure1Simulation }> {
  const response = await fetch(`${API_ROOT}/scenes/figure-1/edit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scene, state, edit })
  });
  return response.json();
}

export async function recognizeCircuitImage(file: File): Promise<RecognitionPayload> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_ROOT}/recognize`, {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function confirmRecognizedScene(
  sessionId: string,
  updates: {
    component_updates?: Array<{ id: string; type?: string; value?: number; enabled?: boolean }>;
    state_updates?: Array<{ key: string; value: number | boolean }>;
    connections?: Array<{ component_id: string; terminal: string; node_id: string }>;
  }
): Promise<{ session_id: string; scene: Figure1Scene; state: Figure1State; simulation: Figure1Simulation }> {
  const response = await fetch(`${API_ROOT}/recognize/${sessionId}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ updates })
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function importSceneBundle(payload: {
  scene: Figure1Scene;
  state?: Partial<Figure1State>;
}): Promise<{ scene: Figure1Scene; state: Figure1State; simulation: Figure1Simulation }> {
  const response = await fetch(`${API_ROOT}/scenes/import-json`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function recognizeMechanicsProblem(payload: {
  problemText: string;
  solutionText?: string;
  finalAnswers?: string;
  imageFile?: File | null;
}): Promise<MechanicsRecognitionPayload> {
  const formData = new FormData();
  formData.append("problem_text", payload.problemText);
  formData.append("solution_text", payload.solutionText ?? "");
  formData.append("final_answers", payload.finalAnswers ?? "");
  if (payload.imageFile) {
    formData.append("image", payload.imageFile);
  }
  const response = await fetch(`${API_ROOT}/mechanics/recognize`, {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function confirmMechanicsProblem(
  sessionId: string,
  updates: {
    selected_model_id?: string;
    assumption_overrides?: Record<string, boolean>;
  }
): Promise<MechanicsRecognitionPayload> {
  const response = await fetch(`${API_ROOT}/mechanics/${sessionId}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ updates })
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function generateMechanicsScene(
  sessionId: string
): Promise<MechanicsScenePayload> {
  const response = await fetch(`${API_ROOT}/mechanics/${sessionId}/generate-scene`, {
    method: "POST"
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function simulateMechanicsScene(
  sessionId: string,
  payload: { stageId: string; progress: number }
): Promise<MechanicsRuntimePayload> {
  const response = await fetch(`${API_ROOT}/mechanics/${sessionId}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stage_id: payload.stageId, progress: payload.progress })
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}
