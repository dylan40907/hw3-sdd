# Feature Specification: Fair Exam Prototype V1

**Feature Branch**: `main` (no feature branch)

**Created**: 2026-11-16

**Status**: Draft

**Input**: User description: "pls create the spec from docs/initial-spec.md. keep every requirement
REQ-01 to REQ-19 with its goal ID, its acceptance scenario, the edge cases and the conflict
decisions. Do not add features. Mark anything unclear as NEEDS CLARIFICATION."

Source: [docs/initial-spec.md](../../docs/initial-spec.md), goals from
[docs/goal-model.md](../../docs/goal-model.md).

Users: student, instructor, integrity office.

## Clarifications

### Session 2026-11-16

- Q: What counts as submitting an answer (REQ-08)? → A: Pressing the Submit button on a question
  (FR-008).
- Q: How many students with the same incorrect answer form a group (REQ-09)? → A: 3 or more
  (FR-009).
- Q: Does the student still see a flag dismissed after an explanation request (REQ-14)? → A: Yes,
  marked as dismissed (FR-014).
- Q: When 3 or more students give the same incorrect answer, is that one shared flag or one flag
  per student? → A: One flag per student, linked to the group (FR-009).
- Q: Can a student end the exam before their end time? → A: Yes, with "Finish exam"; the exam
  also ends automatically at the end time (FR-009).
- Q: How does the prototype know a page leave was caused by a dropped connection? → A: Offline
  and online times are recorded; a page leave that overlaps an offline period shows "connection
  lost" (FR-021).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Take the exam with accommodations applied (Priority: P1)

**Goals**: G-30, G-51, G-39 | **Requirements**: REQ-01, REQ-02, REQ-04

A student opens the exam, sees one start page with the rules, their end time, their accommodations
and what is detected, and confirms it. Their extra time is already applied. While they answer, their
work is saved so a reload or a dropped connection does not lose it.

**Why this priority**: This is what the student sees during the exam. Missed accommodations and lost
time were the main sources of student stress.

**Independent Test**: Select a mock student with 50% extra time, open the exam, check the start page
and end time, confirm, type an answer and reload the page.

**Acceptance Scenarios**:

1. **REQ-01**: **Given** a student has 50% extra time on a 60-minute exam, **When** the student opens
   the exam, **Then** the end time is 90 minutes after the start.
2. **REQ-02**: **Given** the start page is shown, **When** the student has not confirmed it,
   **Then** the exam does not start.
3. **REQ-04**: **Given** a student has typed an answer, **When** the page reloads, **Then** the
   answer is still there.

---

### User Story 2 - Record exam signals (Priority: P1)

**Goals**: G-3, G-115, G-7, G-116, G-117, G-10 | **Requirements**: REQ-03, REQ-05, REQ-06, REQ-07,
REQ-08, REQ-09

Each student gets their own numeric version of each question. The exam asks for fullscreen. Leaving
the exam page, exiting fullscreen, pasting into an answer field, and answering soon after returning
to the page are each recorded as a signal. When the exam ends, students who gave the same incorrect
answer to the same question are grouped.

**Why this priority**: Without a camera (C2), it is uncertain whether these signals give the
instructor useful flags. The prototype is the cheapest way to find out.

**Independent Test**: Run the exam as a mock student, switch tabs, exit fullscreen, paste into an
answer field, answer within 30 seconds of returning, and end the exam; check the recorded signals,
versions and groups.

**Acceptance Scenarios**:

1. **REQ-03**: **Given** two students take the same exam, **When** both open the same question,
   **Then** the system records which version each student received.
2. **REQ-05**: **Given** the student confirms the start page, **When** the exam starts, **Then**
   fullscreen is requested.
3. **REQ-06**: **Given** the exam is running, **When** the student switches to another tab, **Then**
   a signal is recorded.
4. **REQ-07**: **Given** the exam is running, **When** the student pastes into an answer field,
   **Then** a signal is recorded.
5. **REQ-08**: **Given** the student has just returned to the exam page, **When** the student submits
   an answer within 30 seconds, **Then** a signal is recorded.
6. **REQ-09**: **Given** three students give the same incorrect answer to one question, **When** the
   exam ends, **Then** they are grouped in one flag.

---

### User Story 3 - Ask for help without losing time (Priority: P2)

**Goals**: G-53, G-118 | **Requirements**: REQ-10, REQ-11

The student opens a help request from the exam page. The timer pauses and nothing is detected until
the request is closed. The request and the pause are recorded so the instructor can see them.

**Why this priority**: Decided in C3 (G-53 over G-2). It depends on the exam timer from User Story 1
and the detection from User Story 2.

