---

description: "Task list for Fair Exam Prototype V2"
---

# Tasks: Fair Exam Prototype V2

**Input**: Design documents from `specs/002-fair-exam-prototype-v2/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Required. The constitution (Principle II) requires at least one automated test per FR.
Every test name starts with the V2 FR IDs it covers, for example
`test("FR-008 REQ-08: no fast-answer signal after a connection loss", ...)`. Write each story's
tests first and check they fail before implementing.

**Traceability**: Every task cites the V2 FR IDs it implements or tests (Principle III).

**Organization**: Tasks are grouped by user story, in priority order (P1: US1, US2, US3, US5;
P2: US4, US6, US7). This is an edit of the V1 code in `frontend/`, not a rewrite: do not add files,
folders or dependencies, and do not touch code that is not named below (plan.md, Principle I).

## Format: `[ID] [P?] [Story] FR-IDs: Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story from spec.md (US1 to US7)
- All paths are relative to the repository root

## Shared conventions (apply to every task)

- Rules modules in `frontend/js/rules/` never touch the DOM, take `now` (ms) as an argument, return
  new objects, and return `{ ok: false, error }` for rejected actions (see
  [contracts/rules-api.md](contracts/rules-api.md)).
- Tests import from `../js/...` and use only `node:test` and `node:assert/strict`.
- UI modules in `frontend/js/ui/` read and write state only through the store and rules modules.
- No `fetch`, no npm dependencies, all asset paths relative.
- FR numbers differ from V1 in one place: autosave is now FR-004 (was FR-003) and versions are now
  FR-003 (was FR-004). All other FR numbers are the same as V1.
- V1 is not modified: `v1` tag and `gh-pages/v1/` stay as they are.

---

## Phase 1: Setup

**Purpose**: Confirm the starting point

- [X] T001 FR-001 to FR-023: Run `cd frontend && node --test` on the unchanged V1 code and confirm every test passes, so later failures are known to come from V2 changes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The one-flag-per-student data shape (FR-012) is used by signals, grouping, referral and
all three views, and V2 state must be stored apart from V1. Both must be done before any story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 FR-004: In `frontend/tests/store.test.js` add a test that `STORAGE_KEY` equals `"fairExam.v2"` and that a saved state is stored under that key and not under `"fairExam.v1"`; check it fails
- [X] T003 FR-004: In `frontend/js/rules/store.js` change `STORAGE_KEY` to `'fairExam.v2'`; make T002 pass (data-model.md "Stored state", research.md R6)
- [X] T004 FR-012: In `frontend/tests/flags.test.js` replace the test "every recorded signal becomes exactly one new flag" with tests that (a) two signals for the same student give one flag whose `signalIds` has both IDs in the order recorded, (b) signals for two different students give two flags, (c) the first signal creates a flag with `state: 'new'` and `hasNewSignals: false`. Change the tests that read `view.what`, `view.why` and `view.signal` to read `view.signals[i].what`, `.why` and `.signal`, and assert `view.context` has `extraTimePct`, `pauses` and `groups`. Check they fail
- [X] T005 FR-012: Implement the data-model.md Flag shape. In `frontend/js/rules/flags.js` make `createFlag` return `signalIds: [signal.id]` and `hasNewSignals: false` (no `signalId`), and make `flagView` return `{ signals: [{ signal, what, when, until, why, technicalEvent }], context: { extraTimePct, pauses, groups } }` with `technicalEvent` computed per signal and `groups` listing question, shared value and other students for each `same_incorrect_answer` signal. In `frontend/js/rules/signals.js` make `addSignal` create the student's flag on the first signal and otherwise append the signal ID to the student's existing flag; it must never create a second flag for a student. Make T004 pass
- [X] T006 FR-012, FR-009: In `frontend/js/data/mock-data.js` change seeded flags `flag-s1` and `flag-s2` from `signalId: 'sig-s1'` / `'sig-s2'` to `signalIds: ['sig-s1']` / `['sig-s2']` and add `hasNewSignals: false` to both
- [X] T007 FR-018, FR-019, FR-012: In `frontend/tests/referral.test.js` update the tests that build or read a referral document to the new shape: `document.flag.signals` (each with what, when, until, why), `document.flag.context`, and `document.evidence.signals` (each with type, at, until, details, technicalEvent) and `document.evidence.groups`; check they fail
- [X] T008 FR-018, FR-012: In `frontend/js/rules/referral.js` change `buildReferralDocument` and `refer` to build `flag` and `evidence` from the new `flagView` (all signals), per data-model.md "ReferralDocument"; keep `explanation`, `reason`, the deep freeze and the `NO_EXPLANATION` text unchanged; make T007 pass
- [X] T009 [P] FR-012: In `frontend/js/ui/instructor-view.js` change the flag list (about line 126) and flag detail (about line 170) so they compile and work with the new `flagView`: sort by the latest signal time, and show every signal with what, when and why in the detail (the full layout is finished in US5)
- [X] T010 [P] FR-012, FR-015: In `frontend/js/ui/student-view.js` change `renderMyFlags` to list every signal of each flag as its own item with what, when and why (using `flagView(f, state).signals`), followed by the deadline and the existing dismissed marking and explanation form; do not show `hasNewSignals`
- [X] T011 [P] FR-018, FR-019: In `frontend/js/ui/office-view.js` change the referral document view to list every signal in `document.flag.signals` as text (what, when, why, "connection lost" mark when `technicalEvent` is set), then the context, explanation (or "No explanation was given before the deadline.") and reason; keep it free of inputs

