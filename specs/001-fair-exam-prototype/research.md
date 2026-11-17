# Research: Fair Exam Prototype V1

No NEEDS CLARIFICATION items remained in Technical Context. Each decision below covers a technology
choice or a way to make an FR testable.

## R1. Modules without a build step

- **Decision**: Native ES modules (`<script type="module">`) in the browser, the same files imported
  by Node tests. `frontend/package.json` sets `"type": "module"` so Node treats `.js` as ES modules.
- **Rationale**: One code path for browser and tests, no bundler, works on any static host.
- **Alternatives considered**: A bundler (adds a build step, excluded by the user input); `.mjs`
  files (works, but `package.json` keeps file names plain).

## R2. Testing time-based rules (FR-001, FR-008, FR-010, FR-015 to FR-017, FR-020, FR-023)

- **Decision**: Every rule takes the current time as a `now` argument (milliseconds). The UI gets it
  from `clock.js`; tests pass fixed values.
- **Rationale**: 90-minute exams, 30-second windows and 3-day deadlines can be tested instantly and
  repeatably.
- **Alternatives considered**: `node:test` mock timers (works for timers but not for `Date.now()`
  across modules as cleanly); waiting in real time (not practical).

## R3. Testing storage and reload (FR-003, FR-022)

- **Decision**: `store.js` takes a storage object with `getItem` and `setItem`. The browser passes
  `localStorage`; tests pass a small in-memory object. A reload is tested by saving, creating a new
  store from the same storage, and loading.
- **Rationale**: No dependency on browser globals in tests.
- **Alternatives considered**: Node's experimental `localStorage` (behind a flag, file-backed);
  jsdom (an npm dependency).

## R4. Testing browser event wiring (FR-005 to FR-007, FR-021, FR-022)

- **Decision**: `exam-events.js` exports `attachExamEvents({ doc, win, examEl, onEvent })`. It uses
  only `addEventListener`, `document.visibilityState`, `document.fullscreenElement` and
  `element.requestFullscreen()`. Tests pass Node's built-in `EventTarget` objects with those
  properties added and dispatch `Event` objects.
- **Rationale**: Node 20+ has `EventTarget` and `Event` built in, so the wiring is tested without a
  browser or packages.
- **Alternatives considered**: Browser end-to-end tests (needs Playwright or similar); leaving the
  wiring untested (breaks Principle II).

## R5. Detecting a page leave (FR-006, FR-008)

- **Decision**: A leave starts on the first of `visibilitychange` to `hidden` or window `blur`, and
  ends on the first of `visibilitychange` to `visible` or window `focus`. One leave records one
  page-leave signal. The return time is kept for the fast-answer check. Exiting fullscreen
  (`fullscreenchange` with no `fullscreenElement`) records its own signal.
- **Reload (FR-022)**: a reload fires `visibilitychange` to hidden and `blur` first, so `startLeave`
  saves an open leave that `endLeave` never closes. On load of a running exam, `recordReload`
  closes that open leave (or uses `now` as both ends if none is open), records exactly one
  `page_leave` signal with `cause: "reload"`, and sets `lastReturnAt = now` like `endLeave`.
- **Rationale**: `visibilitychange` catches tab switches; `blur` catches switching to another
  window. Merging them avoids two signals for one leave.
- **Alternatives considered**: `visibilitychange` only (misses another app over the browser);
  `blur` only (also fires when focus moves into browser chrome, so it is merged rather than used
  alone).

## R6. Fast answer after return (FR-008)

- **Decision**: Each question has a Submit button (clarification). A fast-answer signal is recorded
  when Submit is pressed and `now - lastReturnAt <= 30000`.
- **Rationale**: Matches REQ-08 and the 30-second assumption; the boundary (exactly 30 s) counts.
- **Alternatives considered**: Strictly less than 30 s (the spec says "within 30 seconds", read as
  inclusive).

