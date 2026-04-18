# Simulation Studio Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the React frontend into a unified simulation studio shell with focused home input, single-task generation flow, stable conversation workbench, and closable/restorable runtime preview.

**Architecture:** Keep the existing Vite + React app and API contract, but replace the split launcher/workspace UI with a shell-first state machine. Use Tailwind-driven tokens for visual consistency, synthesize conversation/artifact state from run data plus local UI persistence, and reuse the simulation viewport as the runtime engine inside a new preview system.

**Tech Stack:** React 19, TypeScript, Vite, Tailwind CSS, Vitest, Testing Library

---

### Task 1: Tooling And Test Harness

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.ts`
- Create: `frontend/src/test/setup.ts`
- Create: `frontend/src/App.test.tsx`

- [ ] Add Tailwind and Vitest dependencies plus scripts.
- [ ] Configure Vite plugins for React and Tailwind.
- [ ] Configure Vitest with `jsdom` and Testing Library setup.
- [ ] Write failing tests for the core shell behavior:
  - home state renders without preview
  - completed run opens preview automatically
  - closing preview hides it
  - clicking artifact card reopens preview

### Task 2: Studio State And Data Mapping

**Files:**
- Create: `frontend/src/types/studio.ts`
- Create: `frontend/src/lib/studio.ts`
- Modify: `frontend/src/lib/api.ts`

- [ ] Define shell state, conversation state, artifact state, runtime document state, and generation stage metadata.
- [ ] Add mapper helpers from backend run/status/result payloads into UI conversations and runtime artifacts.
- [ ] Add persistence helpers for per-conversation UI restoration.

### Task 3: Shell Components

**Files:**
- Create: `frontend/src/components/studio/AppShell.tsx`
- Create: `frontend/src/components/studio/UtilityRail.tsx`
- Create: `frontend/src/components/studio/CollapsibleConversationSidebar.tsx`
- Create: `frontend/src/components/studio/HomeInputStage.tsx`
- Create: `frontend/src/components/studio/TooltipActionIcons.tsx`
- Create: `frontend/src/components/studio/GenerationStagePlayer.tsx`
- Create: `frontend/src/components/studio/GenerationTaskCard.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] Build the shell frame and left-side rail/sidebar behavior.
- [ ] Build the home input stage with no preview presence.
- [ ] Build the generation player with single-task switching.
- [ ] Connect stage selection to route and run status.

### Task 4: Conversation Workbench And Preview

**Files:**
- Create: `frontend/src/components/studio/ConversationContentPanel.tsx`
- Create: `frontend/src/components/studio/ArtifactCard.tsx`
- Create: `frontend/src/components/studio/PreviewPanel.tsx`
- Create: `frontend/src/components/studio/RuntimeHeaderActions.tsx`

- [ ] Build the message/artifact workbench center panel.
- [ ] Build artifact cards with active state and preview reopen behavior.
- [ ] Build the preview panel with close semantics, version switch, download, and preview/code tabs.

### Task 5: Runtime Editing

**Files:**
- Create: `frontend/src/components/studio/SimulationRuntimePanel.tsx`
- Create: `frontend/src/components/studio/InlineEditOverlay.tsx`
- Create: `frontend/src/components/studio/FullscreenRuntimeModal.tsx`
- Modify: `frontend/src/components/SimulationViewport.tsx`

- [ ] Wrap the existing simulation viewport in a runtime workspace.
- [ ] Add clickable editable labels and local document fields.
- [ ] Add fullscreen mode that preserves structure.
- [ ] Add local version snapshots for conversation-scoped edits.

### Task 6: Tailwind Token System

**Files:**
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/main.tsx`

- [ ] Define design tokens for color, spacing, radius, shadow, motion, and widths.
- [ ] Add component-layer utility compositions for shell surfaces, cards, toolbars, and typographic hierarchy.
- [ ] Ensure the homepage, generation state, workbench, and preview share one cohesive visual language.

### Task 7: Verification

**Files:**
- Modify: `task_plan.md`
- Modify: `progress.md`

- [ ] Run targeted tests first during development.
- [ ] Run full frontend test suite.
- [ ] Run production build.
- [ ] Log verification outcomes in progress tracking files.