**Independent Test**: With 20 minutes left, open a help request, switch tabs, close the request after
2 minutes, then check the remaining time, the recorded pause and the absence of a page-leave signal.

**Acceptance Scenarios**:

1. **REQ-10**: **Given** 20 minutes remain, **When** the student opens a 2-minute help request,
   switches tabs during it, then closes it, **Then** 20 minutes still remain, the help request is
   recorded, and no page-leave signal is recorded.
2. **REQ-11**: **Given** a help request was closed, **When** the instructor opens the student's exam
   record, **Then** the pause is shown with its reason and length.

---

### User Story 4 - Instructor reviews flags with context (Priority: P1)

**Goals**: G-20, G-111, G-112 | **Requirements**: REQ-12, REQ-13, REQ-14

Every signal becomes a flag that shows what happened, when, why, and the student's accommodations and
pauses. The instructor reviews each flag before the student can see it and can dismiss it. A
dismissed flag cannot be referred.

**Why this priority**: Handling a flag from signal to referral is the main concern of all three
stakeholders, and it is where conflict C4 sits.

**Independent Test**: Load mock signals, open each flag as the instructor, check its details and
context, confirm the student cannot see it, dismiss one and try to refer it.

**Acceptance Scenarios**:

1. **REQ-12**: **Given** a signal was recorded, **When** the instructor opens the flag, **Then** it
   shows what happened, when, why, and the context.
2. **REQ-13**: **Given** a new flag exists, **When** the instructor has not reviewed it, **Then** the
   student cannot see it.
3. **REQ-14**: **Given** the instructor dismisses a flag, **When** the instructor tries to refer it,
   **Then** referral is not possible.

---

### User Story 5 - Student explains a flag (Priority: P2)

**Goals**: G-65, G-66 | **Requirements**: REQ-15, REQ-16

The instructor asks the student to explain a flag. Only then does the student see it, with its
details and a deadline. The student submits an explanation before the deadline and the instructor
sees it.

**Why this priority**: Decided in C4 (G-111 over G-64). It depends on reviewed flags from User
Story 4.

**Independent Test**: As the instructor, keep two flags and ask for an explanation on one; as the
student, check that only that flag is shown and submit an explanation; as the instructor, read it.

**Acceptance Scenarios**:

1. **REQ-15**: **Given** the instructor kept two flags and asked for an explanation on one, **When**
   the student checks their flags, **Then** only that one is shown, with its details and deadline.
2. **REQ-16**: **Given** the student was asked to explain a flag, **When** the student submits an
   explanation before the deadline, **Then** the instructor sees the explanation.

---

### User Story 6 - Refer a flag to the integrity office (Priority: P2)

**Goals**: G-25, G-113, G-114 | **Requirements**: REQ-17, REQ-18, REQ-19

After the student explains or the deadline passes, the instructor refers the flag with a reason. The
referral creates a document with the flag, its evidence, the student's explanation and the
instructor's reason. The integrity office can read the document but not edit it.

**Why this priority**: The referral document is the handoff to the integrity office and ends the
sprint scope. It depends on User Story 5.

**Independent Test**: Refer a flag that has an explanation and one whose deadline has passed; check
both documents as the integrity office.

**Acceptance Scenarios**:

1. **REQ-17**: **Given** the student was asked to explain, and has explained or the deadline has
   passed, **When** the instructor refers the flag, **Then** the flag is referred to the integrity
   office.
2. **REQ-18**: **Given** a flag is referred, **When** the document is generated, **Then** it contains
   the flag, its evidence, the explanation and the reason.
3. **REQ-19**: **Given** a referral document exists, **When** the integrity office opens it, **Then**
   the document can be read but not edited.

---

### Edge Cases

| Case | Expected behavior | Requirement | FR |
|---|---|---|---|
| A help request is still open when the end time arrives | The end time moves later by the length of the pause. | REQ-10 | FR-020 |
| A connection drop makes the student leave the exam page | The flag shows the technical event. | REQ-12 | FR-021 |
| The student reloads the page during the exam | The answers are restored, the timer keeps running, and a page-leave signal is recorded. | REQ-04, REQ-06 | FR-022 |
| The deadline passes without an explanation | The instructor can still refer the flag, and the document states that no explanation was given. | REQ-17, REQ-18 | FR-023 |

## Requirements *(mandatory)*

### Functional Requirements

Each FR cites its user story (US) and its requirement from `docs/initial-spec.md`.

**Taking the exam**

