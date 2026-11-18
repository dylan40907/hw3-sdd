# Feature Specification: Fair Exam Prototype V2

**Feature Branch**: `main` (no feature branch)

**Created**: 2026-11-17

**Status**: Draft

**Input**: User description: "A fair online exam prototype. Use docs/goal-model.md sections 1 to 4 as the source of truth: REQ-01 to REQ-19, the acceptance scenarios, assumptions, dependencies, edge cases and decisions exactly as written there."

Source: [docs/goal-model.md](../../docs/goal-model.md) (Version 2), sections 1 to 4. Where this spec and
the goal model differ, the goal model wins. This spec replaces the V1 spec in
[../001-fair-exam-prototype/spec.md](../001-fair-exam-prototype/spec.md); V1 clarifications that the
goal model does not state are not carried over.

Users: student, instructor, integrity office.

## Clarifications

### Session 2026-11-17

- Q: What counts as submitting an answer for the 30-second fast-answer signal (REQ-08)? → A: Pressing
  a Submit button on that question; autosave never counts as submitting (FR-008).
- Q: When a signal arrives for a flag that is no longer new (kept, dismissed, explanation requested,
  explained or referred), what happens? → A: The signal is added to the flag and the flag is marked
  "has new signals" for the instructor; its review state, explanation and deadline do not change
  (FR-012).
- Q: Does the student still see a flag the instructor dismissed after asking for an explanation
  (REQ-14, REQ-15)? → A: Yes, with its signals, marked as dismissed (FR-014).
- Q: What ends the exam (REQ-09)? → A: The end time, or earlier when the student chooses "Finish
  exam", whichever comes first; it also ends at the end time when the student is not on the exam page
  (FR-009).
- Q: How does the prototype know a page leave was caused by a lost connection (REQ-08)? → A: The
  device's offline and online times are recorded; a page leave that overlaps an offline period is a
  connection loss (FR-021).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Take the exam with accommodations applied (Priority: P1)

**Goals**: G-30, G-51, G-39 | **Requirements**: REQ-01, REQ-02, REQ-04

A student opens the exam and sees one start page with the rules, their end time, their accommodations
and what is detected, and confirms it. Their approved extra time is already applied. While they type,
their answers are saved, so a reload or a dropped connection does not lose them.

**Why this priority**: This is what the student sees during an exam. Jordan's stress came from not
knowing if accommodations were applied and from losing time.

**Independent Test**: Select a mock student with 50% extra time, open the exam, check the start page and
end time, try to start without confirming, confirm, type an answer and reload the page.

**Acceptance Scenarios**:

1. **REQ-01**: **Given** a student has 50% extra time on a 60-minute exam, **When** the student opens the
   exam, **Then** the end time is 90 minutes after the start.
2. **REQ-02**: **Given** the start page is shown, **When** the student has not confirmed it, **Then** the
   exam does not start.
3. **REQ-04**: **Given** a student has typed an answer, **When** the page reloads, **Then** the answer is
   still there.

---

### User Story 2 - Give each student their own questions (Priority: P1)

**Goals**: G-3 | **Requirements**: REQ-03

Each student gets their own numeric version of each question, and the system records which version each
student received.

**Why this priority**: Alan needs unique versions so that a shared incorrect answer stands out (D2).

**Independent Test**: Open the same question as two mock students and compare the recorded versions.

**Acceptance Scenarios**:

1. **REQ-03**: **Given** two students take the same exam, **When** both open the same question, **Then**
   the system records which version each student received.

---

### User Story 3 - Record exam signals (Priority: P1)

**Goals**: G-115, G-7, G-116, G-117, G-10 | **Requirements**: REQ-05, REQ-06, REQ-07, REQ-08, REQ-09

The exam asks the student to enter fullscreen. Leaving the exam page or exiting fullscreen, pasting into
an answer field, and submitting an answer within 30 seconds of returning to the exam page are each
recorded as a signal. A fast answer after a connection loss or a help request is not recorded. When the
exam ends, students with the same incorrect answer to the same question are grouped, and the group is
added as a signal to each of their flags.

