# Requirements Traceability Matrix

Version 1. Code paths are under `frontend/`, tests are in `frontend/tests/` and run with `node --test`
(76 tests, all passing). FR IDs are in `specs/001-fair-exam-prototype/spec.md`.

Interview evidence uses these sources:

- **D-Alan, D-Jordan, D-Okoye**: Dylan's transcripts in `hw2/dylan/transcripts/`, cited by line number.
- **A-Alan, A-Jordan, A-Okoye**: Ashley's transcripts in `hw2/ashley/transcripts/`, cited by timestamp.

## Matrix

| Requirement | Interview Evidence | Goal Model Reference | Code / Implementation | Status |
|---|---|---|---|---|
| REQ-01 (FR-001) Extra time applied automatically | D-Alan L78 (wrong deadline instead of extra time); D-Jordan L9 ("approved extra time ... applied automatically") | G-30 | `js/rules/timer.js`, `js/rules/start-page.js` | Fully satisfied |
| REQ-02 (FR-002) One start page confirmed before the exam | D-Jordan L32, L36 ("one clear page would show my approved time, the exam rules"); A-Jordan 21:24:57 (accommodations and actual end time shown before starting) | G-51 | `js/rules/start-page.js`, `js/ui/student-view.js` | Fully satisfied |
| REQ-03 (FR-004) Own version of each question, recorded | D-Alan L17, L22 ("generate and record each student's problem instance") | G-3 | `js/rules/versions.js`, exam record in `js/ui/instructor-view.js` | Fully satisfied |
| REQ-04 (FR-003, FR-022) Answers autosaved | D-Alan L94 ("preserve what they've completed") | G-39 | `js/rules/versions.js` (`saveAnswer`), `js/rules/store.js` | Fully satisfied |
| REQ-05 (FR-005) Fullscreen requested | Derived from conflict C1 (D-Alan L14 vs L58). Not stated by a stakeholder | G-115 | `js/ui/exam-events.js` | Fully satisfied |
| REQ-06 (FR-006) Page leave or fullscreen exit recorded | D-Alan L14 ("monitor the session, flag unusual patterns"); D-Okoye L29 ("irregular focus-loss event"); A-Okoye 20:55:35 ("browser or application focus changes") | G-7 | `js/rules/signals.js`, `js/ui/exam-events.js` | Fully satisfied |
| REQ-07 (FR-007) Paste recorded | Derived from conflict C2 (D-Alan L10 copying from websites). Not stated by a stakeholder | G-116 | `js/rules/signals.js`, `js/ui/exam-events.js` | Fully satisfied |
| REQ-08 (FR-008) Answer within 30 s of returning recorded | D-Okoye L29 ("an unusual response-time distribution"). The 30 s threshold is our assumption | G-117 | `js/rules/signals.js` (`FAST_ANSWER_MS`) | Partially satisfied (see V1-3) |
| REQ-09 (FR-009) Same incorrect answer grouped | D-Alan L10 ("30 students had the same wrong answer to four decimal places"); A-Alan 03:05:15 ("identical unusual mistakes") | G-10 | `js/rules/grouping.js` | Partially satisfied (see V1-4) |
| REQ-10 (FR-010, FR-020) Help request pauses timer and detection | D-Jordan L18 ("not knowing whether contacting support will cost me time"); A-Jordan 21:24:57, 21:25:21 ("clear confirmation that the exam timer has stopped") | G-53 | `js/rules/timer.js`, `js/rules/signals.js`, `js/ui/student-view.js` | Partially satisfied (see V1-2) |
| REQ-11 (FR-011) Each pause recorded with reason and length | A-Alan 03:16:54 (audit trail with "any pauses or connection failures") | G-118 | `js/rules/timer.js`, exam record in `js/ui/instructor-view.js` | Partially satisfied (see V1-2) |
| REQ-12 (FR-012, FR-021) Flag shows what, when, why and context | D-Alan L40 ("what happened, when it happened, and why it was flagged"); D-Okoye L53; A-Okoye 20:50:17 (observation, timestamp, rule, provenance) | G-20 | `js/rules/flags.js`, `js/rules/signals.js`, `js/ui/instructor-view.js` | Partially satisfied (see V1-1) |
| REQ-13 (FR-013) Instructor reviews before the student sees a flag | A-Alan 03:05:15 ("check whether there's a reasonable explanation before contacting a student") | G-111 | `js/rules/flags.js` | Fully satisfied |
| REQ-14 (FR-014) Dismissed flag cannot be referred | Derived from G-25 (A-Alan 03:17:59 "speak with the students if the concern remains"). Not stated directly | G-112 | `js/rules/flags.js` (`dismiss`) | Fully satisfied |
| REQ-15 (FR-015) Student sees a flag only after being asked | D-Jordan L18, L99 ("I should be able to see what was flagged"); A-Jordan 21:26:22 | G-65 | `js/rules/flags.js`, `js/ui/student-view.js` | Fully satisfied |
| REQ-16 (FR-016) Student explains before the deadline | D-Jordan L18, L99; D-Okoye L11 ("opportunity to review the evidence and submit a response"); A-Okoye 18:03:43 | G-66 | `js/rules/flags.js`, `js/ui/student-view.js` | Fully satisfied |
| REQ-17 (FR-017, FR-023) Refer only after asking for an explanation | D-Alan L36 ("refer the stronger cases"); A-Alan 03:17:59 ("If it looks serious, I refer it") | G-25 | `js/rules/referral.js`, `js/ui/instructor-view.js` | Fully satisfied |
| REQ-18 (FR-018, FR-023) Referral document assembled | A-Okoye 20:50:17 ("a useful report should establish the factual basis"); D-Okoye L37 (intake of the instructor's report) | G-113 | `js/rules/referral.js` | Fully satisfied |
| REQ-19 (FR-019) Integrity office reads the document | A-Okoye 20:58:34 ("clear record of who reviewed each item"); D-Okoye L37 | G-114 | `js/rules/referral.js`, `js/ui/office-view.js` | Fully satisfied |

Timed on the V1 build from the gh-pages branch (Nov 18): SC-002 took about 8 seconds from opening the exam
to the first question, with the end time shown on the start page. SC-005 took about 34 seconds from opening a
new flag to the integrity office opening the referral document. Both pass.

## V1 Evaluation Observations

Found by running V1 in the browser as each role and reading the code against the spec.

| ID | What we found | Type | What needs to change |
|---|---|---|---|
| V1-1 | One student's single action produces several separate flags. Leaving the page and then submitting an answer gives two flags, and a group answer adds a third. The instructor reviews, asks and refers each one separately. REQ-12 says "every recorded signal becomes a flag", so this is what the spec asked for, but it works against reducing review workload (G-11) and Okoye's wish for one case record (D-Okoye L53). | Requirements issue | Spec change: one flag per student per exam that collects all of that student's signals as evidence. |
| V1-2 | The help request has no reason field, and nobody receives it. The pause is always recorded with the same fixed reason, so the instructor can't tell a technical problem from anything else (REQ-11). A student could also leave help open for as long as they like, which is the risk behind conflict C3. Jordan asked for a way to "report a technical problem or interruption" (A-Jordan 21:24:57). | Requirements issue | Spec change: the student picks or types a reason when opening help. Stakeholder clarification needed on a maximum pause length (Alan). |
| V1-3 | A fast answer right after a dropped connection is still flagged. FR-021 marks the page leave as "connection lost", but the "answered soon after returning" signal has no such exception. That flags an outage as suspicious, which G-21 says to avoid (D-Alan L40). | Requirements issue | Spec change: no fast-answer signal when the return follows a connection loss or a help request. |
| V1-4 | Any shared wrong answer forms a group, even a common mistake many honest students could make. Alan's example was a wrong answer "to four decimal places" (D-Alan L10), meaning an unusual mistake. | Requirements issue | Stakeholder clarification (Alan): what makes a shared wrong answer suspicious. Keep for a later version. |
| V1-5 | The agent hid the questions while help is open and added a confirm step to Finish exam. Neither is in the spec. Hiding questions is a reasonable answer to C3, but it was the agent's decision, not ours. | Requirements issue (behavior not specified) | Spec change: state that questions are hidden during a help request. |

No implementation defects were found. Every behavior we checked matches the spec as written. The issues above
come from what the spec did or did not say.

---

# Version 2

Code paths are under `frontend/`, tests are in `frontend/tests/` and run with `node --test`
(104 tests, all passing). FR and user story (US) IDs are in `specs/002-fair-exam-prototype-v2/spec.md`;
goals and requirements are in `docs/goal-model.md` (Version 2).

## V2 Matrix

| Requirement | Interview Evidence | FR | Story | Goal | Code / Implementation | Tests | Status |
|---|---|---|---|---|---|---|---|
| REQ-01 Extra time applied | D-Alan L78 (wrong deadline instead of extra time); D-Jordan L9 ("approved extra time ... applied automatically") | FR-001 | US1 | G-30 | `js/rules/timer.js`, `js/rules/start-page.js` | `timer.test.js` | Fully satisfied (unchanged from V1) |
| REQ-02 One start page | D-Jordan L32, L36 ("one clear page would show my approved time, the exam rules"); A-Jordan 21:24:57 (accommodations and actual end time shown before starting) | FR-002 | US1 | G-51 | `js/rules/start-page.js`, `js/ui/student-view.js` | `start-page.test.js` | Fully satisfied (unchanged from V1) |
| REQ-03 Own version, recorded | D-Alan L17, L22 ("generate and record each student's problem instance") | FR-003 | US2 | G-3 | `js/rules/versions.js` | `versions.test.js` | Fully satisfied (unchanged from V1, renumbered) |
| REQ-04 Answers autosaved | D-Alan L94 ("preserve what they've completed") | FR-004, FR-022 | US1 | G-39 | `js/rules/versions.js`, `js/rules/store.js` (key `fairExam.v2`) | `store.test.js`, `versions.test.js` | Fully satisfied (unchanged from V1, renumbered, new storage key) |
| REQ-05 Fullscreen requested | Derived from conflict C1 (D-Alan L14 vs L58). Not stated by a stakeholder | FR-005 | US3 | G-115 | `js/ui/exam-events.js` | `exam-events.test.js` | Fully satisfied (unchanged from V1) |
| REQ-06 Page leave or fullscreen exit | D-Alan L14 ("monitor the session, flag unusual patterns"); D-Okoye L29 ("irregular focus-loss event"); A-Okoye 20:55:35 ("browser or application focus changes") | FR-006 | US3 | G-7 | `js/rules/signals.js`, `js/ui/exam-events.js` | `signals.test.js`, `exam-events.test.js` | Fully satisfied (unchanged from V1) |
| REQ-07 Paste recorded | Derived from conflict C2 (D-Alan L10 copying from websites). Not stated by a stakeholder | FR-007 | US3 | G-116 | `js/rules/signals.js`, `js/ui/exam-events.js` | `signals.test.js`, `exam-events.test.js` | Fully satisfied (unchanged from V1) |
| REQ-08 Fast answer, not after outage or help | D-Okoye L29 ("an unusual response-time distribution"). The 30 s threshold is our assumption; V1-3 (connection loss is not suspicious, D-Alan L40, G-21) | FR-008, FR-021 | US3 | G-117 | `js/rules/signals.js` (`overlapsOffline`, `endLeave`, `recordReload`), `js/rules/timer.js` (`closePause`) | `signals.test.js` | Fully satisfied (changed for V1-3) |
| REQ-09 Same incorrect answer grouped | D-Alan L10 ("30 students had the same wrong answer to four decimal places"); A-Alan 03:05:15 ("identical unusual mistakes") | FR-009 | US3 | G-10 | `js/rules/grouping.js` (`MIN_GROUP_SIZE` 2) | `grouping.test.js`, `flags.test.js` | Partially satisfied (group size changed to 2 or more; V1-4 still open with Alan) |
| REQ-10 Help request with a reason | D-Jordan L18 ("not knowing whether contacting support will cost me time"); A-Jordan 21:24:57, 21:25:21 ("clear confirmation that the exam timer has stopped"); V1-2 (A-Jordan 21:24:57 "report a technical problem or interruption") | FR-010, FR-020 | US4 | G-53 | `js/rules/timer.js` (`openPause`, `questionsHidden`), `js/data/mock-data.js` (`helpReasons`), `js/ui/student-view.js` | `timer.test.js`, `signals.test.js` | Partially satisfied (reason added and questions hidden for V1-2, V1-5; maximum pause length still open with Alan) |
| REQ-11 Pause with reason and length | A-Alan 03:16:54 (audit trail with "any pauses or connection failures") | FR-011 | US4 | G-118 | `js/rules/timer.js` (`pauseLog`), `js/ui/instructor-view.js` | `timer.test.js` | Fully satisfied (changed for V1-2) |
| REQ-12 One flag per student | D-Alan L40 ("what happened, when it happened, and why it was flagged"); D-Okoye L53; A-Okoye 20:50:17 (observation, timestamp, rule, provenance); V1-1 (one case record, D-Okoye L53) | FR-012 | US5 | G-20 | `js/rules/flags.js`, `js/rules/signals.js` (`addSignal`), `js/ui/instructor-view.js` | `flags.test.js`, `referral.test.js` | Fully satisfied (changed for V1-1) |
| REQ-13 Review before student sees | A-Alan 03:05:15 ("check whether there's a reasonable explanation before contacting a student") | FR-013 | US5 | G-111 | `js/rules/flags.js` | `flags.test.js` | Fully satisfied (unchanged from V1) |
| REQ-14 Dismiss, no referral | Derived from G-25 (A-Alan 03:17:59 "speak with the students if the concern remains"). Not stated directly | FR-014 | US5 | G-112 | `js/rules/flags.js` (`dismiss`) | `flags.test.js` | Fully satisfied (unchanged from V1, dismissed flag visible to student clarified) |
| REQ-15 Student sees flag after request | D-Jordan L18, L99 ("I should be able to see what was flagged"); A-Jordan 21:26:22 | FR-015 | US6 | G-65 | `js/rules/flags.js`, `js/ui/student-view.js` | `flags.test.js` | Fully satisfied (unchanged from V1, all signals shown) |
| REQ-16 Student explains | D-Jordan L18, L99; D-Okoye L11 ("opportunity to review the evidence and submit a response"); A-Okoye 18:03:43 | FR-016 | US6 | G-66 | `js/rules/flags.js`, `js/ui/student-view.js` | `flags.test.js` | Fully satisfied (unchanged from V1) |
| REQ-17 Refer after explanation or deadline | D-Alan L36 ("refer the stronger cases"); A-Alan 03:17:59 ("If it looks serious, I refer it") | FR-017, FR-023 | US7 | G-25 | `js/rules/referral.js`, `js/ui/instructor-view.js` | `referral.test.js` | Fully satisfied (unchanged from V1) |
| REQ-18 Referral document | A-Okoye 20:50:17 ("a useful report should establish the factual basis"); D-Okoye L37 (intake of the instructor's report) | FR-018, FR-023 | US7 | G-113 | `js/rules/referral.js` | `referral.test.js` | Fully satisfied (now lists every signal) |
| REQ-19 Office reads the document | A-Okoye 20:58:34 ("clear record of who reviewed each item"); D-Okoye L37 | FR-019 | US7 | G-114 | `js/rules/referral.js`, `js/ui/office-view.js` | `referral.test.js` | Fully satisfied (unchanged from V1, lists every signal) |

Checked in a browser on the V2 build from the gh-pages branch (Nov 17): as a student, left the page, came back and submitted within 30 seconds, pasted, opened help (refused without a reason, questions hidden once open), left the page during help, closed it and submitted again, then finished. The instructor saw one flag for that student with four signals (page leave, fast answer, paste, same incorrect answer) and no fast-answer or page-leave signal from the help period; the exam record showed the pause with its reason and length. Keep, ask, explain and refer worked in order (Refer stayed disabled until the student explained), and the integrity office document listed every signal, the explanation and the reason. The same steps in V1 gave three separate flags. We also went offline, left the page, came back online and submitted within 30 seconds: V2 marked the page leave "connection lost" and recorded no fast answer, where V1 recorded one. Timed (Nov 18): SC-002 took about 8 seconds and SC-006 took about 34 seconds from opening a new flag to the integrity office opening the document. Both pass.
