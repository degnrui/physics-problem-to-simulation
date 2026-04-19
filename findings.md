# Findings

## 2026-04-18

- `frontend/src/App.tsx` currently uses route split: `/` for launcher and `/simulation/:id` for workspace.
- Existing homepage already mixes creation and recent runs, but not as a collapsible conversation system.
- Existing workspace uses a left stage rail and a right status panel; this directly conflicts with the requested shell where the left side is only conversation management.
- Current generation view is a persistent multi-step rail, not a single-task transition player.
- Current result view centers the simulation and places artifacts in an inspector; requested result view instead centers conversation content and keeps runtime in a closable right preview panel.
- API surface is sufficient for a first pass: run creation, list, polling status, fetch result, export HTML.
- `.impeccable.md` confirms teacher-facing, light theme, professional education product direction.
- The new frontend maps backend `run` items to conversations and persists per-conversation UI state in local storage.
- Runtime versions are currently frontend-managed snapshots: initial generation creates `V1`, and follow-up prompts or inline edits append later versions.
- The runtime itself is now a dedicated studio component instead of the previous inspector-centric workspace layout.

## 2026-04-19

- The follow-up "delete conversation" UI path had only been removing items from frontend state and local storage; it was not calling the new backend `DELETE /problem-to-simulation/runs/{run_id}` endpoint.
- A regression test in `frontend/src/App.test.tsx` now asserts that deleting a conversation issues the `DELETE` request before the UI returns home.
- The new HTML runtime source builder in `frontend/src/lib/studio.ts` cannot rely on `String.prototype.replaceAll` under the current TypeScript target; a regex-based escape helper keeps the build compatible without changing output.
- The home-stage "no response on generate" symptom had two separate causes:
  - frontend `createRun` failures were surfacing as unhandled promise rejections with no user-visible error state;
  - backend `ModelExecutor.execute()` did not treat `socket.timeout` as a fallback condition, so LLM timeouts crashed the background run thread instead of degrading gracefully.
- Local reproduction confirmed the API create route and Vite proxy both return `202`; the deeper backend failure happened after enqueue, inside the background worker.
- Current NVIDIA configuration is valid: the configured `OPENAI_BASE_URL`, `OPENAI_MODEL`, and API key all load correctly, `/models` responds `200`, and a direct `chat/completions` call with `minimaxai/minimax-m2.5` succeeds.
- Timeout handling policy is now stricter than before: retry timeout-class failures up to 5 times, and if the fifth attempt still times out, re-raise the timeout instead of silently falling back.
- The current backend architecture is still fundamentally a rule router:
  - `backend/app/workers/planner.py` maps a few keyword patterns to `problem_family/model_family/stage_type`;
  - `backend/app/pipeline/problem_to_simulation.py` then compiles those families into fixed `scene/template` structures.
- This means the system behaves more like a template selector than a true harness for an agent model. Even when LLM output is used, the harness still constrains execution to pre-authored families and shapes.
- External references align with the user's critique:
  - OpenAI's practical guide frames agents around `model + tools + instructions`, and recommends explicit task decomposition, reusable tools, guardrails, and evals rather than brittle rule trees.
  - Anthropic's “Building effective agents” distinguishes workflows from agents: workflows are predefined code paths, while agents dynamically decide process and tool usage.
  - Anthropic's evals article defines the harness/scaffold as the runtime that gives the model tools, captures trajectories, and measures outcomes; this is closer to the target architecture than the current repo.
- The referenced repo `SH-Nihil-Mukkesh-25/Stemly` is also largely topic-template driven:
  - `backend/services/ai_detector.py` uses keyword+Gemini topic detection.
  - `backend/services/visualiser_loader.py` maps topics to fixed JSON templates.
  - `backend/routers/visualiser_engine.py` loads templates and applies parameter updates.
- Conclusion from comparison: Stemly is useful as a product reference, but not as the core architecture to copy for a flexible harness+agent system.