- **FR-001** (US1, REQ-01): System MUST set each student's end time to the start time plus the exam
  length plus the student's approved extra time (a 60-minute exam with 50% extra time ends 90
  minutes after the start).
- **FR-002** (US1, REQ-02): System MUST show one start page with the exam rules, the student's end
  time, the student's accommodations and the behaviors that are detected (leaving the page, exiting
  fullscreen, pasting, answering within 30 seconds of returning), and MUST NOT start the exam until
  the student confirms it.
- **FR-003** (US1, REQ-04): System MUST save each answer while the student types and MUST restore
  saved answers after a page reload or a dropped connection.

**Detection during the exam**

- **FR-004** (US2, REQ-03): System MUST give each student their own numeric version of each question
  and MUST record which version each student received.
- **FR-005** (US2, REQ-05): System MUST request fullscreen when the exam starts after the student
  confirms the start page. Fullscreen is requested only; the computer is not otherwise locked (C1).
- **FR-006** (US2, REQ-06): While the exam is running, System MUST record a signal when the student
  leaves the exam page or exits fullscreen.
- **FR-007** (US2, REQ-07): While the exam is running, System MUST record a signal when the student
  pastes into an answer field.
- **FR-008** (US2, REQ-08): System MUST record a signal when the student submits an answer within 30
  seconds of returning to the exam page. Submitting an answer means pressing the Submit button on
  that question; continuous saving (FR-003) does not count as submitting.
- **FR-009** (US2, REQ-09): The exam ends when the student chooses "Finish exam" or when the end
  time is reached, whichever comes first, including when the student is not on the exam page at
  that time. When the exam ends, System MUST group students who gave the same incorrect answer to
  the same question into one group. A group needs 3 or more students; 2 students with the same
  incorrect answer are not grouped. Each student in the group gets exactly one flag for that group,
  which shows the shared answer and the other students in the group, and is reviewed, explained and
  referred on its own.
  - Note: the REQ-09 acceptance scenario says the students "are grouped in one flag". Per the
    clarification, this means one group, with one flag for each student in it.

**Help requests and pauses**

- **FR-010** (US3, REQ-10): System MUST let the student open and close a help request from the exam
  page. While a help request is open, the timer MUST pause and no signals (FR-006 to FR-008) MUST be
  recorded. The help request itself MUST be recorded.
- **FR-011** (US3, REQ-11): System MUST record each pause with its reason and length and MUST show it
  in the student's exam record to the instructor.

**Flag review**

- **FR-012** (US4, REQ-12): System MUST turn every recorded signal into a flag that shows what
  happened, when, why it was raised, and the student's accommodations and pauses as context. All
  signal types are recorded separately and shown the same way (O4).
- **FR-013** (US4, REQ-13): System MUST NOT show a flag to the student until the instructor has
  reviewed it.
- **FR-014** (US4, REQ-14): System MUST let the instructor dismiss a flag before or after the student
  explains, and MUST NOT allow a dismissed flag to be referred. If the flag is dismissed after the
  student was asked to explain, the student MUST still see it, marked as dismissed.
- **FR-015** (US5, REQ-15): System MUST let the instructor ask the student to explain a reviewed
  flag, with a deadline 3 days after the request. The student MUST see a flag only after this
  request, with its details and deadline.
- **FR-016** (US5, REQ-16): System MUST let the student submit an explanation before the deadline and
  MUST show the explanation to the instructor.

**Referral**

- **FR-017** (US6, REQ-17): System MUST let the instructor refer a flag to the integrity office only
  after an explanation was requested and the student has explained or the deadline has passed. A
  flag that was never sent for explanation MUST NOT be referable.
- **FR-018** (US6, REQ-18): A referral MUST create a document with the flag, its evidence, the
  student's explanation and the instructor's reason.
- **FR-019** (US6, REQ-19): System MUST let the integrity office open and read referral documents and
  MUST NOT let it edit them.

**Edge cases**

- **FR-020** (US3, REQ-10): If a help request is still open when the end time arrives, System MUST
  move the end time later by the length of the pause.
- **FR-021** (US4, REQ-12): System MUST record when the student's device goes offline and comes back
  online during the exam. When a page-leave signal overlaps an offline period, its flag MUST show
  "connection lost" as the technical event.
- **FR-022** (US1, REQ-04; US2, REQ-06): When the student reloads the page during the exam, System
  MUST restore the answers, keep the timer running, and record exactly one page-leave signal for
  the reload.
- **FR-023** (US6, REQ-17, REQ-18): When the deadline passes without an explanation, System MUST
  still let the instructor refer the flag, and the referral document MUST state that no explanation
  was given.

