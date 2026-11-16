"""
17-626 HW2 - Goal model extracted from the interview with Dr. Alan Whitaker (instructor,
400-student intro statistics course, six TAs). Project: Online Exam Delivery and Proctoring.

Conventions used in all four models
- Every goal name starts with its unique ID, e.g. Achieve[G-3: ...]. IDs are unique across all
  three transcripts (Alan G-1..G-41, Jordan G-42..G-71, Nkechi G-72..G-109) so the combined
  model, use cases and traceability matrix can refer to them unambiguously.
- SOURCE comments cite transcript turns as "T<n>" where n is the line number of that turn in
  the transcript CSV file (the header is line 1).
- Goals NOT stated in the transcript (tacit knowledge, pattern/heuristic derived) are listed in
  MISSING and are highlighted YELLOW in the Mermaid output.
- Each Refinement is annotated with exactly one heuristic (H3-H12) or pattern (P1-P7) code
  from Appendix A of the assignment.
- Conditional goals use the "If [condition]" form (van Lamsweerde p. 266).
"""
from goalmodeling.schema import *

GOALS = {}      # goal ID -> goal object
CATEGORY = {}   # goal ID -> (type, category) for documentation
MISSING = set() # goal IDs not stated in the transcript (highlighted yellow)


def goal(cls, gid, name, refinements=None, performs=None, leaf=False,
         category="functional", missing=False):
    """Create a behavioral goal whose rendered name is Keyword[G-n: Name]."""
    g = cls(name=f"{gid}: {name}", performs=performs, refinements=refinements, leaf=leaf)
    GOALS[gid] = g
    CATEGORY[gid] = (cls.__name__.replace("Goal", ""), category)
    if missing:
        MISSING.add(gid)
    return g


def soft(keyword, gid, name, refinements=None, performs=None, leaf=False,
         category="non-functional", missing=False):
    """Create a soft goal rendered as Keyword[G-n: Name] (Improve/Increase/Reduce/Maximize/Minimize)."""
    g = SoftGoal(name=f"{keyword}[{gid}: {name}]", performs=performs,
                 refinements=refinements, leaf=leaf)
    GOALS[gid] = g
    CATEGORY[gid] = ("Soft", category)
    if missing:
        MISSING.add(gid)
    return g


def by(agent, operation, environment=False):
    """Performance link: a single responsible agent performing an operation (H11 leaf)."""
    a = Agent(agent, AgentType.ENVIRONMENT_AGENT if environment else AgentType.SOFTWARE_AGENT)
    o = Operation(operation, OperationCategory.ENVIRONMENT_OPERATION if environment
                  else OperationCategory.SOFTWARE_TO_BE_OPERATION)
    return [PerformanceLink(a, o)]


def ref(children, code, complete=False):
    """AND-refinement annotated with one heuristic/pattern code."""
    return Refinement(complete=complete, children=children, annotation=code)


def render(roots, links):
    """Generate the Mermaid definition and highlight non-transcript goals yellow."""
    text = generate_graph(roots, links).rstrip()
    if MISSING:
        nodes = ",".join(GOALS[gid].get_node_id() for gid in sorted(MISSING))
        text += f"\nclassDef missing fill:#ffff00,stroke:#000\nclass {nodes} missing\n"
    return text


# --------------------------------------------------------------------------------------------
# Leaf goals (requirements on software agents / expectations on environment agents)
# --------------------------------------------------------------------------------------------
# SOURCE T17, T20, T22: item bank with parameterized numeric questions, a different instance per student
g3 = goal(AchieveGoal, "G-3", "UniqueProblemInstanceIssuedToEachStudent", leaf=True,
          performs=by("ExamPlatform", "GenerateParameterizedInstances"))
# NOT IN TRANSCRIPT: lockdown alternative for enforcing the resource policy (tacit knowledge)
g5 = goal(AchieveGoal, "G-5", "ProhibitedResourcesBlockedDuringExam", leaf=True,
          performs=by("ExamPlatform", "LockDownExamBrowser"), missing=True)
