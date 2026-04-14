from backend.app.domain.problem import ProblemInput, StructuredProblem
from backend.app.domain.model import PhysicsModel
from backend.app.domain.scene import ProblemToSimulationResult, SimulationScene


def run_problem_to_simulation(problem: ProblemInput) -> ProblemToSimulationResult:
    structured = StructuredProblem(
        summary=problem.text[:80],
        knowns=["Placeholder known quantity"],
        unknowns=["Placeholder target"],
        assumptions=["Pipeline stub: replace with real parser"],
    )

    model = PhysicsModel(
        model_type="dynamic_circuit_stub",
        core_relations=["Ohm's law", "Series-parallel reasoning"],
        variables=["U", "I", "R"],
        reasoning_focus=["Map text to a canonical circuit model"],
    )

    scene = SimulationScene(
        scene_type="circuit",
        template_id="dynamic-circuit-v1",
        parameters={"battery_voltage": 6.0, "resistor_value": 10.0},
        notes=["Stub scene generated from scaffold pipeline"],
    )

    return ProblemToSimulationResult(
        problem_summary=structured.summary,
        structured_problem=structured.model_dump(),
        physics_model=model.model_dump(),
        scene=scene.model_dump(),
        warnings=["This is a scaffold response, not a real physics parser yet."],
    )

