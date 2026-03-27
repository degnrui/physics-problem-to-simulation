export type SampleListItem = {
  id: string;
  title: string;
  image_path: string;
};

export type SampleResponse = {
  sample: { id: string; image_svg: string };
  preprocessing: { mime_type: string; image_base64: string; steps: string[] };
  detection: DetectionDocument;
  physics: PhysicsDocument;
  simulation: SimulationResponse;
};

export type DetectionDocument = {
  metadata: { title?: string; image_id?: string };
  components: Array<{
    id: string;
    type: string;
    bbox: { x: number; y: number; width: number; height: number };
    confidence?: number;
    source: string;
  }>;
  wires: Array<{ id: string; points: number[][]; confidence?: number; source: string }>;
  nodes: Array<{ id: string; x: number; y: number; source: string }>;
  texts: Array<{ id: string; text: string; source: string }>;
};

export type PhysicsDocument = {
  metadata: { title?: string; image_id?: string };
  components: Array<{
    id: string;
    type: string;
    terminals: string[];
    value?: number | null;
    source: string;
    confidence?: number;
  }>;
  nodes: Array<{ id: string }>;
  connections: Array<{ component_id: string; terminal: string; node_id: string }>;
  parameters: Record<string, unknown>;
  simulation_config: { analysis_type: string };
};

export type SimulationResponse = {
  node_results: Record<string, { voltage: number }>;
  component_results: Record<string, Record<string, string | number>>;
  summary: { source_voltage: number; total_current: number };
};

const API_ROOT = "http://127.0.0.1:8000/api";

export async function fetchSamples(): Promise<SampleListItem[]> {
  const response = await fetch(`${API_ROOT}/samples`);
  return response.json();
}

export async function fetchSampleDetails(imageId: string): Promise<SampleResponse> {
  const response = await fetch(`${API_ROOT}/samples/${imageId}`);
  return response.json();
}

export async function simulatePhysics(
  document: PhysicsDocument
): Promise<SimulationResponse> {
  const response = await fetch(`${API_ROOT}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(document)
  });
  return response.json();
}