**Why this priority**: Without a camera (C2), we do not know if these signals give the instructor useful
flags. The prototype is the cheapest way to find out.

**Independent Test**: Run the exam as a mock student; confirm fullscreen is requested, switch tabs,
paste into an answer field, answer within 30 seconds of returning, repeat after a simulated connection
loss, and end the exam with three students sharing an incorrect answer.

**Acceptance Scenarios**:

1. **REQ-05**: **Given** the student confirms the start page, **When** the exam starts, **Then**
   fullscreen is requested.
2. **REQ-06**: **Given** the exam is running, **When** the student switches to another tab, **Then** a
   signal is recorded.
3. **REQ-07**: **Given** the exam is running, **When** the student pastes into an answer field, **Then**
   a signal is recorded.
4. **REQ-08**: **Given** the student has just returned to the exam page after switching tabs, **When**
   the student submits an answer within 30 seconds, **Then** a signal is recorded.
5. **REQ-08**: **Given** the student has just returned after a connection loss or a help request,
   **When** the student submits an answer within 30 seconds, **Then** no signal is recorded.
6. **REQ-09**: **Given** three students give the same incorrect answer to one question, **When** the exam
   ends, **Then** each of the three flags shows the group as a signal.

---

### User Story 4 - Ask for help without losing time (Priority: P2)

**Goals**: G-53, G-118 | **Requirements**: REQ-10, REQ-11

The student requests help from the exam page and must pick or type a reason. The timer pauses, the
questions are hidden and nothing is detected until the request is closed. The request is recorded with
the student's reason and its length, and the instructor can see it.

**Why this priority**: Decided in C3 (G-53 over G-2). It depends on the exam timer (User Story 1) and
the detection (User Story 3).

**Independent Test**: With 20 minutes left, open a help request with a reason, switch tabs, close it
after 2 minutes; check the remaining time, the hidden questions, the recorded request and the absence of
a page-leave signal; then open the exam record as the instructor.

**Acceptance Scenarios**:

1. **REQ-10**: **Given** 20 minutes remain, **When** the student opens a 2-minute help request with a
   reason, switches tabs during it, then closes it, **Then** the questions are hidden while it is open,
   20 minutes still remain, the help request is recorded, and no page-leave signal is recorded.
2. **REQ-11**: **Given** a help request was closed, **When** the instructor opens the student's exam
   record, **Then** the pause is shown with the student's reason and its length.

---

### User Story 5 - Instructor reviews one flag per student (Priority: P1)

**Goals**: G-20, G-111, G-112 | **Requirements**: REQ-12, REQ-13, REQ-14

Each student has at most one flag per exam. It collects all of that student's signals, each showing
what happened, when and why, together with the student's accommodations and pauses. The instructor
reviews each flag before the student sees it, and can dismiss it before or after the student explains.
A dismissed flag cannot be referred.

**Why this priority**: Handling a flag from signal to referral is the main concern of all three
stakeholders, and it is where conflict C4 sits.

**Independent Test**: Create two signals for one mock student, open the student's flags as the
instructor, check the single flag and its context, check that the student cannot see it, dismiss it and
try to refer it.

**Acceptance Scenarios**:

1. **REQ-12**: **Given** a student left the page and then answered within 30 seconds, **When** the
   instructor opens the student's flags, **Then** there is one flag with both signals, each showing what,
   when and why, plus the context.
2. **REQ-13**: **Given** a new flag exists, **When** the instructor has not reviewed it, **Then** the
   student cannot see it.
3. **REQ-14**: **Given** the instructor dismisses a flag, **When** the instructor tries to refer it,
   **Then** referral is not possible.

---

### User Story 6 - Student explains a flag (Priority: P2)

**Goals**: G-65, G-66 | **Requirements**: REQ-15, REQ-16

The instructor asks the student to explain a flag. Only then does the student see it, with its signals
and deadline. The student submits an explanation before the deadline and the instructor sees it.

**Why this priority**: Decided in C4 (G-111 over G-64). It depends on reviewed flags (User Story 5).

**Independent Test**: As the instructor, keep a flag; as the student, check before and after the
instructor asks for an explanation; submit an explanation; as the instructor, read it.

