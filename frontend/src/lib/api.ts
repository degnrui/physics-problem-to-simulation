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
  capabilities: {
    editable_value: boolean;
    toggleable: boolean;
    removable: boolean;
    slider_range?: { min_ratio: number; max_ratio: number } | null;
  };
};

export type Figure1Scene = {
  id: string;
  title: string;
  canvas: { width: number; height: number };
  components: Figure1SceneComponent[];
  wires: Array<{ id: string; role: string; points: Array<{ x: number; y: number }> }>;
  meter_anchors: Array<{ component_id: string; x: number; y: number }>;
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

export type Figure1Payload = {
  reference_image: { id: string; svg: string };
  scene: Figure1Scene;
  state: Figure1State;
  simulation: Figure1Simulation;
};

const API_ROOT = "http://127.0.0.1:8000/api";

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