**Checkpoint**: `cd frontend && node --test` passes; the page loads over HTTP; the seeded flags show in
the instructor view

---

## Phase 3: User Story 1 - Take the exam with accommodations applied (Priority: P1) 🎯 MVP

**Goal**: Extra time applied, one confirmed start page, answers saved while typing (REQ-01, REQ-02,
REQ-04)

**Independent Test**: Start as Student A (50% extra time): the end time is 90 minutes after the start,
the exam does not start until confirmed, a typed answer survives a reload

- [X] T012 [US1] FR-004: Rename the autosave tests to the V2 FR ID: in `frontend/tests/store.test.js` change the prefix `FR-003` to `FR-004` on all four test names (including "FR-003 REQ-04" to "FR-004 REQ-04" and "FR-003 FR-022" to "FR-004 FR-022"), and in `frontend/tests/versions.test.js` change the two `saveAnswer` tests ("FR-003: saveAnswer ..." and "FR-003: saving again ...") to `FR-004`

**Checkpoint**: `node --test tests/timer.test.js tests/start-page.test.js tests/store.test.js` passes
with no change to `timer.js` or `start-page.js`; tests for FR-001, FR-002, FR-004 and FR-022 are named
with those IDs

---

## Phase 4: User Story 2 - Give each student their own questions (Priority: P1)

**Goal**: Each student gets their own numeric version, and it is recorded (REQ-03)

**Independent Test**: Open the same question as two mock students; the recorded versions differ

- [X] T013 [US2] FR-003: Rename the version tests to the V2 FR ID: in `frontend/tests/versions.test.js` change the prefix `FR-004` to `FR-003` on the tests "versionFor gives the same version ...", "two students get their own version ... and each is recorded" and "opening a question again does not change the recorded version"; in `frontend/tests/grouping.test.js` change "FR-004 FR-009: the live student is graded against their own recorded version" to "FR-003 FR-009: ..."; and in `frontend/tests/versions.test.js` change "FR-009: correctAnswer uses the version params" to "FR-003: correctAnswer uses the version params"

**Checkpoint**: `node --test tests/versions.test.js` passes with no change to `versions.js`

---

## Phase 5: User Story 3 - Record exam signals (Priority: P1)

