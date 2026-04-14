export interface ProblemToSimulationResponse {
  problem_summary: string;
  structured_problem: Record<string, unknown>;
  physics_model: Record<string, unknown>;
  scene: Record<string, unknown>;
  warnings: string[];
}

export async function submitProblem(text: string): Promise<ProblemToSimulationResponse> {
  const response = await fetch("http://127.0.0.1:8000/api/problem-to-simulation", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text })
  });

  if (!response.ok) {
    throw new Error("Request failed");
  }

  return response.json();
}