# SOURCE T14: "The system should monitor the session, flag unusual patterns"
g7 = goal(AchieveGoal, "G-7", "ProhibitedResourceSignalDetected", leaf=True,
          performs=by("ProctoringMonitor", "DetectProhibitedResourceSignal"))
# NOT IN TRANSCRIPT: accuracy goal introduced by the unmonitorability pattern (P6)
g8 = goal(MaintainGoal, "G-8", "DetectedSignalReflectsActualResourceUse", leaf=True,
          performs=by("ProctoringMonitor", "CalibrateDetectionRules"),
          category="non-functional (accuracy)", missing=True)
# SOURCE T10, T22: 30 students shared the same wrong answer; "flag clusters of unusually similar work"
g10 = goal(AchieveGoal, "G-10", "SimilarAnswerClustersFlagged", leaf=True,
           performs=by("ExamPlatform", "CompareSubmissionSimilarity"))
# SOURCE T22: "generate and record each student's problem instance reliably"
g13 = goal(AchieveGoal, "G-13", "ProblemInstanceRecordedForEachStudent", leaf=True,
           performs=by("ExamPlatform", "RecordProblemInstance"))
# SOURCE T22, T68: "grade the parameterized answers automatically"
g14 = goal(AchieveGoal, "G-14", "AnswerGraded <b>If</b> ProblemInstanceRecorded", leaf=True,
           performs=by("ExamPlatform", "AutoGradeAgainstInstance"))
# SOURCE T68: "let us quickly correct questionable answers"
g15 = goal(AchieveGoal, "G-15", "GradeCorrected <b>If</b> TAFlagsQuestionableAnswer", leaf=True,
           performs=by("TA", "CorrectGrade", environment=True))
# SOURCE T40, T68: "organize written work for the TAs"
g16 = goal(AchieveGoal, "G-16", "WrittenWorkOrganizedForTAGrading", leaf=True,
           performs=by("ExamPlatform", "QueueWrittenResponsesForTAs"))
# SOURCE T40, T48: "see a clear history without keeping separate spreadsheets"; evidence was scattered
g17 = goal(MaintainGoal, "G-17", "FlaggedCaseHistoryKeptInOneRecord", leaf=True,
           performs=by("ExamPlatform", "LogCaseFindings"))
# SOURCE T40: "what happened, when it happened, and why it was flagged"
g20 = goal(AchieveGoal, "G-20", "FlagRecordsWhatWhenAndWhy", leaf=True,
           performs=by("ProctoringMonitor", "AttachEvidenceToFlag"))
# SOURCE T40, T96: separate technical problems / approved accommodations from unusual behavior
g21 = goal(AvoidGoal, "G-21", "AccommodationOrOutageFlaggedAsSuspicious", leaf=True,
           performs=by("ProctoringMonitor", "ExcludeAccommodationAndOutageEvents"))
# SOURCE T40: "The six TAs should be able to divide cases, record their findings"
g22 = goal(AchieveGoal, "G-22", "FlaggedCaseReviewedByAssignedTA <b>If</b> FlagRaised", leaf=True,
           performs=by("TA", "ReviewAssignedFlag", environment=True))
# NOT IN TRANSCRIPT: my interpretation of the vague term "consistency" (T58)
g24 = goal(AchieveGoal, "G-24", "SharedFlagReviewCriteriaApplied", leaf=True,
           performs=by("TA", "ApplyReviewCriteria", environment=True), missing=True)
# SOURCE T36: "refer the stronger cases through the university's academic integrity process"
g25 = goal(AchieveGoal, "G-25", "StrongCaseReferredToIntegrityProcess <b>If</b> EvidenceSufficient",
           leaf=True, performs=by("Instructor", "ReferCase", environment=True))
# SOURCE T29, T83: TAs check "the approved accommodation list"; "a reliable accommodation record"
g28 = goal(MaintainGoal, "G-28", "AccommodationRecordMatchesApprovedList", leaf=True,
           performs=by("ExamPlatform", "SyncApprovedAccommodations"),
           category="non-functional (accuracy)")
