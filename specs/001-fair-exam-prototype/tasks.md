---

description: "Task list for Fair Exam Prototype V1"
---

# Tasks: Fair Exam Prototype V1

**Input**: Design documents from `specs/001-fair-exam-prototype/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Required. The constitution (Principle II) requires at least one automated test per FR.
Every test name starts with the FR IDs it covers, for example
`test("FR-001 REQ-01: 50% extra time on 60 minutes ends 90 minutes after start", ...)`.
Write each story's tests first and check they fail before implementing.

**Traceability**: Every task cites the FR IDs it implements or tests (Principle III).

**Organization**: Tasks are grouped by user story, in priority order (P1: US1, US2, US4; P2: US3,
US5, US6).

## Format: `[ID] [P?] [Story] FR-IDs: Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story from spec.md (US1 to US6)
- All paths are relative to the repository root

## Shared conventions (apply to every task)

- Rules modules in `frontend/js/rules/` never touch the DOM, take `now` (ms) as an argument, return
  new objects, and return `{ ok: false, error }` for rejected actions (see
  [contracts/rules-api.md](contracts/rules-api.md)).
- Tests import from `../js/...` and use only `node:test` and `node:assert/strict`.
- UI modules in `frontend/js/ui/` read and write state only through the store and rules modules,
  and save after every change.
- No `fetch`, no npm dependencies, all asset paths relative.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Folder layout, test runner and page shell

