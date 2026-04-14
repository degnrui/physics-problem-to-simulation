# Physics Problem to Simulation Scaffold Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the initial repository scaffold for a standalone `physics-problem-to-simulation` project.

**Architecture:** The repository separates product concerns into app, domain, and pipeline layers. The first version centers on a stable transformation path from problem text to structured physics model to simulation scene, instead of attempting arbitrary end-to-end AI code generation.

**Tech Stack:** Python backend scaffold, React/TypeScript frontend scaffold, Markdown docs, local git

---

### Task 1: Create repository structure

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `docs/architecture.md`
- Create: `docs/product-scope.md`
- Create: `docs/plans/2026-04-14-scaffold-design.md`

### Task 2: Add backend scaffold

**Files:**
- Create: `backend/README.md`
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/routes/__init__.py`
- Create: `backend/app/api/routes/health.py`
- Create: `backend/app/api/routes/pipeline.py`
- Create: `backend/app/domain/__init__.py`
- Create: `backend/app/domain/problem.py`
- Create: `backend/app/domain/model.py`
- Create: `backend/app/domain/scene.py`
- Create: `backend/app/pipeline/__init__.py`
- Create: `backend/app/pipeline/problem_to_simulation.py`

### Task 3: Add frontend scaffold

**Files:**
- Create: `frontend/README.md`
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/components/ProblemInput.tsx`
- Create: `frontend/src/components/PipelinePreview.tsx`

### Task 4: Add shared schemas and samples

**Files:**
- Create: `shared/README.md`
- Create: `shared/contracts/problem-to-simulation.json`
- Create: `sample_data/problems/dynamic-circuit-01.md`
- Create: `sample_data/models/dynamic-circuit-01.json`
- Create: `sample_data/scenes/dynamic-circuit-01.json`

### Task 5: Initialize git and verify

**Files:**
- Modify: `task_plan.md`
- Modify: `findings.md`
- Modify: `progress.md`

