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