# SOURCE T26, T78, T83: extra time; "giving a student the standard deadline instead of the approved extra time"
g30 = goal(AchieveGoal, "G-30", "ExtendedTimeApplied <b>If</b> ExtraTimeApproved", leaf=True,
           performs=by("ExamPlatform", "ExtendStudentDeadline"))
# SOURCE T26, T78, T83: "failing to schedule a required break correctly"
g31 = goal(AchieveGoal, "G-31", "BreaksScheduled <b>If</b> BreaksApproved", leaf=True,
           performs=by("ExamPlatform", "ScheduleBreaks"))
# SOURCE T83: "a TA and I can verify it before the exam"
g33 = goal(AchieveGoal, "G-33", "AppliedAccommodationsVerifiedBeforeExam", leaf=True,
           performs=by("TA", "VerifyAccommodationSettings", environment=True))
# SOURCE T83: "keep a record of what was applied ... investigate any discrepancy afterward"
g34 = goal(AchieveGoal, "G-34", "AppliedAccommodationsLogged", leaf=True,
           performs=by("ExamPlatform", "LogAppliedAccommodation"))
# NOT IN TRANSCRIPT: converse of G-29 found with H9 (extra time only when approved)
g36 = goal(MaintainGoal, "G-36", "ExtendedTimeGranted <b>Only If</b> AccommodationApproved", leaf=True,
           performs=by("ExamPlatform", "BlockUnapprovedTimeOverride"),
           category="non-functional (security/integrity)", missing=True)
# SOURCE T94: "preserve what they've completed"
g39 = goal(MaintainGoal, "G-39", "CompletedAnswersSavedContinuously", leaf=True,
           performs=by("ExamPlatform", "AutosaveAnswers"),
           category="non-functional (reliability)")
# SOURCE T94: "let them resume"
g40 = goal(AchieveGoal, "G-40", "StudentResumedWithRemainingTime <b>If</b> ResumePossible", leaf=True,
           performs=by("ExamPlatform", "RestoreSessionAndTimer"))
# SOURCE T94: "or arrange a retake without giving anyone an advantage"
g41 = goal(AchieveGoal, "G-41", "EquivalentRetakeArranged <b>If Not</b> ResumePossible", leaf=True,
           performs=by("Instructor", "ScheduleEquivalentRetake", environment=True))

# --------------------------------------------------------------------------------------------
# Intermediate goals
# --------------------------------------------------------------------------------------------
# SOURCE T14: "flag unusual patterns ... keep those flags tied to specific evidence"
g6 = goal(AchieveGoal, "G-6", "ExamSessionMonitoredForProhibitedResourceUse",
          refinements=[ref([g7, g8], "P6")])
# SOURCE T14, T26: permitted resources = one page of notes and a calculator, no internet search
# OR-refinement: two alternative designs (lockdown vs monitoring), found by weighing pros/cons (H6)
g4 = goal(MaintainGoal, "G-4", "OnlyPermittedResourcesUsed",
          refinements=[ref([g5], "H6"), ref([g6], "H6")],
          category="non-functional (security/integrity)")
# SOURCE T7, T10, T14: answers from classmates, websites or messaging apps
g2 = goal(AvoidGoal, "G-2", "UnauthorizedHelpUsedDuringExam",
          refinements=[ref([g3, g4, g10], "H4")],
          category="non-functional (security/integrity)")
# SOURCE T58: "without making the exam so restrictive that it stops measuring statistics"
g9 = soft("Minimize", "G-9", "ExamRestrictionsBeyondResourcePolicy", leaf=True,
          category="non-functional (usability)")
# SOURCE T22: milestone = each student's instance recorded, then graded against it
g12 = goal(AchieveGoal, "G-12", "RoutineAnswersAutoGraded",
           refinements=[ref([g13, g14], "P1", complete=True)])
# SOURCE T14, T40: flags tied to specific, reviewable evidence
g19 = goal(AchieveGoal, "G-19", "UnusualBehaviorFlaggedWithReviewableEvidence",
           refinements=[ref([g20, g21], "H11")])