## R7. Timer, pauses and reload (FR-001, FR-010, FR-020, FR-022)

- **Decision**: Store `startedAt`, `baseDurationMs = length * (1 + extraTimePct / 100)` and a list
  of pauses. End time = `startedAt + baseDurationMs + sum of closed pause lengths`. While a pause is
  open, remaining time is frozen at the value when it opened, and its open length is added to the end
  time. A reload keeps all of these, so the timer keeps running while the page is gone.
- **Rationale**: One formula covers REQ-01, REQ-10 and the "help open at end time" edge case: the
  end time moves later by the pause length automatically.
- **Alternatives considered**: A countdown counter saved every second (loses time on reload and
  drifts).

## R8. Detection during help (FR-010)

- **Decision**: `signals.js` drops page-leave, fullscreen-exit, paste and fast-answer signals when a
  help request is open. Offline and online times are still recorded as context. A return that ends a
  leave which started during help does not start the 30-second window.
- **Rationale**: REQ-10 says nothing is detected until the request is closed.

## R9. Question versions (FR-004)

- **Decision**: Each question is a template with numeric parameters. A version is picked by a
  deterministic hash of `studentId + questionId`, recorded in state the first time the student opens
  the question, and never changed. The correct answer is computed from the version.
- **Rationale**: Recorded and repeatable; two mock students get different versions.
- **Alternatives considered**: `Math.random()` (not repeatable in tests).

## R10. Same incorrect answer groups (FR-009)

- **Decision**: One rule function, `processExamEnd(state, exam, students, now)` in `grouping.js`,
  does all end-of-exam work:
  1. Sets `endedAt` on every started live session whose end time has passed and has no `endedAt`
     yet ("Finish exam" sets it directly).
  2. Collects answers from live sessions with `endedAt` set and from the pre-filled mock students,
     keeps the incorrect ones (compared against each student's own version), normalizes them as
     numbers, and groups equal values. Groups of 3 or more are stored with the ID
     `questionId:value`, adding new members if the group grows.
  3. For every student in each group, live or pre-filled, records one `same_incorrect_answer`
     signal (and so one flag) with that `groupId`, unless that student already has one.

  `main.js` calls it on load and on every 1-second tick in every role, so groups form even when no
  student page is open. Running it again changes nothing.
- **Rationale**: Matches the clarifications (3 or more, one flag per student). Keeping the check
  in one place makes it safe to run repeatedly and removes the need to seed group flags.
- **Alternatives considered**: Running grouping only from the student screen (misses students who
  closed the tab, and creates duplicates after Finish and reload).

## R11. Dropped connection (FR-021)

- **Decision**: Record `offline` and `online` window events as offline periods. When a page-leave
  signal's time range overlaps an offline period, its flag shows "connection lost".
- **Rationale**: Matches the clarification and needs no server.

## R12. Flag states and visibility (FR-012 to FR-017, FR-023)

- **Decision**: A flag has one state: `new`, `kept`, `dismissed`, `explanation_requested`,
  `explained`, `referred`. It also keeps `explanationRequestedAt`, so a dismissed flag that had an
  explanation request stays visible to the student, marked as dismissed. Transitions are in
  [data-model.md](data-model.md).
- **Rationale**: One place enforces REQ-13 to REQ-17 and the deadline edge case.

## R13. Read-only referral document (FR-018, FR-019)

- **Decision**: The referral document is built once on referral, stored as a snapshot, and returned
  with `Object.freeze` (deep). The office view renders it as text with no inputs.
- **Rationale**: Later flag changes cannot alter the document, and the UI has nothing to edit.

## R14. Deployment

- **Decision**: Serve `frontend/` as the site root on any static host (for example GitHub Pages
  from a workflow that uploads `frontend/`). All asset paths are relative.
- **Rationale**: Meets "deployable as a static site" with no build.
- **Local run**: any static server, for example `python -m http.server` from `frontend/`.
