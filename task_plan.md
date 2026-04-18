# Task Plan

## Goal
Refactor the entire React frontend into a unified teacher-facing simulation studio shell with four primary states:
home input, generation transition, result workbench with preview open/closed, and fullscreen/runtime inline edit.

## Phases
| Phase | Status | Notes |
| --- | --- | --- |
| 1. Inspect current frontend structure and constraints | completed | Existing app is split between launcher and workspace routes with inspector-heavy layout. |
| 2. Define target state machine, layout system, and component boundaries | completed | User approved state machine, design tokens, and component interaction model. |
| 3. Rebuild frontend components and styling system | completed | Replaced the split launcher/workspace UI with a unified studio shell, conversation workbench, preview system, and interactive runtime editing. |
| 4. Verify build and state transitions | completed | Added Vitest coverage for home/preview transitions and passed frontend test + production build. |

## Decisions
- Keep React + Vite baseline.
- Replace current bespoke CSS with tokenized Tailwind-style utility layer via reusable class composition in CSS.
- Preserve backend API contract around runs, status polling, results, and HTML export.

## Risks
- Current API does not expose persistent multi-conversation history beyond run list, so conversation UX will map runs to conversations.
- Runtime preview/edit behaviors need to be represented with a frontend-side interactive simulation shell even if backend only returns HTML/export data.

## Errors Encountered
None yet.