**Goal**: Fullscreen, page leave, paste, fast answer (not after a connection loss or help request) and
shared incorrect answer groups of 2 or more (REQ-05 to REQ-09)

**Independent Test**: Run the exam as a mock student; switch tabs, paste, answer within 30 seconds of
returning, repeat after a simulated connection loss and after a help request, and end the exam with a
shared incorrect answer

### Tests for User Story 3 (write first, check they fail)

- [X] T014 [US3] FR-008, FR-021: In `frontend/tests/signals.test.js` add tests: (a) a page leave that overlaps an offline period still records one `page_leave` signal and its flag view shows `technicalEvent: 'connection lost'`, but a `submitAnswer` within 30 seconds of returning records no `fast_answer` signal (REQ-08 second scenario); (b) the same when the student is still offline at the moment of return
- [X] T015 [US3] FR-008, FR-010, FR-004: In `frontend/tests/signals.test.js` add tests: (a) the student leaves and returns, opens a help request and closes it, then calls `submitAnswer` within 30 seconds of the earlier return: no `fast_answer` signal; (b) `saveAnswer` right after returning records no signal and only `submitAnswer` records one (clarified: Submit only, autosave never counts)
- [X] T016 [US3] FR-022, FR-021, FR-008: In `frontend/tests/signals.test.js` add a test: `recordReload` during an offline period records exactly one `page_leave` signal marked as a reload and a following `submitAnswer` within 30 seconds records no `fast_answer`
- [X] T017 [P] [US3] FR-009: In `frontend/tests/grouping.test.js` change the test "two students with the same incorrect answer are not grouped" to expect one group with both students, add a test that one student with a unique incorrect answer forms no group, and update the other tests whose expectations assume a minimum of 3 (the pre-filled s3 and s4 now form a group of 2 at the first exam end, and a live student with the same value grows it to 3)
- [X] T018 [P] [US3] FR-009, FR-012: In `frontend/tests/flags.test.js` add a test for the REQ-09 scenario: three students give the same incorrect answer, the exam ends, and each student's one flag has a `same_incorrect_answer` signal in `flagView(...).signals` and a `context.groups` entry with the shared value and the other two students; a student with an earlier page-leave signal still has exactly one flag with both signals

### Implementation for User Story 3

- [X] T019 [US3] FR-008, FR-021, FR-022: In `frontend/js/rules/signals.js` add one helper that tells whether a leave overlaps an offline period (the same test `technicalEvent` uses: `p.from <= end && (p.to ?? Infinity) >= at`), use it in `technicalEvent`, and in `endLeave` and `recordReload` mark the closed leave `connectionLoss: true` when it overlaps; for such a leave still record the `page_leave` signal but do not set `lastReturnAt`. Make T014 and T016 pass
- [X] T020 [P] [US3] FR-008, FR-010: In `frontend/js/rules/timer.js` make `closePause` also set the session's `lastReturnAt` to `null`; make T015 pass
- [X] T021 [P] [US3] FR-009: In `frontend/js/rules/grouping.js` change `MIN_GROUP_SIZE` from 3 to 2, and in `frontend/js/data/mock-data.js` change the comment on `SHARED_INCORRECT_Q2` to say a live student who also answers 50 joins the group of s3 and s4; make T017 and T018 pass

**Checkpoint**: `node --test tests/signals.test.js tests/grouping.test.js tests/exam-events.test.js` passes;
tests for FR-005, FR-006, FR-007, FR-008, FR-009, FR-021 and FR-022 are named with those IDs

---

## Phase 6: User Story 5 - Instructor reviews one flag per student (Priority: P1)

**Goal**: One flag per student with all signals and context, a "New signals" mark, review before the
student sees it, dismiss (REQ-12, REQ-13, REQ-14)

**Independent Test**: Create two signals for one student, open the instructor flag list (one row), keep
the flag, add a third signal (mark appears), open it (mark clears), check the student cannot see it,
dismiss it and try to refer it

### Tests for User Story 5 (write first, check they fail)