### Decisions on Overlapping and Conflicting Requirements

**Overlaps**

| ID | Overlap | Decision |
|---|---|---|
| O1 | Confirming accommodations, a one-page summary, and showing the rules before the start | Combined into one start page (REQ-02, FR-002). |
| O2 | Separating accommodations and technical problems from unusual behavior (Alan), and not counting normal behavior against the student (Jordan) | Combined: shown as context on each flag (REQ-12, FR-012). |
| O3 | Instructor screening (Alan) and human review (Nkechi, Jordan) | Combined into one review step (REQ-13, FR-013). |
| O4 | Four signal types | Recorded separately, shown the same way (REQ-12, FR-012). |

**Conflicts**

| ID | Conflict | Decision |
|---|---|---|
| C1 | Block outside resources (G-5) ↔ Don't over-restrict the exam (G-9) | **Compromise**: fullscreen only, without blocking the computer (REQ-05, FR-005). |
| C2 | Monitor the exam (G-6) ↔ Reduce student stress (G-43) | **Compromise**: no camera; detect page leaves, pastes and timing, and tell students beforehand (REQ-02, REQ-06 to REQ-08; FR-002, FR-006 to FR-008). |
| C3 | Pause the timer for help (G-53) ↔ Prevent outside help (G-2) | **Prioritize G-53**: the student keeps their time, and every pause is recorded for review (REQ-10, REQ-11; FR-010, FR-011). |
| C4 | Student explains first (G-64) ↔ Instructor reviews first (G-111) | **Prioritize G-111**: the student sees a flag only when the instructor asks for an explanation, and must be asked before any referral (REQ-13 to REQ-17; FR-013 to FR-017). |

### Dependencies

| ID | Dependency |
|---|---|
| D1 | REQ-12 depends on REQ-01 and REQ-11: each flag shows the student's extra time and pauses as context. |
| D2 | REQ-09 depends on REQ-03: because each student has a different version, the same incorrect answer from several students stands out. |
| D3 | REQ-16 depends on REQ-15, and REQ-17 on REQ-16: the student explains only after being asked, and a flag is referred only after the explanation or the deadline. |
| D4 | REQ-06 to REQ-08 depend on REQ-10: detection stops during a help request. |

### Key Entities

- **Exam**: the one mock exam; has a length, rules and questions.
- **Student**: a mock student; has approved extra time (or none).
- **Question version**: the numeric version of a question given to one student; records which
  student received it.
- **Answer**: a student's saved answer to a question version.
- **Signal**: a recorded event (page leave, fullscreen exit, paste, fast answer after return,
  same incorrect answer) with its time and student.
- **Offline period**: when the student's device went offline and came back online during the
  exam; used as the technical event on an overlapping page-leave flag.
- **Pause**: a help request with its reason, start and length.
- **Flag**: created from a signal for one student; shows what, when, why and context; has a review
  state (new, kept, dismissed, explanation requested, explained, referred).
- **Answer group**: 3 or more students with the same incorrect answer to one question; each
  student's flag links to the group.
- **Explanation request**: a request on a flag with a deadline 3 days later and the student's
  explanation, if submitted.
- **Referral document**: created on referral; holds the flag, evidence, explanation (or a statement
  that none was given) and the instructor's reason; read-only for the integrity office.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 19 acceptance scenarios (REQ-01 to REQ-19) and all 4 edge cases pass as automated
  tests.
- **SC-002**: A student can go from opening the exam to the first question in under 1 minute, with
  their correct end time shown before they confirm.
- **SC-003**: In 100% of reload tests during an exam, no typed answer is lost.
- **SC-004**: 0 flags are visible to a student before the instructor asks for an explanation.
- **SC-005**: An instructor can take a flag from new to referred, and the integrity office can open
  the resulting document, in under 5 minutes using only the prototype.

## Assumptions

- The prototype uses mock data: one exam and a small list of students.
- Users switch roles with a selector; there is no login.
- The student has 3 days to explain after the instructor asks.
- The response-time threshold is 30 seconds.
- Help requests are the only kind of pause, so a pause's reason is "help request".
- Other students' answers for grouping (REQ-09) come from mock data.
- Mock data includes an explanation request whose deadline has already passed, so REQ-17 and the
  deadline edge case can be shown without waiting 3 days.
- A referred flag cannot be dismissed or referred again.

### Out of scope

- Login and real user accounts
- Webcam, audio, room scans and face identity checks
- The integrity office process after a referral (screening, decision, appeal)
- Recording storage and retention
- Grading
- Accommodations other than extra time
- Resuming on another device or retakes after a crash