# SOURCE T58: "Six TAs can watch the same kind of behavior and describe it differently"
g23 = goal(MaintainGoal, "G-23", "ConsistentFlagReviewAcrossTAs",
           refinements=[ref([g24], "H4")], category="non-functional (consistency)")
# SOURCE T78, T83: extra time and scheduled breaks applied automatically (two disjoint cases)
g29 = goal(AchieveGoal, "G-29", "ApprovedAccommodationsApplied <b>If</b> AccommodationApproved",
           refinements=[ref([g30, g31], "P3")])
# SOURCE T83: verify before the exam (TA) and investigate afterwards (record) -> split by agent
g32 = goal(MaintainGoal, "G-32", "AccommodationApplicationVerifiable",
           refinements=[ref([g33, g34], "H5")])
# SOURCE T7: "the process fair for the honest students"; converse check (H9) of G-29
g35 = goal(MaintainGoal, "G-35", "ExamTimingEquitableAcrossStudents",
           refinements=[ref([g29, g36], "H9")], category="non-functional (fairness)")
# SOURCE T94, T96: resume if possible, otherwise retake (complementary case, H10)
g38 = goal(AchieveGoal, "G-38", "ExamContinuedFairly <b>If</b> SessionDisrupted",
           refinements=[ref([g39, g40, g41], "H10")])
# SOURCE T96: "a failure can cost a student exam time or erase work"
g37 = goal(MaintainGoal, "G-37", "StudentExamWorkAndTimeIntact",
           refinements=[ref([g38], "H8")], category="non-functional (reliability)")

# --------------------------------------------------------------------------------------------
# High-level goals (roots)
# --------------------------------------------------------------------------------------------
# SOURCE T7: "I want the exams to reflect what students actually know"
g1 = soft("Maximize", "G-1", "ExamsMeasureStudentsOwnKnowledge",
          refinements=[ref([g2, g9, g35, g37], "H12")])
# SOURCE T7, T52, T68, T75: grading manageable; "making grading faster without making it careless"
g11 = soft("Reduce", "G-11", "ExamWorkloadForInstructorAndTAs",
           refinements=[ref([g12, g15, g16, g17], "H4")])
# SOURCE T36, T38, T40, T52: review, document, refer; "isn't as consistent or efficient as I'd like"
g18 = goal(AchieveGoal, "G-18", "SuspectedMisconductHandledFairlyAndConsistently",
           refinements=[ref([g19, g22, g23, g25, g17], "H4")])
# SOURCE T40, T75, T88: "so honest students aren't dragged into an investigation"
g26 = soft("Minimize", "G-26", "HonestStudentsWronglyFlagged",
           refinements=[ref([g20, g21], "H7")])
# SOURCE T29, T33, T78, T80, T83, T88: "apply accommodations accurately"
g27 = goal(MaintainGoal, "G-27", "ApprovedAccommodationsAppliedAccurately",
           refinements=[ref([g28, g29, g32], "H4")], category="non-functional (accuracy)")

# --------------------------------------------------------------------------------------------
# Obstacles and conflicts
# --------------------------------------------------------------------------------------------
# SOURCE T94: "what happens if the system or a student's connection fails during an exam"
o1 = Obstacle("ConnectionOrSystemFailureDuringExam")

ROOTS = [g1, g11, g18, g26, g27]
LINKS = [
    ObstructionLink(g37, o1),
    ResolutionLink(g38, o1),
    # Intra-stakeholder conflict (T58): locking down resources vs. keeping the exam open-note
    ConflictLink(g5, g9),
]

if __name__ == "__main__":
    output = render(ROOTS, LINKS)
    print(output)
    print(generate_pako_link(output, "edit",
                             config={"theme": "default",
                                     "themeVariables": {"fontFamily": "Segoe UI Symbol, Helvetica"}}))
    print("\nGoals:", len(GOALS), "| Not in transcript:", sorted(MISSING, key=lambda x: int(x[2:])))