- [X] T001 FR-001 to FR-023: Create the folders `frontend/css/`, `frontend/js/data/`, `frontend/js/rules/`, `frontend/js/ui/` and `frontend/tests/` per plan.md
- [X] T002 FR-001 to FR-023: Create `frontend/package.json` with `"name": "fair-exam-prototype"`, `"private": true`, `"type": "module"`, `"scripts": { "test": "node --test" }` and no dependencies
- [X] T003 [P] FR-002, FR-012, FR-019: Create `frontend/index.html` with a header holding a role `<select id="role">` (Student, Instructor, Integrity office) and a student `<select id="student">`, three containers `#student-view`, `#instructor-view`, `#office-view`, a relative `css/styles.css` link and `<script type="module" src="js/main.js">`
- [X] T004 [P] FR-002, FR-012, FR-019: Create `frontend/css/styles.css` with base layout, a visible timer area, a `.flag-state` badge style and a `.dismissed` style
- [X] T005 [P] FR-003, FR-005 to FR-008, FR-021, FR-022: Create `frontend/tests/helpers.js` exporting `fakeStorage()` (in-memory `getItem`/`setItem`/`removeItem`), `fakeDoc()` and `fakeWin()` built on Node's `EventTarget` with writable `visibilityState` and `fullscreenElement`, `fakeExamEl()` with a spy `requestFullscreen()` that can be set to reject, and time constants `MIN = 60000`, `DAY = 86400000`, `T0 = Date.UTC(2026, 10, 16, 9, 0)`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Clock, mock data, store and app boot used by every story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 [P] FR-001, FR-008, FR-015: Create `frontend/js/rules/clock.js` exporting `now()` that returns `Date.now()`
- [X] T007 [P] FR-001, FR-002, FR-004, FR-009, FR-017, FR-023: Create `frontend/js/data/mock-data.js` exporting `exam` (`id: "exam-1"`, `lengthMinutes: 60`, `rules`, `detected` listing "leaving the exam page", "exiting fullscreen", "pasting into an answer field", "submitting an answer within 30 seconds of returning", and 3 questions `q1` to `q3` each with `template`, `params` (allowed numeric values per placeholder) and `answer(params)`), `students` (`s1` "Student A" `extraTimePct: 50` `playable: true`; `s2` "Student B" `extraTimePct: 0` `playable: true`; `s3` to `s5` `playable: false` with `prefilledAnswers` `{ questionId: { version, value } }`, where `s3` and `s4` share one value on `q2` that is incorrect for both of their versions and `s5` has a different answer), and `seed` with signals and flags for non-playable students: one flag in `explanation_requested` whose `deadline` is before `T0` with no explanation, and one in `explained` with explanation text (no group flags are seeded; `processExamEnd` creates them)
- [X] T008 FR-003, FR-022: Write `frontend/tests/store.test.js`: `load()` on empty storage returns a state built from the seed with keys `role`, `currentStudentId`, `sessions`, `signals`, `flags`, `groups`, `referrals`; `save(state)` then `load()` from a new store on the same storage returns an equal state
- [X] T009 FR-003, FR-022: Implement `createStore(storage, seed)` in `frontend/js/rules/store.js` using the key `fairExam.v1` and `JSON.stringify`/`JSON.parse`; make T008 pass
- [X] T010 FR-002, FR-012, FR-019: Implement `frontend/js/ui/role-selector.js` (renders the role select and a student select listing only `playable` students, shown only for the Student role, and saves `role` and `currentStudentId`) and `frontend/js/main.js` (creates the store with `localStorage` and `seed`, renders the selected role's container and hides the others, re-renders after every state change, and re-renders the timer once per second)

**Checkpoint**: `cd frontend && node --test` passes; the page loads over HTTP and the role selector switches containers

---

## Phase 3: User Story 1 - Take the exam with accommodations applied (Priority: P1) 🎯 MVP

**Goal**: Start page with rules, end time, accommodations and detected behaviors; extra time applied; answers autosaved and restored on reload

**Independent Test**: As Student A (50%), the start page shows an end time 90 minutes after now; the exam opens only after Confirm; a typed answer survives a reload and the timer keeps counting

### Tests for User Story 1

- [X] T011 [P] [US1] FR-001, FR-022: Write `frontend/tests/timer.test.js`: `baseDurationMs(60, 50) === 90 * MIN` and `baseDurationMs(60, 0) === 60 * MIN`; REQ-01 scenario: a session started at `T0` with 50% extra time has `endTime === T0 + 90 * MIN`; `remainingMs` at `T0 + 30 * MIN` is `60 * MIN`; after a simulated reload (same `startedAt`, later `now`) remaining time has kept counting down
- [X] T012 [P] [US1] FR-002: Write `frontend/tests/start-page.test.js`: `startPageSummary(exam, s1, T0)` returns the exam rules, `endTime === T0 + 90 * MIN`, accommodations naming 50% extra time, and the 4 detected behaviors; REQ-02 scenario: `startExam` on a session with `confirmedAt: null` returns `{ ok: false }` and leaves `startedAt` null; after `confirm`, `startExam` sets `startedAt`
- [X] T013 [P] [US1] FR-003: Add to `frontend/tests/store.test.js` and create `frontend/tests/versions.test.js`: `saveAnswer(session, "q1", "42", now)` sets `answers.q1.value === "42"` and `savedAt === now`; REQ-04 scenario: after saving the session and loading from a new store on the same storage, the answer is still `"42"`

### Implementation for User Story 1

- [X] T014 [P] [US1] FR-001, FR-022: Implement `baseDurationMs(lengthMinutes, extraTimePct)` as `lengthMinutes * 60000 * (1 + extraTimePct / 100)`, `endTime(session, now)` as `startedAt + baseDurationMs + sum of closed pause lengths + (now - openPause.from)` and `remainingMs(session, now)` as `max(0, endTime - now)` in `frontend/js/rules/timer.js`; make T011 pass
- [X] T015 [P] [US1] FR-002: Implement `startPageSummary(exam, student, now)`, `confirm(session, now)` and `startExam(session, now)` in `frontend/js/rules/start-page.js` ("Exam cannot start while `confirmedAt` is null"); make T012 pass
- [X] T016 [P] [US1] FR-003: Implement `saveAnswer(session, questionId, value, now)` in `frontend/js/rules/versions.js` per contracts/rules-api.md (keeps any existing `submittedAt`); make T013 pass
- [X] T017 [US1] FR-001, FR-002, FR-003: Implement the start page and exam screens in `frontend/js/ui/student-view.js`: start page shows the summary and a Confirm button and no questions; after Confirm the exam screen shows remaining time as `h:mm:ss`, each question's text with an answer `<input data-question-id>`, saves on every `input` event and shows "Saved"; on render, inputs are filled from saved answers
- [X] T018 [US1] FR-003, FR-022: Wire `student-view.js` into `frontend/js/main.js` so that a reload with a started session reopens the exam screen with restored answers and the remaining time computed from the saved `startedAt`

**Checkpoint**: US1 works on its own and its tests pass

---

## Phase 4: User Story 2 - Record exam signals (Priority: P1)

**Goal**: Per-student question versions, fullscreen request, page-leave, fullscreen-exit, paste and fast-answer signals, reload signal, Finish exam, and same incorrect answer groups

**Independent Test**: Run the exam as a student, switch tabs, exit fullscreen, paste, press Submit within 30 seconds of returning, reload, and Finish; the instructor's exam record lists the versions and each signal

### Tests for User Story 2

- [X] T019 [P] [US2] FR-004: Add to `frontend/tests/versions.test.js`: `versionFor` returns the same params for the same student and question every time; REQ-03 scenario: `s1` and `s2` get different params for each question and `openQuestion` records each student's version; opening again does not change the recorded version; `correctAnswer` matches the question's `answer(params)`
- [X] T020 [P] [US2] FR-006, FR-007, FR-008, FR-022: Write `frontend/tests/signals.test.js`: REQ-06 scenario: `startLeave` then `endLeave` records one `page_leave` signal with `at` and `until`, and a second `startLeave` during the same leave adds nothing; `recordSignal(..., "fullscreen_exit", ...)` records one signal; REQ-07 scenario: `recordSignal(..., "paste", { questionId: "q1" }, ...)` records one signal; REQ-08 scenario: `submitAnswer` at `lastReturnAt + 30000` records `fast_answer` with `secondsSinceReturn: 30`, at `lastReturnAt + 30001` records none, and with no return records none; `recordReload` adds a `page_leave` with `cause: "reload"` only when the session is started and not ended; edge case: after `startLeave` (the hidden and blur events a reload fires) followed by `recordReload`, there is exactly one `page_leave` signal, it has `cause: "reload"`, its `at` is the leave's `from`, the session has no open leave, and `lastReturnAt === now`
- [X] T021 [P] [US2] FR-009: Write `frontend/tests/grouping.test.js`: REQ-09 scenario: three students with the same incorrect value on one question form one group of 3; two students form no group; a student whose value is correct for their own version is not in the group; `applyGroups` stores the group with ID `questionId:value` and adds one `same_incorrect_answer` signal with that `groupId` for every student in the group, including the pre-filled students `s3` and `s4`; `processExamEnd` sets `endedAt` on a started session whose end time has passed with no student action, and forms the group from it; running `processExamEnd` twice, or after `finishExam` and again after a reload, leaves exactly one group signal per student; when a second live student ends with the same value, the group grows to 4 and only that student gets a new signal
- [X] T022 [P] [US2] FR-005, FR-006, FR-007: Write `frontend/tests/exam-events.test.js` with the fakes from `helpers.js`: REQ-05 scenario: `requestFullscreen(examEl)` calls `examEl.requestFullscreen()` once and a rejection does not throw; `visibilitychange` to hidden and `blur` together emit one `leave`, and `visibilitychange` to visible emits one `return`; `fullscreenchange` with `fullscreenElement` null emits `fullscreen_exit`; a `paste` event whose target has `dataset.questionId = "q2"` emits `paste` with `questionId: "q2"`; the detach function removes all listeners
- [X] T023 [P] [US2] FR-009: Add to `frontend/tests/timer.test.js`: `isEnded` is false before the end time, true at the end time, and true right after `finishExam(session, now)` sets `endedAt`

### Implementation for User Story 2

- [X] T024 [US2] FR-004, FR-009: Implement `versionFor(studentId, question)` (deterministic string hash of `studentId + question.id` indexing into each param's allowed values), `openQuestion(session, question, now)` (records `{ params, assignedAt }` once, never changed) and `correctAnswer(question, params)` in `frontend/js/rules/versions.js`; make T019 pass
- [X] T025 [US2] FR-006, FR-007, FR-008, FR-022: Implement `recordSignal(state, studentId, type, details, now)` with `type` one of `page_leave`, `fullscreen_exit`, `paste`, `fast_answer`, `same_incorrect_answer`, plus `startLeave`, `endLeave` (sets `lastReturnAt`), `submitAnswer` (sets `submittedAt`; fast answer when `now - lastReturnAt <= 30000`) and `recordReload` in `frontend/js/rules/signals.js`; make T020 pass
- [X] T026 [P] [US2] FR-009: Implement `isEnded(session, now)` and `finishExam(session, now)` in `frontend/js/rules/timer.js`; make T023 pass
- [X] T027 [US2] FR-009: Implement `findGroups(exam, answersByStudent)` (compare each answer as a number against that student's own version, group equal incorrect values, keep groups of 3 or more), `applyGroups(state, groups, now)` (group ID `questionId:value`; one signal per student per group, skipped if one exists) and `processExamEnd(state, exam, students, now)` (sets `endedAt` on started sessions past their end time, then groups ended live sessions with pre-filled students) in `frontend/js/rules/grouping.js` per research.md R10; make T021 pass (uses `isEnded` from T026)
- [X] T028 [P] [US2] FR-005, FR-006, FR-007: Implement `requestFullscreen(examEl)` and `attachExamEvents({ doc, win, onEvent })` in `frontend/js/ui/exam-events.js` per research.md R5; make T022 pass
- [X] T029 [US2] FR-004 to FR-009, FR-022: Update `frontend/js/ui/student-view.js`: on Confirm call `requestFullscreen`; show each question with the student's version via `openQuestion`; add a Submit button per question calling `submitAnswer`; attach exam events to `startLeave`/`endLeave`/`recordSignal`; call `recordReload` on load of a running exam; add a Finish exam button that calls `finishExam`; show "Exam ended" once the session has `endedAt`. In `frontend/js/main.js`, call `processExamEnd(state, exam, students, now())` on load and on every 1-second tick in every role, saving only when the state changed
- [X] T030 [US2] FR-004, FR-006 to FR-009: Implement the exam record screen in `frontend/js/ui/instructor-view.js`: a student picker, then the versions each student received and their signals with type and time

**Checkpoint**: US1 and US2 work; all tests pass

---

## Phase 5: User Story 4 - Instructor reviews flags with context (Priority: P1)

**Goal**: Every signal becomes a flag with what, when, why and context; instructor keeps or dismisses; students see nothing yet; dropped connections shown as the technical event

**Independent Test**: With seeded and live signals, open each flag as the instructor, check details and context, confirm the student sees none, dismiss one and check Refer is disabled

### Tests for User Story 4

- [X] T031 [P] [US4] FR-012, FR-013, FR-014: Write `frontend/tests/flags.test.js`: every signal recorded with `recordSignal` creates exactly one flag in state `new`; REQ-12 scenario: `flagView` returns `what`, `when`, `why` and `context` with `extraTimePct` and pauses (build the test session with its `pauses` array set directly, since `openPause` and `closePause` come in US3), in the same shape for all 5 signal types; group flags list the other students and the shared value; REQ-13 scenario: `studentFlags` returns nothing for flags in `new` or `kept`; `keep` works only from `new`; REQ-14 scenario: `dismiss` works from `new`, `kept`, `explanation_requested` and `explained`, and `canRefer` is false for a dismissed flag; any action on a `dismissed` flag returns `{ ok: false }`
- [X] T032 [P] [US4] FR-021: Add to `frontend/tests/signals.test.js`: `recordOffline`/`recordOnline` store `{ from, to }`; `technicalEvent` returns `"connection lost"` for a page leave overlapping an offline period and null otherwise; and add to `frontend/tests/exam-events.test.js`: window `offline` and `online` events emit `offline` and `online`

### Implementation for User Story 4

- [X] T033 [US4] FR-012, FR-013, FR-014: Implement `createFlag(signal, state)` (state `new`), `flagView(flag, state)` with a `why` sentence per signal type (for example "Submitted 12 s after returning to the exam page (limit 30 s)"), `keep`, `dismiss`, `canRefer(flag, now)` (true only for `explained`, or `explanation_requested` with `now > deadline`) and `studentFlags(flags, studentId)` (only flags with `explanationRequestedAt` set; dismissed ones marked) in `frontend/js/rules/flags.js`
- [X] T034 [US4] FR-012: Update `recordSignal` in `frontend/js/rules/signals.js` and `applyGroups` in `frontend/js/rules/grouping.js` to add exactly one flag per new signal via `createFlag`; make T031 pass
- [X] T035 [US4] FR-021: Implement `recordOffline`, `recordOnline` and `technicalEvent` in `frontend/js/rules/signals.js` and include `technicalEvent` in `flagView` context; make the signals part of T032 pass
- [X] T036 [US4] FR-021: Emit `offline`/`online` in `frontend/js/ui/exam-events.js` and record them from `frontend/js/ui/student-view.js`; make the exam-events part of T032 pass
- [X] T037 [US4] FR-012, FR-013, FR-014, FR-021: Implement the flag list (student, type, time, state) and flag detail (what, when, why, context including technical event and group members; Keep and Dismiss buttons; a Refer button disabled unless `canRefer`) in `frontend/js/ui/instructor-view.js`

**Checkpoint**: US1, US2 and US4 work; all tests pass

---

## Phase 6: User Story 3 - Ask for help without losing time (Priority: P2)

**Goal**: Help request pauses the timer and detection; each pause recorded with reason and length

**Independent Test**: With 20 minutes left, open help, switch tabs, close after 2 minutes; 20 minutes remain, no page-leave flag, and the exam record shows the pause

### Tests for User Story 3

- [X] T038 [P] [US3] FR-010, FR-011, FR-020: Add to `frontend/tests/timer.test.js`: REQ-10 scenario: with 20 minutes remaining, `openPause` then `closePause` 2 minutes later leaves 20 minutes remaining; remaining time is frozen while the pause is open; a second `openPause` while one is open returns `{ ok: false }`; REQ-11 scenario: `pauseLog` returns `reason: "help request"` and `lengthMs: 2 * MIN`; edge case: a pause still open at the original end time moves `endTime` later by the pause length and `isEnded` stays false
- [X] T039 [P] [US3] FR-010: Add to `frontend/tests/signals.test.js`: REQ-10 scenario: while a pause is open, `page_leave`, `fullscreen_exit`, `paste` and `fast_answer` are not recorded and no flag is created; a leave that started during the pause does not set `lastReturnAt`; offline periods are still recorded

### Implementation for User Story 3

- [X] T040 [US3] FR-010, FR-011, FR-020: Implement `openPause(session, now)` (`reason: "help request"`, one open pause at a time), `closePause(session, now)` and `pauseLog(session)` in `frontend/js/rules/timer.js`; make T038 pass
- [X] T041 [US3] FR-010: Update `recordSignal`, `startLeave`, `endLeave` and `submitAnswer` in `frontend/js/rules/signals.js` to record nothing while a pause is open; make T039 pass
- [X] T042 [US3] FR-010: Add a Request help button and a help panel ("Help request open, timer paused" with a Close help request button) to `frontend/js/ui/student-view.js`
- [X] T043 [US3] FR-011: Show each pause with reason and length in the exam record in `frontend/js/ui/instructor-view.js`

**Checkpoint**: US1 to US4 work; all tests pass

---

## Phase 7: User Story 5 - Student explains a flag (Priority: P2)

**Goal**: Instructor asks for an explanation with a 3-day deadline; student sees only those flags and submits an explanation

**Independent Test**: Keep two flags, ask on one; the student sees only that one with its deadline, submits an explanation, and the instructor sees it

### Tests for User Story 5

- [X] T044 [P] [US5] FR-014, FR-015, FR-016: Add to `frontend/tests/flags.test.js`: `requestExplanation` works only from `kept` and sets `deadline = explanationRequestedAt + 3 * DAY`; REQ-15 scenario: with two kept flags and a request on one, `studentFlags` returns only that one with its details and deadline; a flag dismissed after a request is returned marked as dismissed; REQ-16 scenario: `submitExplanation` before or at the deadline moves the flag to `explained` and stores the text; after the deadline it returns `{ ok: false }`

### Implementation for User Story 5

- [X] T045 [US5] FR-015, FR-016: Implement `requestExplanation(flag, now)` and `submitExplanation(flag, text, now)` in `frontend/js/rules/flags.js`; make T044 pass
- [X] T046 [US5] FR-015, FR-016: Add an Ask for explanation button (kept flags only) and show the deadline and explanation in the flag detail in `frontend/js/ui/instructor-view.js`
- [X] T047 [US5] FR-014, FR-015, FR-016: Add a My flags screen to `frontend/js/ui/student-view.js` listing `studentFlags` with details, deadline and state (dismissed ones marked), and an explanation text box with Submit shown only before the deadline

**Checkpoint**: US1 to US5 work; all tests pass

---

## Phase 8: User Story 6 - Refer a flag to the integrity office (Priority: P2)

**Goal**: Referral after an explanation or a passed deadline; read-only referral document for the integrity office

**Independent Test**: Refer the explained flag and the seeded flag whose deadline passed; as integrity office both documents open with no inputs, and the second states no explanation was given

### Tests for User Story 6

- [X] T048 [P] [US6] FR-017, FR-018, FR-019, FR-023: Write `frontend/tests/referral.test.js`: REQ-17 scenario: `refer` succeeds for an `explained` flag and for an `explanation_requested` flag after its deadline; it returns `{ ok: false }` for `kept` (never asked), for `explanation_requested` before the deadline, for `dismissed`, for an empty reason, and for an already `referred` flag; REQ-18 scenario: the document contains the flag (what, when, why, context), evidence, explanation and reason; edge case: with no explanation the document's `explanation` is "No explanation was given before the deadline."; REQ-19 scenario: the document and its nested objects are frozen, later flag changes do not change it, and `referralsForOffice` returns it

### Implementation for User Story 6

- [X] T049 [US6] FR-017, FR-018, FR-019, FR-023: Implement `buildReferralDocument(flag, signal, reason, now)` (deep `Object.freeze`), `refer(state, flagId, reason, now)` (uses `canRefer`, requires a non-empty reason, sets `referred` and `referralId`) and `referralsForOffice(state)` in `frontend/js/rules/referral.js`; make T048 pass
- [X] T050 [US6] FR-017, FR-023: Add a reason text box to the Refer action in `frontend/js/ui/instructor-view.js`, enabled only when `canRefer` is true
- [X] T051 [US6] FR-018, FR-019: Implement `frontend/js/ui/office-view.js` (referral list, and a document view rendered as text with no inputs or buttons other than Back) and render it from `frontend/js/main.js` for the Integrity office role

**Checkpoint**: All stories work; all tests pass

---

## Phase 9: Polish & Cross-Cutting Concerns

- [X] T052 FR-001 to FR-023: Run `node --test` in `frontend/` and check that each of FR-001 to FR-023 appears in at least one test name (for example `node --test 2>&1 | grep -o "FR-0[0-9][0-9]" | sort -u`)
- [ ] T053 FR-001 to FR-023: Serve `frontend/` with `python -m http.server 8000` and run the 10 manual scenarios in `specs/001-fair-exam-prototype/quickstart.md`; time scenario 1 from opening the exam to the first question (SC-002, under 1 minute) and scenarios 7 to 9 from a new flag to the integrity office opening its document (SC-005, under 5 minutes), and record both times in `docs/learning-log.md`
- [X] T054 [P] FR-001 to FR-023: Update `docs/traceability.md` with one row per FR: goal ID, REQ ID, user story, FR ID and test file

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; blocks all stories
- **US1 (Phase 3)**: Depends on Foundational
- **US2 (Phase 4)**: Depends on Foundational; its UI tasks (T029) extend the US1 exam screen
- **US4 (Phase 5)**: Depends on US2 (flags are created from signals; seeded flags allow its rules tests to run earlier)
- **US3 (Phase 6)**: Depends on US1 (timer) and US2 (signal suppression)
- **US5 (Phase 7)**: Depends on US4 (kept flags)
- **US6 (Phase 8)**: Depends on US5 (explanations and deadlines)
- **Polish (Phase 9)**: Depends on all stories

### Same-file order

These files are edited by more than one task, so those tasks run in ID order:

- `frontend/js/rules/timer.js`: T014, T026, T040
- `frontend/js/rules/versions.js`: T016, T024
- `frontend/js/rules/signals.js`: T025, T034, T035, T041
- `frontend/js/rules/flags.js`: T033, T045
- `frontend/js/rules/grouping.js`: T027, T034
- `frontend/js/main.js`: T010, T018, T029, T051
- `frontend/js/ui/student-view.js`: T017, T029, T036, T042, T047
- `frontend/js/ui/instructor-view.js`: T030, T037, T043, T046, T050
- Test files: `timer.test.js` (T011, T023, T038), `signals.test.js` (T020, T032, T039), `flags.test.js` (T031, T044), `versions.test.js` (T013, T019), `exam-events.test.js` (T022, T032), `store.test.js` (T008, T013)

### Within Each User Story

- Tests first, and they fail before implementation
- Rules modules before UI modules
- Story checkpoint before the next phase

## Parallel Examples

```bash
# Phase 1
Task: "T003 Create frontend/index.html"
Task: "T004 Create frontend/css/styles.css"
Task: "T005 Create frontend/tests/helpers.js"

# US1 tests, then US1 rules
Task: "T011 timer.test.js"  |  Task: "T012 start-page.test.js"  |  Task: "T013 store/versions tests"
Task: "T014 timer.js"       |  Task: "T015 start-page.js"       |  Task: "T016 versions.js saveAnswer"

# US2 tests
Task: "T019 versions.test.js" | "T020 signals.test.js" | "T021 grouping.test.js" | "T022 exam-events.test.js" | "T023 timer.test.js"

# US2 rules after T024 and T025
Task: "T026 timer.js isEnded"  |  Task: "T028 exam-events.js"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 and Phase 2
2. Phase 3 (US1)
3. Stop and validate: `node --test` passes and quickstart scenarios 1 and 2 work

### Incremental Delivery

1. US1: take the exam with extra time and autosave
2. US2: signals, versions, groups
3. US4: flag review
4. US3: help requests and pauses
5. US5: explanations
6. US6: referral and integrity office view

Run `node --test` at every checkpoint.
