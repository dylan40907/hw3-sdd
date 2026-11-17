# Implementation Plan: Fair Exam Prototype V1

**Branch**: `001-fair-exam-prototype` (work is on `main`) | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-fair-exam-prototype/spec.md`

## Summary

A browser-only prototype of one timed exam with three roles: student, instructor and integrity
office. The student takes the exam with extra time applied, autosave, a help request that pauses the
timer, and detection of page leaves, fullscreen exits, pastes and fast answers after returning. The
instructor reviews flags with context, asks for explanations, dismisses or refers. The integrity
office reads referral documents. It is built as static HTML, CSS and JavaScript ES modules in
`frontend/` with no build step and no backend. All rules (timer, versions, signals, grouping, flag
states, referral) live in DOM-free modules tested with Node's built-in test runner. Event wiring is
tested with Node's built-in `EventTarget` and fake document objects. State is kept in
`localStorage`, so all roles in one browser share it.

## Technical Context

**Language/Version**: JavaScript (ES2022 modules), HTML5, CSS3; Node.js 20+ for tests (24.x
installed)

**Primary Dependencies**: None. No frameworks, no npm packages.

**Storage**: Browser `localStorage`, one JSON document under one key; mock seed data in a JS module

**Testing**: `node --test` (Node's built-in test runner and `node:assert`), run from `frontend/`

**Target Platform**: Current desktop Chrome, Edge and Firefox; any static host

**Project Type**: Static single-page web app

**Performance Goals**: Timer display updates once per second; every action renders within the same
frame for the mock data size

**Constraints**: No build step, no backend, no network calls, served over HTTP (ES modules do not
load from `file://`), all paths relative so it works from a subfolder on a static host

**Scale/Scope**: 1 exam, 3 questions, 5 mock students (2 playable, 3 with pre-filled answers),
3 roles, about 6 screens

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Pre-design | Post-design |
|---|---|---|---|
| I. Spec Scope Only | Every module and screen maps to an FR; nothing from the spec's Out of scope list | Pass | Pass: [contracts/ui.md](contracts/ui.md) and [contracts/rules-api.md](contracts/rules-api.md) list the FR for every screen and function. "Finish exam" (FR-009) and offline tracking (FR-021) come from clarifications. |
| II. Testable Requirements | Every FR has at least one automated test that names its FR ID | Pass | Pass: [research.md](research.md) R2 to R4 make UI-bound FRs (FR-003, FR-005 to FR-008, FR-021, FR-022) testable in Node through injected storage, clock and event targets. The FR to test file map is in [quickstart.md](quickstart.md). |
| III. Traceability | Stories cite goals, FRs cite story and REQ, tasks cite FRs | Pass (spec) | Pass: data model fields and contract entries cite FRs; tasks are checked at `/speckit-tasks`. |
| IV. Mock Data Only | No backend, API, database, auth or network call | Pass | Pass: mock seed module plus `localStorage`; no `fetch` anywhere. |

No violations. Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-fair-exam-prototype/
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

```text
frontend/
├── index.html                 # role selector and view containers
├── package.json               # "type": "module", "test": "node --test"
├── css/
│   └── styles.css
├── js/
│   ├── main.js                # boot: load state, render role, 1 s tick that runs processExamEnd
│   ├── data/
│   │   └── mock-data.js       # exam, questions, students, pre-filled answers, seeded flags
│   ├── rules/                 # pure functions, no DOM
│   │   ├── clock.js           # now() wrapper, injectable for tests
│   │   ├── store.js           # load/save state with an injected storage
│   │   ├── timer.js           # end time, remaining time, pauses
│   │   ├── start-page.js      # start page summary, canStart
│   │   ├── versions.js        # question versions, correctness and saved answers
│   │   ├── signals.js         # signal creation, suppression during help, fast answer, offline overlap
│   │   ├── grouping.js        # end-of-exam processing and same incorrect answer groups
│   │   ├── flags.js           # flag creation and state transitions, student visibility
│   │   └── referral.js        # referral document
│   └── ui/                    # DOM rendering and event wiring
│       ├── format.js          # HTML escaping and time formatting
│       ├── role-selector.js
│       ├── exam-events.js     # page leave, fullscreen, paste, online/offline, reload wiring
│       ├── student-view.js
│       ├── instructor-view.js
│       └── office-view.js
└── tests/
    ├── helpers.js             # fake storage, fake document and window, time constants
    ├── state-fixtures.js      # test states built from the seed
    ├── timer.test.js
    ├── start-page.test.js
    ├── store.test.js
    ├── versions.test.js
    ├── signals.test.js
    ├── grouping.test.js
    ├── flags.test.js
    ├── referral.test.js
    └── exam-events.test.js
```

**Structure Decision**: One static web app in `frontend/`, matching the repository layout in
`README.md`. The `frontend/` folder is the site root when deployed. Rules are split from UI so every
FR can be tested in Node without a browser or extra packages.

## Complexity Tracking

No constitution violations to justify.