**Acceptance Scenarios**:

1. **REQ-15**: **Given** the instructor has kept a flag, **When** the student checks before and after the
   instructor asks for an explanation, **Then** the flag appears only after the request, with its
   signals and deadline.
2. **REQ-16**: **Given** the student was asked to explain a flag, **When** the student submits an
   explanation before the deadline, **Then** the instructor sees the explanation.

---

### User Story 7 - Refer a flag to the integrity office (Priority: P2)

**Goals**: G-25, G-113, G-114 | **Requirements**: REQ-17, REQ-18, REQ-19

After the student explains or the deadline passes, the instructor can refer the flag to the integrity
office. A referral creates a document with the flag, its evidence, the student's explanation and the
instructor's reason. The integrity office can view the document but not edit it.

**Why this priority**: The referral document is the handoff to the integrity office and ends the sprint
scope. It depends on User Story 6.

**Independent Test**: Refer a flag that has an explanation and one whose deadline has passed without
one; try to refer a flag that was never sent for explanation; open each document as the integrity
office.

**Acceptance Scenarios**:

1. **REQ-17**: **Given** the student was asked to explain, and has explained or the deadline has passed,
   **When** the instructor refers the flag, **Then** the flag is referred to the integrity office.
2. **REQ-18**: **Given** a flag is referred, **When** the document is generated, **Then** it contains the
   flag, its evidence, the explanation and the reason.
3. **REQ-19**: **Given** a referral document exists, **When** the integrity office opens it, **Then** the
   document can be read but not edited.

---

### Edge Cases

| Case | Expected behavior | Requirement | FR |
|---|---|---|---|
| A help request is still open when the end time arrives | The end time moves later by the length of the pause. | REQ-10 | FR-020 |
| A connection drop makes the student leave the exam page | The page leave is marked as a connection loss, and a fast answer after returning is not recorded. | REQ-06, REQ-08 | FR-021 |
| The student reloads the page during the exam | The answers are restored, the timer keeps running, and a page-leave signal is recorded. | REQ-04, REQ-06 | FR-022 |
| The deadline passes without an explanation | The instructor can still refer the flag, and the document states that no explanation was given. | REQ-17, REQ-18 | FR-023 |

## Requirements *(mandatory)*

### Functional Requirements

Each FR cites its user story (US) and its requirement from `docs/goal-model.md` section 1.

**Taking the exam**

- **FR-001** (US1, REQ-01): System MUST apply a student's approved extra time automatically, so that a
  60-minute exam with 50% extra time ends 90 minutes after the start.
- **FR-002** (US1, REQ-02): System MUST show, before the exam starts, one page with the rules, the
  student's end time, the student's accommodations and what is detected, and MUST NOT start the exam
  until the student confirms it.
- **FR-003** (US2, REQ-03): System MUST give each student their own numeric version of each question and
  MUST record which version each student received.
- **FR-004** (US1, REQ-04): System MUST save answers while the student types and MUST restore them after
  a page reload or a dropped connection.

**Detection during the exam**

- **FR-005** (US3, REQ-05): System MUST ask the student to enter fullscreen when the exam starts after
  the student confirms the start page. Fullscreen is requested only; the computer is not blocked (C1).
- **FR-006** (US3, REQ-06): System MUST record a signal when the student leaves the exam page or exits
  fullscreen.
- **FR-007** (US3, REQ-07): System MUST record a signal when the student pastes into an answer field.
- **FR-008** (US3, REQ-08): System MUST record a signal when the student submits an answer within 30
  seconds of returning to the exam page, unless the student is returning from a connection loss or a help
  request. Submitting an answer means pressing the Submit button on that question; continuous saving
  (FR-004) does not count as submitting. The 30-second threshold is fixed. This depends on knowing why the student left the page (D5).
- **FR-009** (US3, REQ-09): The exam ends when the student chooses "Finish exam" or when the end time
  is reached, whichever comes first, including when the student is not on the exam page at that time.
  When the exam ends, System MUST group students who gave the same incorrect answer to the same
  question and MUST add the group as a signal to each of their flags. Any shared incorrect answer forms a
  group.

**Help requests and pauses**

