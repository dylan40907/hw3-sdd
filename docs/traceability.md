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
| REQ-09 (FR-009) Same incorrect answer grouped | D-Alan L10 ("30 students had the same wrong answer to four decimal places"); A-Alan 03:05:15 ("identical unusual mistakes") | G-10 | `js/rules/grouping.js` | Fully satisfied as specified (see V1-4) |
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

Not checked in V1: success criteria SC-002 (under 1 minute to the first question) and SC-005 (under 5 minutes
from a new flag to referral) need a person to time a real run.

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
