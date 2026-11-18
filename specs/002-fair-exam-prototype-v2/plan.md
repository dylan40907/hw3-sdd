# Implementation Plan: Fair Exam Prototype V2

**Branch**: `main` (no feature branch) | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-fair-exam-prototype-v2/spec.md`. User input: keep the
existing tech stack and code structure in `frontend/`, change only what the spec requires, and deploy
this version separately from the previous one so both can be compared.

## Summary

V2 is an edit of the V1 prototype, not a rewrite. The stack, folders and module split in `frontend/`
stay the same. Five behaviors change because the V2 spec changed (details in
[research.md](research.md)):

1. One flag per student per exam that collects all of the student's signals, with a "New signals" mark
   for the instructor when a signal is added to a flag that is no longer new (REQ-12, FR-012).
2. A help request needs a reason that the student picks or types, and the reason is stored on the
   pause (REQ-10, REQ-11, FR-010, FR-011).
3. No fast-answer signal after a connection loss or a help request (REQ-08, FR-008, FR-021).
4. Any shared incorrect answer forms a group, so the minimum group size drops from 3 to 2 (REQ-09,
   FR-009).
5. Stored state moves to a new key and shape so V2 can run next to V1 on the same host (deployment).

Everything else in `frontend/` (start page, versions, autosave, fullscreen, timer, explanation
request, referral, read-only office view, event wiring) is kept as is and only re-tested under the V2
FR numbers. V2 is deployed to `/v2/` on the existing `gh-pages` branch, next to `/v1/`, which is not
touched.

## Technical Context

**Language/Version**: JavaScript (ES2022 modules), HTML5, CSS3; Node.js 20+ for tests (unchanged)

**Primary Dependencies**: None (unchanged)

**Storage**: Browser `localStorage`, one JSON document; key changes from `fairExam.v1` to
`fairExam.v2` (R6)

**Testing**: `node --test` from `frontend/` (unchanged)

**Target Platform**: Current desktop Chrome, Edge and Firefox; static host (unchanged)

**Project Type**: Static single-page web app (unchanged)

**Performance Goals**: Unchanged from V1

**Constraints**: No build step, no backend, no network calls, relative asset paths so the app works
from the `/v2/` subfolder (unchanged)

**Scale/Scope**: 1 exam, 3 questions, 5 mock students, 3 roles (unchanged)

No NEEDS CLARIFICATION items. The two open questions in the spec (maximum help-request length and
what makes a shared answer suspicious) are assumptions in the spec and are not built.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Pre-design | Post-design |
|---|---|---|---|
| I. Spec Scope Only | Every change maps to an FR; nothing from the spec's Out of scope list; nothing changed that the spec does not require | Pass | Pass: [research.md](research.md) lists each change with its FR and lists what stays unchanged. A change that no FR needs (for example a maximum help length, a "suspicious" score, a landing page) is rejected there. |
| II. Testable Requirements | Every FR has an automated test that names its FR ID | Pass | Pass: V1 tests keep their logic but are renamed to V2 FR IDs; changed behaviors get new tests. Map in [quickstart.md](quickstart.md). |
| III. Traceability | Stories cite goals, FRs cite story and REQ, tasks cite FRs | Pass (spec) | Pass: data model and contracts cite V2 FRs. Note: the constitution names `docs/initial-spec.md` as the REQ source; V2 uses `docs/goal-model.md`. The constitution wording should be updated with `/speckit-constitution`; this does not block the plan. |
| IV. Mock Data Only | No backend, API, database, auth or network call | Pass | Pass: still mock seed plus `localStorage`. The deployment step publishes static files only. |

No violations. Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/002-fair-exam-prototype-v2/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── rules-api.md
│   └── ui.md
├── checklists/
│   └── requirements.md
└── tasks.md              # created by /speckit-tasks
```

### Source Code (repository root)

The V1 tree is kept. Only the files marked below change; unmarked files are untouched.

```text
frontend/
├── index.html                 # no change
├── package.json               # no change
├── css/styles.css             # small: styles for the help reason field and signal list
├── js/
│   ├── main.js                # no change (store key comes from store.js)
│   ├── data/mock-data.js      # CHANGED: help reason options, seeded flags use signalIds
│   ├── rules/
│   │   ├── store.js           # CHANGED: key fairExam.v2
│   │   ├── timer.js           # CHANGED: openPause takes a reason; closePause clears the fast-answer window
│   │   ├── signals.js         # CHANGED: addSignal adds to the student's one flag; connection-loss leave does not start the fast-answer window
│   │   ├── grouping.js        # CHANGED: MIN_GROUP_SIZE 2
│   │   ├── flags.js           # CHANGED: one flag per student with signalIds and hasNewSignals; flagView lists all signals
│   │   ├── referral.js        # CHANGED: evidence lists all signals
│   │   ├── clock.js, start-page.js, versions.js   # no change
│   └── ui/
│       ├── student-view.js    # CHANGED: reason field on the help request; flag shows all signals
│       ├── instructor-view.js # CHANGED: flag detail lists all signals and clears the New signals mark; flag list is one row per student with that mark
│       ├── office-view.js     # CHANGED: referral document lists all signals
│       └── exam-events.js, format.js, role-selector.js   # no change
└── tests/                     # V1 tests renamed to V2 FR IDs; new tests for changed behavior
```

**Structure Decision**: Keep the V1 layout (static app in `frontend/`, DOM-free rules in
`js/rules/`, rendering in `js/ui/`). No new modules, folders or dependencies.

### Deployment (separate from V1)

```text
gh-pages branch
├── .nojekyll
├── index.html      # existing, not edited by this plan
├── v1/             # existing V1 build, not touched
└── v2/             # NEW: contents of frontend/ at the v2 tag
```

V1 stays at `https://dylan40907.github.io/hw3-sdd/v1/` and V2 goes to `.../v2/`, so both can be opened
side by side. Both are the same origin, so they would share `localStorage`; the V2 key change (R6)
prevents V2 from reading V1 data. Publishing is outward-facing and is done as a task after tests
pass, with the user's confirmation, not by `/speckit-plan`.

## Complexity Tracking

No constitution violations to justify.
