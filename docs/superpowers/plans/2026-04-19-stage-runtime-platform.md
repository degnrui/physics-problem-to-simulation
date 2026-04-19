# Stage Runtime Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a stage-based runtime with skill-pack integration, validator/repair flow, and an end-to-end simulation package run for a physics problem.

**Architecture:** Replace the hard-coded harness task sequence with a registry-driven stage graph. Adapt existing builders as deterministic fallbacks behind stage contracts so the platform can run now while still matching the v2 architecture.

**Tech Stack:** FastAPI, Python, Pydantic, JSON artifact store, Vite frontend compatibility, unittest/pytest-style backend tests

---

### Task 1: Add runtime contracts and skill-pack loading

**Files:**
- Create: `backend/app/harness/stage_runtime.py`
- Create: `backend/app/harness/skill_registry.py`
- Create: `skillpacks/physics_sim_agent_v2_package/...`
- Test: `tests/test_harness.py`

- [ ] Define stage contract and validation result models.
- [ ] Implement file-based skill registry for `skill.md`, `validator.md`, `repair.md`.
- [ ] Add minimal skill-pack files for all `00-10` stages.
- [ ] Add tests that verify stage registry returns the expected ordered graph.

### Task 2: Implement stage builders, validators, and repairers

**Files:**
- Create: `backend/app/harness/stage_builders.py`
- Modify: `backend/app/workers/*.py`
- Test: `tests/test_harness.py`

- [ ] Map existing worker outputs into v2 stage artifacts.
- [ ] Add stage-specific validation checks with unified issue format.
- [ ] Add deterministic repair functions for core stages.
- [ ] Add tests for validation and repair behavior on representative artifacts.

### Task 3: Replace hard-coded orchestration with stage runtime execution

**Files:**
- Modify: `backend/app/harness/orchestrator.py`
- Modify: `backend/app/harness/run_state.py`
- Modify: `backend/app/harness/task_registry.py`
- Test: `tests/test_harness.py`

- [ ] Execute stages through the registry rather than static task indices.
- [ ] Persist stage artifacts, validation reports, logs, and statuses.
- [ ] Skip conditional stages when profiling says they are unnecessary.
- [ ] Block compile when final validation fails and return repair guidance.

### Task 4: Update API contract and compatibility aliases

**Files:**
- Modify: `shared/contracts/problem-to-simulation.json`
- Modify: `backend/app/api/routes/pipeline.py`
- Test: `tests/test_harness.py`, `frontend/src/App.test.tsx`

- [ ] Update shared contract examples to the new stage names and status model.
- [ ] Keep legacy top-level aliases in final package responses.
- [ ] Adjust tests for the new stage-based fields while preserving current API routes.

### Task 5: Refresh architecture docs and verify end-to-end flow

**Files:**
- Modify: `docs/architecture.md`
- Modify: `README.md`
- Test: `tests/test_harness.py`, `frontend/src/App.test.tsx`

- [ ] Rewrite repo docs to describe the new platform runtime.
- [ ] Run backend and frontend tests.
- [ ] Run one end-to-end sample problem and confirm the final package includes compile artifacts.