- **FR-010** (US4, REQ-10): System MUST let the student request help from the exam page and MUST require
  the student to pick or type a reason. While the request is open, the timer MUST pause, the questions
  MUST be hidden and no signals (FR-006 to FR-008) MUST be recorded. The request itself MUST be recorded.
  There is no maximum length for a help request.
- **FR-011** (US4, REQ-11): System MUST record each pause with the reason the student gave and its
  length, and MUST show it to the instructor in the student's exam record.

**Flag review**

- **FR-012** (US5, REQ-12): System MUST keep at most one flag per student per exam. The flag MUST collect
  all of that student's signals, each showing what happened, when and why, together with the student's
  accommodations and pauses as context. Signal types are recorded separately (O4) and the context is
  shown on each flag (O2). If a signal is added to a flag that is no longer new, System MUST mark the
  flag "has new signals" for the instructor, MUST NOT change its review state, explanation or deadline,
  and MUST clear the mark when the instructor opens the flag. A referral document already created is
  not changed.
- **FR-013** (US5, REQ-13): System MUST NOT show a flag to the student until the instructor has reviewed
  it (O3).
- **FR-014** (US5, REQ-14): System MUST let the instructor dismiss a flag before or after the student
  explains, and MUST NOT allow a dismissed flag to be referred. If the flag is dismissed after the
  student was asked to explain, the student MUST still see it, marked as dismissed.
- **FR-015** (US6, REQ-15): System MUST let the instructor ask the student to explain a flag, with a
  deadline 3 days after the request. The student MUST see a flag only after this request, with its
  signals and deadline.
- **FR-016** (US6, REQ-16): System MUST let the student submit an explanation before the deadline and
  MUST show the explanation to the instructor.

**Referral**

- **FR-017** (US7, REQ-17): System MUST let the instructor refer a flag to the integrity office only after
  an explanation was requested and the student has explained or the deadline has passed. A flag that was
  never sent for explanation MUST NOT be referable.
- **FR-018** (US7, REQ-18): A referral MUST create a document with the flag, its evidence, the student's
  explanation and the instructor's reason.
- **FR-019** (US7, REQ-19): System MUST let the integrity office view referral documents and MUST NOT let
  it edit them.

**Edge cases**

- **FR-020** (US4, REQ-10): If a help request is still open when the end time arrives, System MUST move
  the end time later by the length of the pause.
- **FR-021** (US3, REQ-06, REQ-08): System MUST record when the student's device goes offline and comes
  back online during the exam. When a connection drop makes the student leave the exam page (the leave
  overlaps an offline period), System
  MUST mark the page leave as a connection loss and MUST NOT record a fast answer after returning.
- **FR-022** (US1, REQ-04; US3, REQ-06): When the student reloads the page during the exam, System MUST
  restore the answers, keep the timer running and record a page-leave signal.
- **FR-023** (US7, REQ-17, REQ-18): When the deadline passes without an explanation, System MUST still let
  the instructor refer the flag, and the referral document MUST state that no explanation was given.

### Decisions on Overlapping and Conflicting Requirements

**Overlaps**

| ID | Overlap | Decision |
|---|---|---|
| O1 | Confirming accommodations, a one-page summary, and showing the rules before the start | Combined into one start page (REQ-02, FR-002). |
| O2 | Separating accommodations and technical problems from unusual behavior (Alan), and not counting normal behavior against the student (Jordan) | Combined: shown as context on each flag (REQ-12, FR-012). |
| O3 | Instructor screening (Alan) and human review (Nkechi, Jordan) | Combined into one review step (REQ-13, FR-013). |
| O4 | Four signal types | Recorded separately and collected in one flag per student per exam (REQ-12, FR-012). |

**Conflicts**

