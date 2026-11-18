# Quickstart: Fair Exam Prototype V2

## Prerequisites

- Node.js 20 or later (for tests)
- Any static file server (for the app), for example Python 3

## Run the tests

```bash
cd frontend
node --test
```

Expected: all tests pass. Each test name starts with the V2 FR IDs it covers, for example
`FR-001 REQ-01: 50% extra time on 60 minutes ends 90 minutes after start`.

## Run the app

```bash
cd frontend
python -m http.server 8000
```

Open `http://localhost:8000`. State is saved under the key `fairExam.v2`; to start over, clear the
site's storage in the browser's developer tools.

## Deploy next to V1

Done only after all tests pass and the user confirms (it pushes to the shared remote).

1. Tag the commit `v2`.
2. Check out `gh-pages`, copy the contents of `frontend/` at the `v2` tag into `v2/`, and commit.
   Do not edit `v1/`.
3. Push `gh-pages`, wait for Pages to update, then open `/v1/` and `/v2/` in the same browser.
4. Check: both load; a student action in V2 does not appear in V1 and the reverse (separate storage);
   V1 still shows one flag per signal and V2 shows one flag per student.
5. Put `https://dylan40907.github.io/hw3-sdd/v2/` in the README "Prototype V2" row.

## FR to test file map

| FR | Test file |
|---|---|
| FR-001, FR-010, FR-011, FR-020, FR-022 (timer, pause reason) | `tests/timer.test.js` |
| FR-002 (start page) | `tests/start-page.test.js` |
| FR-004, FR-022 (restore), storage key | `tests/store.test.js` |
| FR-003, FR-004 | `tests/versions.test.js` |
| FR-006, FR-007, FR-008, FR-010, FR-021, FR-022 (signal, connection loss, help return) | `tests/signals.test.js` |
| FR-009 (group of 2 or more) | `tests/grouping.test.js` |
| FR-008, FR-009, FR-012 to FR-016 (one flag, signals list, New signals mark, dismissed flag visible to student) | `tests/flags.test.js` |
| FR-017, FR-018, FR-019, FR-023 | `tests/referral.test.js` |
| FR-005, FR-006, FR-007, FR-021 (event wiring) | `tests/exam-events.test.js` |

## Manual validation scenarios

Each scenario matches an acceptance scenario in [spec.md](spec.md). Scenarios marked **new** differ
from V1; run them in `/v1/` and `/v2/` to compare.

1. **Start page and extra time (REQ-01, REQ-02, REQ-05)**: As in V1.
2. **Autosave and reload (REQ-04, edge case)**: As in V1; the reload adds a page-leave signal.
3. **Versions (REQ-03)**: As in V1.
4. **One flag per student (REQ-06 to REQ-08, REQ-12) (new)**: Switch tabs, come back, press Submit
   within 30 seconds, then paste. The instructor sees one flag for the student with three signals,
   each with what, when and why, plus extra time and pauses. V1 shows three flags.
5. **Help request (REQ-10, REQ-11) (new)**: Try to open a help request with no reason: it is
   refused. Open one with a reason, confirm the questions are hidden, switch tabs, come back, close
   it. Remaining time is unchanged, no page-leave signal appears, and the exam record shows the
   pause with the student's reason and length.
6. **No fast answer after help or outage (REQ-08) (new)**: Close a help request and press Submit
   within 30 seconds: no signal. In developer tools go offline, switch tabs, come back online and
   press Submit within 30 seconds: the page leave shows "connection lost" and there is no
   fast-answer signal.
7. **Groups (REQ-09) (new)**: Finish the exam as Student A with the shared incorrect answer on
   question 2 (see `js/data/mock-data.js`), and the instructor sees the group in the flags of all
   three students. Finish with a different answer: the two pre-filled students still form a group of
   2, which V1 did not.
8. **Review and explanation (REQ-13 to REQ-16)**: As in V1.
9. **Dismiss (REQ-14)**: As in V1. Dismiss a flag after asking for an explanation: the student still
   sees it, with its signals, marked as dismissed.
10. **Referral (REQ-17 to REQ-19, edge case)**: As in V1; the document now lists every signal.
11. **New signals mark (REQ-12) (new)**: Keep the flag of a student, then give that student another
    signal (for example finish the exam with a shared incorrect answer so the group signal is added).
    In the instructor's flag list the row shows "New signals"; the flag's state, explanation and
    deadline are unchanged. Open the flag: the mark disappears. A flag still `new` never shows the
    mark. A referral document created earlier does not change.
12. **Exam end (REQ-09)**: Press "Finish exam" and see groups form at once. Start another exam, leave
    the page open on another tab past the end time, and check the groups form without returning.
13. **Fast answer needs Submit (REQ-08)**: Come back to the page and type an answer within 30
    seconds without pressing Submit: no signal. Press Submit within 30 seconds: one signal.
