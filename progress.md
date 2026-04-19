# Progress Log

## 2026-04-18

- Loaded mandatory workflow skills and project design context.
- Inspected frontend entry, styles, API layer, and existing components.
- Identified that the current architecture must be restructured around a single shell-level state machine rather than patched incrementally.
- Completed design alignment with the user: quiet studio visual direction, document-first workbench behavior, preview restoration by conversation, and detailed component tree.
- Wrote the approved design spec to `docs/superpowers/specs/2026-04-18-simulation-studio-frontend-design.md`.
- Added Tailwind and Vitest tooling, plus a red-green test for the key shell transitions.
- Rebuilt the frontend around `AppShell`, collapsible conversation management, focused home input, single-task generation playback, conversation workbench, runtime preview, fullscreen runtime, and inline edit overlay.
- Verification passed:
  - `npm test`
  - `npm run build`

## 2026-04-19

- Recovered session state from planning files and current git diff.
- Confirmed the frontend delete flow was incomplete: backend delete endpoint existed, but `App.tsx` still performed only local removal.
- Added a red regression test proving conversation deletion must call `DELETE /api/problem-to-simulation/runs/:id`.
- Wired `handleDeleteConversation` to await `deleteRun` before clearing local state and navigating home.
- Fixed a production build regression by replacing `replaceAll` in the HTML escaping helper with a target-compatible regex implementation.
- Reproduced the "开始生成没有反应" issue path: successful `POST /api/problem-to-simulation/runs` calls were possible, but frontend request failures had no visible error state, and backend model timeouts could crash the background worker via uncaught `socket.timeout`.
- Added frontend regressions for starter prompt launch, custom prompt launch, and visible create-run failure feedback.
- Added a backend regression test proving `ModelExecutor` must fallback instead of crashing on `socket.timeout`.
- Implemented frontend create-run error messaging plus home prompt accessibility labeling.
- Updated backend `ModelExecutor` to treat `socket.timeout` as a fallback condition.
- Verified the live NVIDIA model configuration directly: `/models` and `chat/completions` both respond successfully with the configured `minimaxai/minimax-m2.5` model.
- Changed backend timeout behavior per request: `ModelExecutor` now retries timeout-class failures up to 5 attempts and re-raises on the final timeout instead of converting them into fallback output.
- Replaced the earlier timeout fallback test with two retry-oriented backend tests: one for eventual success after repeated timeouts, and one for raising after 5 consecutive timeouts.
- Verification passed:
  - `cd frontend && npm test -- --run src/App.test.tsx`
  - `cd frontend && npm test -- --run`
  - `cd frontend && npm run build`
  - `python3 -m compileall backend/app`
  - `python3 -m unittest tests.test_harness.ModelExecutorTests.test_execute_falls_back_when_socket_times_out`
  - `python3 -m unittest tests.test_harness.ModelExecutorTests`
  - `python3 -m unittest tests.test_harness.HarnessOrchestratorTests tests.test_harness.ModelExecutorTests`
- User rejected the ongoing direction of adding more hard-coded routing/template families, and clarified the target is an agent system where the harness decomposes work, exposes tools, and improves the model's execution quality rather than classifying problems into fixed buckets.
- Reviewed external agent references and the suggested `Stemly` repository to recalibrate architecture direction before further implementation.
- Wrote the controlled-agent harness design spec to `docs/superpowers/specs/2026-04-19-controlled-agent-harness-design.md`, defining fixed stages, tool registry, artifact/trace stores, validation gates, and the migration path away from hard-coded family routing.