- [X] T022 [US5] FR-012: In `frontend/tests/flags.test.js` add tests: (a) a signal added to a flag in state `kept`, `dismissed`, `explanation_requested`, `explained` or `referred` sets `hasNewSignals` to `true` and leaves `state`, `explanation` and `deadline` unchanged; (b) a signal added to a `new` flag leaves `hasNewSignals` `false`; (c) `markFlagSeen(state, flagId)` sets it back to `false` and changes nothing else
- [X] T023 [US5] FR-013, FR-014: In `frontend/tests/flags.test.js` add tests: (a) a student with a two-signal flag that is `new` or `kept` sees nothing from `studentFlags`; (b) a flag dismissed after an explanation request is returned by `studentFlags` with `dismissed: true` and its `flagView` still lists both signals; (c) a dismissed flag cannot be referred

### Implementation for User Story 5

- [X] T024 [P] [US5] FR-012: In `frontend/js/rules/signals.js` make `addSignal` set the student's flag `hasNewSignals` to `true` when it appends to a flag whose `state` is not `'new'`, and leave `state`, `explanation`, `deadline` and `createdAt` unchanged
- [X] T025 [P] [US5] FR-012: In `frontend/js/rules/flags.js` add and export `markFlagSeen(state, flagId)` that returns a state where that flag's `hasNewSignals` is `false` (same state object if already `false`); make T022 and T023 pass
- [X] T026 [US5] FR-012: In `frontend/js/ui/instructor-view.js` make the flag list one row per student (one flag per exam) showing the student name, the number of signals, the state, the time of the latest signal, and a "New signals" mark when `hasNewSignals` is true (contracts/ui.md, Instructor, Flag list)
- [X] T027 [US5] FR-011, FR-012, FR-021: In `frontend/js/ui/instructor-view.js` make the flag detail list every signal with what, when and why and a "connection lost" mark where `technicalEvent` is set, then one context block with extra time, pauses (the student's reason and length) and group members for each group signal; opening a flag calls `markFlagSeen` through `ctx.update` so the mark clears; keep the Keep, Dismiss, Ask for explanation and Refer actions and their rules unchanged
- [X] T028 [P] [US5] FR-012: In `frontend/css/styles.css` add a `.new-signals` badge style next to the existing `.flag-state` style

**Checkpoint**: `node --test tests/flags.test.js` passes; in the browser the instructor sees one row per
student and the mark appears and clears

---

## Phase 7: User Story 4 - Ask for help without losing time (Priority: P2)

**Goal**: A help request with a reason pauses the timer, hides the questions and stops detection, and
is recorded with its reason and length (REQ-10, REQ-11)

**Independent Test**: With 20 minutes left, try a help request with no reason (refused), open one with
a reason, switch tabs, close it after 2 minutes; check the hidden questions, the 20 minutes, the
recorded pause and the absence of a page-leave signal

### Tests for User Story 4 (write first, check they fail)

- [X] T029 [US4] FR-010, FR-011: In `frontend/tests/timer.test.js` change every `openPause(session, now)` call to `openPause(session, now, 'Technical problem')` (lines about 54, 61, 62, 67, 74) and add tests: (a) `openPause` with `''` or `'   '` returns `{ ok: false }` and opens nothing; (b) the opened pause stores the trimmed reason and `pauseLog` returns it with the length; (c) `questionsHidden(session)` is `true` while a pause is open and `false` after `closePause`; (d) `exam.helpReasons` from `frontend/js/data/mock-data.js` is a non-empty array of non-empty strings. The REQ-10 test (20 minutes left, 2-minute request) must also assert `questionsHidden` is `true` during it
- [X] T030 [US4] FR-010: In `frontend/tests/signals.test.js` update every `openPause(...)` call in the help tests (about lines 118 to 142) to pass a reason, and check no other test in `frontend/tests/` still calls `openPause` with two arguments (`grep -rn "openPause(" frontend/tests`)

### Implementation for User Story 4

- [X] T031 [US4] FR-010, FR-011: In `frontend/js/rules/timer.js` change `openPause(session, now, reason)` so it trims `reason`, returns `{ ok: false, error: 'Pick or type a reason for the help request.' }` when it is empty, and stores the trimmed `reason` on the pause; remove the `PAUSE_REASON` constant (not used elsewhere); add and export `questionsHidden(session)` that returns `Boolean(openPauseOf(session))`; keep one open pause at a time and `pauseLog` unchanged; make T029 and T030 pass
- [X] T032 [P] [US4] FR-010: In `frontend/js/data/mock-data.js` add `helpReasons` to `exam` with three entries: `'Technical problem'`, `'I do not understand a question'`, `'Accessibility need'` (data-model.md "Exam")
- [X] T033 [US4] FR-010, FR-011: In `frontend/js/ui/student-view.js` change `renderExam` so "Request help" shows a reason `<select>` built from `exam.helpReasons` with an empty first option and a text input for another reason; the typed text is used when it is not empty, otherwise the selected option; the value goes to `openPause(session, now, reason)`; a refused request shows the error through `ctx.update`; the open help panel shows the reason; the questions are rendered only when `questionsHidden(session)` is false
- [X] T034 [P] [US4] FR-010: In `frontend/css/styles.css` add minimal styles for the help reason field (same field styles as the answer input)
- [X] T044 [US4] FR-010: Keep a half-typed or picked help reason when the exam page is rendered again: in `frontend/js/ui/student-view.js` hold the draft in a module variable (reset when the current student changes or after the request opens), render it through an exported `helpFormHtml(helpReasons, draft)`, and update it from the `change` and `input` events; test it in `frontend/tests/timer.test.js`

**Checkpoint**: `node --test tests/timer.test.js tests/signals.test.js` passes; in the browser the help
request is refused without a reason and hides the questions

---

## Phase 8: User Story 6 - Student explains a flag (Priority: P2)

**Goal**: The student sees a flag only after the explanation request, with all its signals and the
deadline, and submits an explanation (REQ-15, REQ-16)

**Independent Test**: As the instructor keep a flag, as the student check before and after the request,
submit an explanation, read it as the instructor

- [X] T035 [US6] FR-015, FR-016: In `frontend/tests/flags.test.js` update the tests "the student sees only the flag they were asked to explain, with its deadline" and "an explanation submitted before the deadline is shown to the instructor" to use a student with a two-signal flag: before the request `studentFlags` is empty, after it the flag is returned with its deadline 3 days later and `flagView` lists both signals; an explanation submitted before the deadline is stored on the flag, one after the deadline or empty is rejected

**Checkpoint**: `node --test tests/flags.test.js` passes; the student view (T010) shows each signal as its
own item

---

## Phase 9: User Story 7 - Refer a flag to the integrity office (Priority: P2)

**Goal**: Refer after the explanation or the deadline, with a reason; the document lists every signal and
is read-only (REQ-17, REQ-18, REQ-19)

**Independent Test**: Refer an explained flag and one whose deadline passed without an explanation;
refuse a flag never sent for explanation; open each document as the integrity office

- [X] T036 [US7] FR-017, FR-018, FR-019, FR-023: In `frontend/tests/referral.test.js` add or update tests: (a) a flag with two signals gives a referral document whose `flag.signals` and `evidence.signals` each have both signals, plus the explanation and the reason; (b) a flag in state `kept` (never sent for explanation) cannot be referred; (c) after the deadline with no explanation the document's `explanation` is "No explanation was given before the deadline."; (d) the document is deeply frozen and an assignment to it throws in strict mode
- [X] T037 [US7] FR-012, FR-018, FR-019: In `frontend/tests/referral.test.js` add a test: a signal added after the flag was referred is appended to the flag with `hasNewSignals: true`, the flag stays `referred`, and the stored referral document is unchanged (same `flag.signals` and `evidence.signals` as before)

**Checkpoint**: `node --test tests/referral.test.js` passes; the office view (T011) opens both seeded
documents with no inputs

---

## Phase 10: Polish, Traceability and Deployment

**Purpose**: Gates required before the version is tagged (constitution, Quality Gates)

- [X] T038 FR-001 to FR-023: Run `cd frontend && node --test` and confirm every test passes; confirm each of FR-001 to FR-023 is named in at least one test (`grep -rhoE "FR-0[0-9]{2}" frontend/tests | sort -u` lists all 23)
- [X] T039 FR-001 to FR-023: Update `docs/traceability.md` with a V2 section listing every goal, REQ, user story, FR and test file for V2, using the FR to test map in [quickstart.md](quickstart.md); leave the V1 section unchanged
- [X] T040 FR-001 to FR-023: Run the 13 manual scenarios in [quickstart.md](quickstart.md) against `python -m http.server 8000` from `frontend/`, and run scenarios 4 to 7 against V1 (`git worktree add` the `v1` tag in the scratchpad directory, not in the repository) to confirm the differences listed there; report any scenario that fails
- [X] T041 Deployment: After the user confirms, commit, tag `v2`, and publish `frontend/` at that tag into `v2/` on the `gh-pages` branch without touching `v1/`, `index.html` or `.nojekyll`; push. This pushes to the shared remote, so ask first (plan.md "Deployment", research.md R7)
- [X] T042 Deployment: Open `/v1/` and `/v2/` of the published site in one browser; check both load, an action in V2 does not appear in V1 and the reverse, and V1 still shows one flag per signal while V2 shows one per student
- [X] T043 Deployment: In `README.md` fill the "GitHub Version 2" and "Prototype V2" rows with the v2 tag link and `https://dylan40907.github.io/hw3-sdd/v2/`, and write "What changed from V1 to V2" from the change list in [research.md](research.md); do not edit the "Roles and Responsibilities" table

---

## Dependencies and Execution Order

- **Phase 1** then **Phase 2** (blocks everything). Inside Phase 2: T002 → T003; T004 → T005 → T006; T007 → T008 (after T005); T009, T010, T011 [P] after T005.
- **US1** (T012) and **US2** (T013) only rename tests; both edit `versions.test.js`, so run T012 then T013.
- **US3** (T014 to T021) depends on Phase 2. Tests T014 to T016 share `signals.test.js` and run in order; T017 and T018 are [P]. T019 follows T014 and T016; T020 follows T015; T021 follows T017 and T018.
- **US5** (T022 to T028) depends on Phase 2. T024 and T025 are [P]; T026 and T027 share one file and run in order after T025; T028 is [P]. T024 shares `signals.js` with T019, so run T019 first.
- **US4** (T029 to T034) depends on Phase 2 and on T020 (same `timer.js`). T029 then T030 before T031; T032 and T034 are [P]; T033 follows T031 and T032.
- **US6** (T035) depends on US5 tests (same file `flags.test.js`). **US7** (T036, T037) depends on T008 and T024.
- **Phase 10** after all stories. T041 waits for the user's confirmation.
- Stories do not depend on each other for their rules logic, except as noted for shared files.

### Parallel opportunities

- Phase 2: T009, T010, T011 (three view files)
- US3: T017 and T018 (two test files); T020 and T021 (two source files)
- US5: T024 and T025 (two rules files); T028 with T026
- US4: T032 and T034 with T031

## Implementation Strategy

1. **MVP**: Phases 1 and 2, then US1, US2, US3 and US5 (all P1). This gives the one-flag-per-student
   model, the corrected signals and groups, and the instructor review, which are the V2 changes that
   decide the comparison with V1.
2. Add US4 (help reason), then US6 and US7 (tests for the explanation and referral path, which keep
   their V1 behavior).
3. Finish with Phase 10. Do not deploy before T038 and T040 pass and the user confirms T041.
