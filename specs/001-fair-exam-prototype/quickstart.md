# Quickstart: Fair Exam Prototype V1

## Prerequisites

- Node.js 20 or later (for tests)
- Any static file server (for the app), for example Python 3

## Run the tests

```bash
cd frontend
node --test
```

Expected: all tests pass. Each test name starts with the FR IDs it covers, for example
`FR-001 REQ-01: 50% extra time on 60 minutes ends 90 minutes after start`.

## Run the app

```bash
cd frontend
python -m http.server 8000
```

Open `http://localhost:8000`. To start over, clear the site's storage in the browser's developer
tools.

## Deploy

Publish the contents of `frontend/` as a static site (for example GitHub Pages). No build step.

## FR to test file map

| FR | Test file |
|---|---|
| FR-001, FR-010, FR-011, FR-020, FR-022 (timer) | `tests/timer.test.js` |
| FR-002 (start page) | `tests/start-page.test.js` |
| FR-003, FR-022 (restore) | `tests/store.test.js` |
| FR-003, FR-004 | `tests/versions.test.js` |
| FR-006, FR-007, FR-008, FR-010, FR-021, FR-022 (signal) | `tests/signals.test.js` |
| FR-009 | `tests/grouping.test.js` |
| FR-008, FR-009, FR-012 to FR-016 | `tests/flags.test.js` |
| FR-017, FR-018, FR-019, FR-023 | `tests/referral.test.js` |
| FR-005, FR-006, FR-007, FR-021 (event wiring) | `tests/exam-events.test.js` |

## Manual validation scenarios

Each scenario matches an acceptance scenario in [spec.md](spec.md).

1. **Start page and extra time (REQ-01, REQ-02, REQ-05)**: Role Student, pick Student A (50%). The
   start page shows an end time 90 minutes after now and lists the detected behaviors. The exam
   does not open until you confirm. On confirm, the browser asks for fullscreen.
2. **Autosave and reload (REQ-04, edge case)**: Type an answer, reload. The answer is still there,
   the timer has kept counting, and the instructor sees a page-leave flag marked as a reload.
3. **Versions (REQ-03)**: Open the same question as Student A and Student B. The numbers differ.
   The instructor's exam record shows which version each received.
4. **Signals (REQ-06 to REQ-08)**: Switch tabs and come back, then press Submit within 30 seconds.
   Exit fullscreen. Paste into an answer field. The instructor sees one flag for each.
5. **Help request (REQ-10, REQ-11)**: Open a help request, switch tabs, wait, come back, close it.
   Remaining time is unchanged, no page-leave flag appears, and the exam record shows the pause
   with reason "help request" and its length.
6. **Groups (REQ-09)**: As Student A, enter the shared incorrect answer on question 2 (see
   `js/data/mock-data.js`), then Finish exam. The instructor sees one group flag each for Student A
   and the two pre-filled students, each listing the other two. Reloading or switching roles adds
   no more group flags.
7. **Review and explanation (REQ-12 to REQ-16)**: As instructor, keep two flags and ask for an
   explanation on one. As the student, only that flag is visible with its deadline. Submit an
   explanation; the instructor sees it.
8. **Dismiss (REQ-14)**: Dismiss a flag. Refer is disabled.
9. **Referral (REQ-17 to REQ-19, edge case)**: Refer the explained flag with a reason, and refer the
   seeded flag whose deadline has passed. As integrity office, both documents open with no inputs;
   the second states that no explanation was given.
10. **Connection drop (edge case)**: In developer tools set the network to offline, switch tabs,
    come back, go online. The page-leave flag shows "connection lost".
