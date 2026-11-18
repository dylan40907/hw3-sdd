# Goal Model

Version 2. Changes from Version 1 are listed in section 5.

## 0. Model, Scope and Justification

### Goal model files

| File | Contents |
|---|---|
| [goal_model_v2.py](goal_model_v2.py) | Merged team goal model, updated for the sprint. Sprint goals are green, goals not stated in any transcript are yellow, and conflicts are lightning-bolt links. |
| [goal_model_v2_mermaid.txt](goal_model_v2_mermaid.txt) | Link to the rendered diagram. |
| [../hw2/dylan/](../hw2/dylan/), [../hw2/ashley/](../hw2/ashley/) | Each member's original HW2 models and interview transcripts. |

Goal IDs G-1 to G-110 come from Dylan's HW2 combined model, which had the most detail. Ashley's
HW2 model was reconciled into it: goals she heard directly that Dylan had only inferred are no
longer marked as inferred (G-53), and goals only her interviews produced were added as G-111 to
G-118. Seven goals were reworded to match the sprint decisions (G-3, G-7, G-20, G-25, G-51, G-65,
G-66).

### Why these goals

| Criterion | Goals | Reason |
|---|---|---|
| Core | G-20, G-111, G-112, G-65, G-66, G-25, G-113, G-114 (REQ-12 to REQ-19) | Handling a flag from signal to referral is the main concern of all three stakeholders, and it is where our biggest conflict sits (C4, found in both members' models). |
| User-facing | G-30, G-51, G-39, G-53 (REQ-01, REQ-02, REQ-04, REQ-10) | This is what the student sees during an exam. Jordan's stress came from not knowing if accommodations were applied and from losing time. |
| Uncertain | G-115, G-7, G-116, G-117, G-10, G-3, G-118 (REQ-03, REQ-05 to REQ-09, REQ-11) | We do not know if detection without a camera gives the instructor useful flags, or how pausing the timer interacts with detection. A prototype is the cheapest way to find out. |

### Goals left out of the sprint

| Goals | Why they were less important for this sprint |
|---|---|
| Integrity office process after a referral: screening, due process, decision, appeal (G-73, G-83, G-90, G-91) | A separate case system. The sprint stops at the referral document, which is the handoff. Conflicts C5 and C6 stay open. |
| Recording retention and the full evidence record (G-101, G-92) | Needs a policy decision from the integrity office (C7). The sprint keeps no recordings. |
| Webcam monitoring and face identity checks (G-108, G-109) | Rejected for the sprint in C2 because of student stress. |
| Auto-grading and TA grading work (G-12 to G-16) | Well understood, low uncertainty, and not involved in any conflict. |
| Resume or retake after a crash, device checks (G-40, G-41, G-57) | The sprint covers autosave only (G-39). |
| Breaks, reduced-distraction mode, medical privacy (G-31, G-48, G-69 to G-71) | Extra time is the one accommodation needed to show the flag context. |
| Consistent review across TAs (G-23, G-24) | The prototype has one instructor role. |

### Conflicts kept in the model but outside the sprint

| ID | Conflict | Status |
|---|---|---|
| C5 | Student explains before a formal case (G-64) ↔ Office opens a case before notifying the student (G-81) | Unresolved. Needs the integrity office to confirm. |
| C6 | Instructor decides which cases to pursue (G-25) ↔ Only an authorized reviewer decides (G-90) | Unresolved. Ashley's interviews suggest two stages and not a conflict. Needs stakeholder clarification. |
| C7 | Delete recordings after retention (G-101) ↔ Keep the full record for appeals (G-92) | Unresolved. Needs a policy decision. |

## 1. Selected Stakeholder Goals and Requirements

| Goal | Goal statement | Stakeholder | Requirement | Requirement statement |
|---|---|---|---|---|
| G-30 | Achieve[ExtendedTimeApplied If ExtraTimeApproved] | Alan, Jordan | REQ-01 | Approved extra time is applied automatically. |
| G-51 | Achieve[ExamConditionsConfirmedOnOnePage Before Start] | Jordan, Alan | REQ-02 | Before starting, the student sees and confirms one page with the rules, the end time, the accommodations and what is detected. |
| G-3 | Achieve[UniqueProblemInstanceIssuedAndRecordedForEachStudent] | Alan | REQ-03 | Each student gets their own numeric version of each question, and the system records which version each student received. |
| G-39 | Maintain[CompletedAnswersSavedContinuously] | Alan, Jordan | REQ-04 | Answers are saved while the student types, so a reload or a dropped connection does not lose them. |
| G-115 | Achieve[FullscreenModeEntered Before Start] | Derived from C1 | REQ-05 | The exam asks the student to enter fullscreen. |
| G-7 | Achieve[PageLeaveOrFullscreenExitDetected] | Alan, Nkechi | REQ-06 | Leaving the exam page or exiting fullscreen is recorded. |
| G-116 | Achieve[PasteIntoAnswerFieldDetected] | Derived from C2 | REQ-07 | Pasting into an answer field is recorded. |
| G-117 | Achieve[ResponseTimeAnomalyDetected Unless ReturnAfterOutageOrHelp] | Nkechi | REQ-08 | An answer submitted within 30 seconds of returning to the exam page is recorded, unless the student is returning from a connection loss or a help request. |
| G-10 | Achieve[SimilarAnswerClustersFlagged] | Alan | REQ-09 | Students with the same incorrect answer to the same question are grouped, and the group is added as a signal to each of their flags. |
| G-53 | Achieve[TimerPausedAndQuestionsHidden While SupportRequestOpen] | Jordan | REQ-10 | The student can request help in the exam page and must pick or type a reason; the timer pauses, the questions are hidden and nothing is detected until the request is closed, but the request itself is recorded. |
| G-118 | Maintain[EachPauseRecordedWithStudentReasonAndDuration] | Alan, Nkechi | REQ-11 | Each pause is recorded with the reason the student gave and its length. |
| G-20 | Achieve[StudentSignalsCollectedInOneFlagWithWhatWhenWhyAndContext] | Alan, Nkechi | REQ-12 | Each student has at most one flag per exam. It collects all of that student's signals, each showing what happened, when and why, together with the student's accommodations and pauses. |
| G-111 | Achieve[FlagScreenedByInstructor Before StudentContacted] | Alan | REQ-13 | The instructor reviews each flag before the student sees it. |
| G-112 | Achieve[FlagDismissedWithoutReferral If ConcernExplained] | Derived from G-25 | REQ-14 | The instructor can dismiss a flag before or after the student explains; a dismissed flag cannot be referred. |
| G-65 | Achieve[FlagDetailsShownToStudent When ExplanationRequested] | Jordan | REQ-15 | The instructor can ask the student to explain a flag; the student sees a flag only after this request. |
| G-66 | Achieve[StudentExplanationSubmitted Before ResponseDeadline] | Jordan, Nkechi | REQ-16 | The student can submit an explanation before the deadline. |
| G-25 | Achieve[CaseReferredToIntegrityOffice If ConcernRemainsSerious] | Alan, Nkechi | REQ-17 | After the student explains or the deadline passes, the instructor can refer the flag to the integrity office. A flag cannot be referred without first asking for an explanation. |
| G-113 | Achieve[ReferralDocumentAssembled] | Nkechi, Alan | REQ-18 | A referral creates a document with the flag, its evidence, the student's explanation and the instructor's reason. |
| G-114 | Achieve[ReferralDocumentViewableByIntegrityOffice] | Nkechi | REQ-19 | The integrity office can view the referral document. |

## 2. Acceptance Scenarios

| Requirement | Given | When | Then |
|---|---|---|---|
| REQ-01 | A student has 50% extra time on a 60-minute exam | The student opens the exam | The end time is 90 minutes after the start |
| REQ-02 | The start page is shown | The student has not confirmed it | The exam does not start |
| REQ-03 | Two students take the same exam | Both open the same question | The system records which version each student received |
| REQ-04 | A student has typed an answer | The page reloads | The answer is still there |
| REQ-05 | The student confirms the start page | The exam starts | Fullscreen is requested |
| REQ-06 | The exam is running | The student switches to another tab | A signal is recorded |
| REQ-07 | The exam is running | The student pastes into an answer field | A signal is recorded |
| REQ-08 | The student has just returned to the exam page after switching tabs | The student submits an answer within 30 seconds | A signal is recorded |
| REQ-08 | The student has just returned after a connection loss or a help request | The student submits an answer within 30 seconds | No signal is recorded |
| REQ-09 | Three students give the same incorrect answer to one question | The exam ends | Each of the three flags shows the group as a signal |
| REQ-10 | 20 minutes remain | The student opens a 2-minute help request with a reason, switches tabs during it, then closes it | The questions are hidden while it is open, 20 minutes still remain, the help request is recorded, and no page-leave signal is recorded |
| REQ-11 | A help request was closed | The instructor opens the student's exam record | The pause is shown with the student's reason and its length |
| REQ-12 | A student left the page and then answered within 30 seconds | The instructor opens the student's flags | There is one flag with both signals, each showing what, when and why, plus the context |
| REQ-13 | A new flag exists | The instructor has not reviewed it | The student cannot see it |
| REQ-14 | The instructor dismisses a flag | The instructor tries to refer it | Referral is not possible |
| REQ-15 | The instructor has kept a flag | The student checks before and after the instructor asks for an explanation | The flag appears only after the request, with its signals and deadline |
| REQ-16 | The student was asked to explain a flag | The student submits an explanation before the deadline | The instructor sees the explanation |
| REQ-17 | The student was asked to explain, and has explained or the deadline has passed | The instructor refers the flag | The flag is referred to the integrity office |
| REQ-18 | A flag is referred | The document is generated | It contains the flag, its evidence, the explanation and the reason |
| REQ-19 | A referral document exists | The integrity office opens it | The document can be read but not edited |

## 3. Assumptions, Dependencies, and Edge Cases

### Assumptions

- The prototype uses mock data: one exam and a small list of students.
- Users switch roles with a selector; there is no login.
- The student has 3 days to explain after the instructor asks.
- The response-time threshold is 30 seconds.
- There is no maximum length for a help request. Alan needs to confirm one.
- Any shared incorrect answer forms a group. Alan needs to clarify what makes a shared answer suspicious.

### Dependencies

| ID | Dependency |
|---|---|
| D1 | REQ-12 depends on REQ-01 and REQ-11: each flag shows the student's extra time and pauses as context. |
| D2 | REQ-09 depends on REQ-03: because each student has a different version, the same incorrect answer from several students stands out. |
| D3 | REQ-16 depends on REQ-15, and REQ-17 on REQ-16: the student explains only after being asked, and a flag is referred only after the explanation or the deadline. |
| D4 | REQ-06 to REQ-08 depend on REQ-10: detection stops during a help request. |
| D5 | REQ-08 depends on REQ-06: the fast-answer signal needs to know why the student left the page. |

### Edge Cases

| Case | Expected behavior |
|---|---|
| A help request is still open when the end time arrives | The end time moves later by the length of the pause. |
| A connection drop makes the student leave the exam page | The page leave is marked as a connection loss, and a fast answer after returning is not recorded. |
| The student reloads the page during the exam | The answers are restored, the timer keeps running, and a page-leave signal is recorded. |
| The deadline passes without an explanation | The instructor can still refer the flag, and the document states that no explanation was given. |

## 4. Decisions on Overlapping and Conflicting Requirements

### Overlaps

| ID | Overlap | Decision |
|---|---|---|
| O1 | Confirming accommodations, a one-page summary, and showing the rules before the start | Combined into one start page (REQ-02). |
| O2 | Separating accommodations and technical problems from unusual behavior (Alan), and not counting normal behavior against the student (Jordan) | Combined: shown as context on each flag (REQ-12). |
| O3 | Instructor screening (Alan) and human review (Nkechi, Jordan) | Combined into one review step (REQ-13). |
| O4 | Four signal types | Recorded separately and collected in one flag per student per exam (REQ-12). |

### Conflicts

| ID | Conflict | Decision |
|---|---|---|
| C1 | Block outside resources (G-5) ↔ Don't over-restrict the exam (G-9) | **Compromise**: fullscreen only, without blocking the computer (REQ-05). |
| C2 | Monitor the exam (G-6) ↔ Reduce student stress (G-43) | **Compromise**: no camera; detect page leaves, pastes and timing, and tell students beforehand (REQ-02, REQ-06 to REQ-08). |
| C3 | Pause the timer for help (G-53) ↔ Prevent outside help (G-2) | **Prioritize G-53**: the student keeps their time, the questions are hidden while help is open, and every pause is recorded with the student's reason (REQ-10, REQ-11). |
| C4 | Student explains first (G-64) ↔ Instructor reviews first (G-111) | **Prioritize G-111**: the student sees a flag only when the instructor asks for an explanation, and must be asked before any referral (REQ-13 to REQ-17). |

## 5. Changes from Version 1

| Observation | What changed | Goals and requirements |
|---|---|---|
| V1-1 | One flag per student per exam instead of one flag per signal, to reduce review work and keep one record per case. | G-20, REQ-12, REQ-09, O4 |
| V1-2 | The student gives a reason when asking for help. A maximum pause length is kept as an open question for Alan. | G-53, G-118, REQ-10, REQ-11 |
| V1-3 | No fast-answer signal after a connection loss or a help request, so an outage is not treated as suspicious. | G-117, G-21, REQ-08 |
| V1-4 | Not changed. Kept as an open question for Alan. | G-10, REQ-09 |
| V1-5 | Questions are hidden while help is open. V1 did this without it being specified; it is now part of REQ-10. | G-53, REQ-10, C3 |