| ID | Conflict | Decision |
|---|---|---|
| C1 | Block outside resources (G-5) ↔ Don't over-restrict the exam (G-9) | **Compromise**: fullscreen only, without blocking the computer (REQ-05, FR-005). |
| C2 | Monitor the exam (G-6) ↔ Reduce student stress (G-43) | **Compromise**: no camera; detect page leaves, pastes and timing, and tell students beforehand (REQ-02, REQ-06 to REQ-08; FR-002, FR-006 to FR-008). |
| C3 | Pause the timer for help (G-53) ↔ Prevent outside help (G-2) | **Prioritize G-53**: the student keeps their time, the questions are hidden while help is open, and every pause is recorded with the student's reason (REQ-10, REQ-11; FR-010, FR-011). |
| C4 | Student explains first (G-64) ↔ Instructor reviews first (G-111) | **Prioritize G-111**: the student sees a flag only when the instructor asks for an explanation, and must be asked before any referral (REQ-13 to REQ-17; FR-013 to FR-017). |

### Dependencies

| ID | Dependency |
|---|---|
| D1 | REQ-12 depends on REQ-01 and REQ-11: each flag shows the student's extra time and pauses as context. |
| D2 | REQ-09 depends on REQ-03: because each student has a different version, the same incorrect answer from several students stands out. |
| D3 | REQ-16 depends on REQ-15, and REQ-17 on REQ-16: the student explains only after being asked, and a flag is referred only after the explanation or the deadline. |
| D4 | REQ-06 to REQ-08 depend on REQ-10: detection stops during a help request. |
| D5 | REQ-08 depends on REQ-06: the fast-answer signal needs to know why the student left the page. |

### Key Entities

- **Exam**: the one mock exam; has a length, rules and questions.
- **Student**: a mock student; has approved extra time (or none).
- **Question version**: the numeric version of a question given to one student; records which student
  received it.
- **Answer**: a student's saved answer to a question version.
- **Signal**: a recorded event (page leave or fullscreen exit, paste, fast answer after return, shared
  incorrect answer group) with its time, reason and student.
- **Offline period**: when the student's device went offline and came back online during the exam; used
  to mark a page leave as a connection loss.
- **Pause**: a help request with the student's reason, start and length.
- **Flag**: one per student per exam; collects all of that student's signals plus context; has a review
  state (new, kept, dismissed, explanation requested, explained, referred) and a "has new signals"
  mark.
- **Answer group**: students with the same incorrect answer to one question; added as a signal to each
  member's flag.
- **Explanation request**: a request on a flag with a deadline 3 days later and the student's
  explanation, if submitted.
- **Referral document**: created on referral; holds the flag, evidence, explanation (or a statement that
  none was given) and the instructor's reason; read-only for the integrity office.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 20 acceptance scenarios (REQ-01 to REQ-19, with REQ-08 having two) and all 4 edge cases
  pass as automated tests.
- **SC-002**: A student can go from opening the exam to the first question in under 1 minute, with their
  correct end time shown before they confirm.
- **SC-003**: In 100% of reload tests during an exam, no typed answer is lost.
- **SC-004**: 0 flags are visible to a student before the instructor asks for an explanation.
- **SC-005**: In 100% of tests, a student with several signals has exactly one flag for the exam.
- **SC-006**: An instructor can take a flag from new to referred, and the integrity office can open the
  resulting document, in under 5 minutes using only the prototype.

## Assumptions

- The prototype uses mock data: one exam and a small list of students.
- Users switch roles with a selector; there is no login.
- The student has 3 days to explain after the instructor asks.
- The response-time threshold is 30 seconds.
- There is no maximum length for a help request. Alan needs to confirm one.
- Any shared incorrect answer forms a group. Alan needs to clarify what makes a shared answer suspicious.

### Out of scope

Goals left out of the sprint in `docs/goal-model.md` section 0 are not built:

- The integrity office process after a referral: screening, due process, decision, appeal (G-73, G-83,
  G-90, G-91); conflicts C5 and C6 stay open
- Recording retention and the full evidence record (G-101, G-92); conflict C7 stays open
- Webcam monitoring and face identity checks (G-108, G-109)
- Auto-grading and TA grading work (G-12 to G-16)
- Resume or retake after a crash, device checks (G-40, G-41, G-57); only autosave (G-39) is covered
- Breaks, reduced-distraction mode, medical privacy (G-31, G-48, G-69 to G-71); extra time is the only
  accommodation
- Consistent review across TAs (G-23, G-24); there is one instructor role
