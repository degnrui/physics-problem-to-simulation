# physics-problem-to-simulation

Convert physics problems into reviewed interactive runtimes through a coordinator graph.

## Runtime Flow

The backend now runs a breaking-cut workflow:

`request_analysis -> evidence_ingestion? -> domain_grounding -> instructional_modeling -> simulation_design -> runtime_package_assembly -> code_generation -> runtime_validation -> publish_result`

Key rules:

- downstream workflows read only from `approved_artifacts`
- `simulation_design` is a subgraph with explicit child-node review loops
- `runtime_validation` rejects report-shell and payload-shell HTML
- `delivery_runtime` is published only after runtime validation passes

## Repository Layout

- `backend/app/orchestrator/`: coordinator graph, state, checkpoints, review loop
- `backend/app/workflows/`: stage packages and the `simulation_design` subgraph
- `backend/app/runtime/`: generator client, artifact store, exporter
- `frontend/src/`: Studio UI that consumes only the new run/result contracts
- `shared/contracts/`: typed shared contract definitions

## API Contract

`/api/problem-to-simulation/runs/{run_id}/result` returns:

- `run_id`
- `run_state`
- `artifacts`
- `approved_artifacts`
- `runtime_package`
- `generated_files`
- `delivery_runtime`
- `execution_trace`

## Local Development

Backend:

```bash
uvicorn backend.app.main:app --reload
```

Frontend:

```bash
npm --prefix frontend install
npm --prefix frontend dev
```

## Verification

Backend tests:

```bash
python3 -m unittest tests.test_harness -v
```

Frontend tests:

```bash
npm --prefix frontend test
```
