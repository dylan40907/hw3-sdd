"""
17-626 HW3 - Team goal model, Version 2.

Base: Dylan's HW2 combined model (hw2/dylan/goal_model_combined.py), reconciled with Ashley's
HW2 model (hw2/ashley/). Goal IDs G-1 .. G-110 keep their HW2 meaning.

Changes for the sprint (see docs/goal-model.md for the decisions)
- Reworded to match the sprint decisions: G-3, G-7, G-20, G-25, G-51, G-65, G-66.
- New goals G-111 .. G-118. G-111, G-113, G-114, G-117 and G-118 come from Ashley's interviews
  (hw2/ashley/transcripts). G-112, G-115 and G-116 are derived from a conflict decision and are
  not stated in any transcript.
- SPRINT holds the 19 goals selected for the prototype. They are drawn GREEN. Goals not stated
  in any transcript keep their YELLOW fill (a yellow goal in the sprint gets a green border).
- No conflict was removed. C1 to C4 involve sprint goals and carry a decision. C5 to C7 are
  outside the sprint and stay unresolved.
- G-53 was inferred in HW2 (yellow) but Ashley's Jordan asked for it directly, so it is no
  longer yellow.
- Version 2 changes, from the V1 evaluation in docs/traceability.md:
  V1-1: G-20 reworded. One flag per student per exam collects all of that student's signals.
  V1-2: G-118 reworded. The pause is recorded with the reason the student gives.
        A maximum pause length is an open question for Alan.
  V1-3: G-117 reworded. No fast-answer signal after a connection loss or a help request (G-21).
  V1-4: Not changed. What makes a shared wrong answer suspicious (G-10) is an open question for Alan.
  V1-5: G-53 reworded. Questions are hidden while a help request is open (decision C3).
- Run: pip install git+https://github.com/cmu-relab/goalmodeling, then python goal_model_v2.py
- SOURCE tags: A/J/N = Dylan's transcripts (line number), aA/aJ/aN = Ashley's transcripts.
"""
from goalmodeling.schema import *

GOALS = {}      # goal ID -> goal object
CATEGORY = {}   # goal ID -> (type, category) for documentation
MISSING = set() # goal IDs not stated in the transcript (highlighted yellow)

# The 19 goals selected for the sprint (REQ-01 .. REQ-19 in docs/goal-model.md)
SPRINT = ["G-30", "G-51", "G-3", "G-39", "G-115", "G-7", "G-116", "G-117", "G-10", "G-53",
          "G-118", "G-20", "G-111", "G-112", "G-65", "G-66", "G-25", "G-113", "G-114"]


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
    sprint = ",".join(GOALS[gid].get_node_id() for gid in SPRINT if gid not in MISSING)
    both = ",".join(GOALS[gid].get_node_id() for gid in SPRINT if gid in MISSING)
    text += f"classDef sprint fill:#b6f2b6,stroke:#1a7f1a,stroke-width:3px\nclass {sprint} sprint\n"
    if both:
        text += f"classDef sprintMissing fill:#ffff00,stroke:#1a7f1a,stroke-width:4px\nclass {both} sprintMissing\n"
    return text




def agent(name, environment=False):
    """Responsibility link to a single agent (operations omitted in the combined model)."""
    return [PerformanceLink(Agent(name, AgentType.ENVIRONMENT_AGENT if environment
                                  else AgentType.SOFTWARE_AGENT), None)]


# Retained goal <- goals merged into it (duplicates across transcripts)
MERGED = {
    "G-1": ["G-42"],          # exams measure own knowledge (A) = student can demonstrate knowledge (J)
    "G-11": ["G-106"],        # instructor/TA workload (A) + integrity office effort (N)
    "G-17": ["G-93"],         # one case history record (A) = one case record with chronology (N)
    "G-18": ["G-72"],         # misconduct handled fairly/consistently (A) = cases resolved fairly (N)
    "G-20": ["G-74"],         # flag records what/when/why (A) = flag linked to timestamp/source/context (N)
    "G-26": ["G-105"],        # honest students wrongly flagged (A) + unfounded cases opened (N)
    "G-27": ["G-44"],         # accommodations applied accurately (A) = same goal (J)
    "G-29": ["G-45"],         # accommodations applied if approved (A) = applied automatically (J)
    "G-37": [],               # (obstacle merged: ExamFreezesOnStudentDevice (J) into o1 (A))
    "G-40": ["G-59"],         # resume with remaining time (A) = work and time restored if freeze (J)
    "G-75": ["G-67"],         # flag not treated as finding (N) = human review before violation (J)
}


# ============================================================================================
# Leaf goals
# ============================================================================================
# --- Exam integrity (Alan + Nkechi) ---
g3 = goal(AchieveGoal, "G-3", "UniqueProblemInstanceIssuedAndRecordedForEachStudent", leaf=True,
          performs=agent("ExamPlatform"))                                   # A17, A20, A22
g5 = goal(AchieveGoal, "G-5", "ProhibitedResourcesBlockedDuringExam", leaf=True,
          performs=agent("ExamPlatform"), missing=True)                     # tacit alternative
g7 = goal(AchieveGoal, "G-7", "PageLeaveOrFullscreenExitDetected", leaf=True,
          performs=agent("ProctoringMonitor"))                              # A14, N29
g8 = goal(MaintainGoal, "G-8", "DetectedSignalReflectsActualResourceUse", leaf=True,
          performs=agent("ProctoringMonitor"), category="non-functional (accuracy)",
          missing=True)                                                     # P6 accuracy goal
# NEW in HW3 (sprint): lighter detection chosen in conflicts C1 and C2
g115 = goal(AchieveGoal, "G-115", "FullscreenModeEntered <b>Before</b> Start", leaf=True,
            performs=agent("ExamPlatform"), missing=True)                   # derived from C1
g116 = goal(AchieveGoal, "G-116", "PasteIntoAnswerFieldDetected", leaf=True,
            performs=agent("ProctoringMonitor"), missing=True)              # derived from C2
g117 = goal(AchieveGoal, "G-117", "ResponseTimeAnomalyDetected <b>Unless</b> ReturnAfterOutageOrHelp", leaf=True,
            performs=agent("ProctoringMonitor"))                            # aN; V2 exception from V1-3 (G-21)
g10 = goal(AchieveGoal, "G-10", "SimilarAnswerClustersFlagged", leaf=True,
           performs=agent("ExamPlatform"))                                  # A10, A22; V1-4 open for Alan
g108 = goal(AchieveGoal, "G-108", "FaceIdentityMatchChecked", leaf=True,
            performs=agent("ProctoringMonitor"))                            # N27, N29
g109 = goal(MaintainGoal, "G-109", "FaceMatchAccurateAcrossStudentGroups", leaf=True,
            performs=agent("ProctoringMonitor"), category="non-functional (accuracy)",
            missing=True)                                                   # P6 accuracy goal

# --- Grading and workload (Alan + Nkechi) ---
g13 = goal(AchieveGoal, "G-13", "ProblemInstanceRecordedForEachStudent", leaf=True,
           performs=agent("ExamPlatform"))                                  # A22
g14 = goal(AchieveGoal, "G-14", "AnswerGraded <b>If</b> ProblemInstanceRecorded", leaf=True,
           performs=agent("ExamPlatform"))                                  # A22, A68
g15 = goal(AchieveGoal, "G-15", "GradeCorrected <b>If</b> TAFlagsQuestionableAnswer", leaf=True,
           performs=agent("TA", True))                                      # A68
g16 = goal(AchieveGoal, "G-16", "WrittenWorkOrganizedForTAGrading", leaf=True,
           performs=agent("ExamPlatform"))                                  # A40, A68
# MERGED G-93 (N15, N53, N73) into G-17 (A40, A48)
g17 = goal(MaintainGoal, "G-17", "CaseEvidenceChronologyAndDecisionsKeptInOneRecord", leaf=True,
           performs=agent("CaseManagementSystem"))
g103 = goal(AchieveGoal, "G-103", "CaseOutcomeReportsGenerated", leaf=True,
            performs=agent("CaseManagementSystem"))                         # N15
g104 = goal(AchieveGoal, "G-104", "InconsistentOutcomePatternsReviewed", leaf=True,
            performs=agent("IntegrityOffice", True))                        # N32
g24 = goal(AchieveGoal, "G-24", "SharedFlagReviewCriteriaApplied", leaf=True,
           performs=agent("TA", True), missing=True)                        # interpretation of A58

# --- Flags (all three stakeholders) ---
# MERGED G-74 (N29, N53, N66) into G-20 (A40)
g20 = goal(AchieveGoal, "G-20", "StudentSignalsCollectedInOneFlagWithWhatWhenWhyAndContext", leaf=True,
           performs=agent("ProctoringMonitor"))                             # V2 from V1-1
g21 = goal(AvoidGoal, "G-21", "AccommodationOrOutageFlaggedAsSuspicious", leaf=True,
           performs=agent("ProctoringMonitor"))                             # A40, A96, N32
g62 = goal(AvoidGoal, "G-62", "ThinkingBehaviorFlaggedAsMisconduct", leaf=True,
           performs=agent("ProctoringMonitor"))                             # J9, J12, J75
g63 = goal(AvoidGoal, "G-63", "UnavoidableHouseholdEventsFlaggedAsMisconduct", leaf=True,
           performs=agent("ProctoringMonitor"))                             # J50, J53, N41
g65 = goal(AchieveGoal, "G-65", "FlagDetailsShownToStudent <b>When</b> ExplanationRequested", leaf=True,
           performs=agent("ExamPlatform"))                                  # J18, J99
g66 = goal(AchieveGoal, "G-66", "StudentExplanationSubmitted <b>Before</b> ResponseDeadline", leaf=True,
           performs=agent("Student", True))                                 # J18, J85, J99
g68 = goal(AvoidGoal, "G-68", "StudentInterruptedDuringExamByFlag", leaf=True,
           performs=agent("ProctoringMonitor"))                             # J16
g22 = goal(AchieveGoal, "G-22", "FlaggedCaseReviewedByAssignedTA <b>If</b> FlagRaised", leaf=True,
           performs=agent("TA", True))                                      # A40
# NEW in HW3 (sprint): flag screening and referral steps
g111 = goal(AchieveGoal, "G-111", "FlagScreenedByInstructor <b>Before</b> StudentContacted", leaf=True,
            performs=agent("Instructor", True))                             # aA (Ashley's Alan)
g112 = goal(AchieveGoal, "G-112", "FlagDismissedWithoutReferral <b>If</b> ConcernExplained", leaf=True,
            performs=agent("Instructor", True), missing=True)               # derived from G-25 (H10)
g113 = goal(AchieveGoal, "G-113", "ReferralDocumentAssembled", leaf=True,
            performs=agent("ExamPlatform"))                                 # aN, aA
g114 = goal(AchieveGoal, "G-114", "ReferralDocumentViewableByIntegrityOffice", leaf=True,
            performs=agent("ExamPlatform"))                                 # aN
g25 = goal(AchieveGoal, "G-25", "CaseReferredToIntegrityOffice <b>If</b> ConcernRemainsSerious",
           refinements=[ref([g113, g114], "P1")])                           # A36, milestones

# --- Integrity office process (Nkechi + Jordan) ---
# MERGED G-67 (J65) into G-75 (N21, N29, N59)
g75 = goal(AvoidGoal, "G-75", "FlagTreatedAsMisconduct <b>Without</b> HumanReview", leaf=True,
           performs=agent("Investigator", True), category="non-functional (fairness)")
g77 = goal(AchieveGoal, "G-77", "FlagComparedAgainstDocumentedAccommodations", leaf=True,
           performs=agent("Investigator", True))                            # N27, N32
g78 = goal(AchieveGoal, "G-78", "FlagComparedAgainstTechnicalEvents", leaf=True,
           performs=agent("Investigator", True))                            # N32, N48
g79 = goal(AchieveGoal, "G-79", "EnvironmentalEventsSeparatedFromExamConduct", leaf=True,
           performs=agent("Investigator", True))                            # N41, N45, N66
# NEW (combined only): resolves conflict G-64 <-> G-81, not stated in any transcript
g110 = goal(AchieveGoal, "G-110", "StudentExplanationConsideredInScreening <b>If</b> ExplanationSubmitted",
            leaf=True, performs=agent("Investigator", True), missing=True)
g81 = goal(AchieveGoal, "G-81", "FormalCaseOpened <b>If</b> EvidenceMeetsPreliminaryThreshold",
           leaf=True, performs=agent("Investigator", True))                 # N21, N37
g82 = goal(AchieveGoal, "G-82", "ReportDismissed <b>If Not</b> EvidenceMeetsPreliminaryThreshold",
           leaf=True, performs=agent("Investigator", True))                 # N6, N57
g84 = goal(AchieveGoal, "G-84", "StudentNotifiedOfAllegation", leaf=True,
           performs=agent("CaseManagementSystem"))                          # N11, N37
g85 = goal(AchieveGoal, "G-85", "EvidenceMadeAvailableToStudent", leaf=True,
           performs=agent("CaseManagementSystem"))                          # N11, N15, N37
g87 = goal(AchieveGoal, "G-87", "ResponseRecorded <b>If</b> SubmittedWithinResponsePeriod", leaf=True,
           performs=agent("CaseManagementSystem"))                          # N37
g88 = goal(AchieveGoal, "G-88", "ResponseSubmittedByStudent", leaf=True,
           performs=agent("Student", True))                                 # N11, N32
g89 = goal(MaintainGoal, "G-89", "DecisionWithheld <b>Unless</b> ResponsePeriodEnded", leaf=True,
           performs=agent("CaseManagementSystem"))                          # N11
g90 = goal(AchieveGoal, "G-90", "DecisionMadeOnFullRecordWithReasons", leaf=True,
           performs=agent("AuthorizedReviewer", True))                      # N11, N37, N48, N59
g91 = goal(AchieveGoal, "G-91", "AppealReviewedOnSameRecord <b>If</b> AppealFiled", leaf=True,
           performs=agent("AppealReviewer", True))                          # N37
g95 = goal(MaintainGoal, "G-95", "EvidenceMetadataPreserved", leaf=True,
           performs=agent("CaseManagementSystem"), category="non-functional (integrity)")  # N23
g96 = goal(MaintainGoal, "G-96", "AccessAndChangesAuditLogged", leaf=True,
           performs=agent("CaseManagementSystem"),
           category="non-functional (accountability)")                      # N71, N73
g97 = goal(MaintainGoal, "G-97", "AuditTimestampsTamperResistant", leaf=True,
           performs=agent("CaseManagementSystem"), category="non-functional (integrity)")  # N71

# --- Privacy (Jordan + Nkechi) ---
g70 = goal(MaintainGoal, "G-70", "InstructorViewLimitedToApprovedAccommodation", leaf=True,
           performs=agent("ExamPlatform"), category="non-functional (confidentiality)")  # J109, J114
g71 = goal(MaintainGoal, "G-71", "MedicalDetailsKeptWithinDisabilityServices", leaf=True,
           performs=agent("DisabilityServices", True),
           category="non-functional (confidentiality)")                     # J109, J114
g99 = goal(AvoidGoal, "G-99", "UnauthorizedCaseRecordAccess", leaf=True,
           performs=agent("CaseManagementSystem"),
           category="non-functional (confidentiality)")                     # N15, N32
g100 = goal(AvoidGoal, "G-100", "IrrelevantThirdPartyImagesReliedOnAsEvidence", leaf=True,
            performs=agent("Investigator", True), category="non-functional (privacy)")  # N41, N45
g101 = goal(AchieveGoal, "G-101", "ExamRecordingsDeleted <b>If</b> RetentionExpired <b>And Not</b> ActiveCase",
            leaf=True, performs=agent("CaseManagementSystem"),
            category="non-functional (privacy)")                            # N76

# --- Accommodations (Alan + Jordan) ---
g28 = goal(MaintainGoal, "G-28", "AccommodationRecordMatchesApprovedList", leaf=True,
           performs=agent("ExamPlatform"), category="non-functional (accuracy)")  # A29, A83, J40
g30 = goal(AchieveGoal, "G-30", "ExtendedTimeApplied <b>If</b> ExtraTimeApproved", leaf=True,
           performs=agent("ExamPlatform"))                                  # A78, A83, J9
g31 = goal(AchieveGoal, "G-31", "BreaksScheduled <b>If</b> BreaksApproved", leaf=True,
           performs=agent("ExamPlatform"))                                  # A78, A83
g33 = goal(AchieveGoal, "G-33", "AppliedAccommodationsVerifiedBeforeExam", leaf=True,
           performs=agent("TA", True))                                      # A83
g34 = goal(AchieveGoal, "G-34", "AppliedAccommodationsLogged", leaf=True,
           performs=agent("ExamPlatform"))                                  # A83
g36 = goal(MaintainGoal, "G-36", "ExtendedTimeGranted <b>Only If</b> AccommodationApproved", leaf=True,
           performs=agent("ExamPlatform"), category="non-functional (security/integrity)",
           missing=True)                                                    # H9 converse
g46 = goal(AchieveGoal, "G-46", "AccommodationsConfirmedToStudentBeforeStart", leaf=True,
           performs=agent("ExamPlatform"))                                  # J16, J85
g47 = goal(AchieveGoal, "G-47", "TimerShowsApprovedExtendedTime", leaf=True,
           performs=agent("ExamPlatform"), category="non-functional (accuracy)")  # J16, J18
g49 = goal(AchieveGoal, "G-49", "ReducedDistractionExamModeEnabled", leaf=True,
           performs=agent("ExamPlatform"))                                  # J53
g50 = goal(AchieveGoal, "G-50", "QuietestAvailableSpaceArrangedByStudent", leaf=True,
           performs=agent("Student", True), missing=True)                   # P7 expectation

# --- Taking the exam (Jordan + Alan) ---
g51 = goal(AchieveGoal, "G-51", "ExamConditionsConfirmedOnOnePage <b>Before</b> Start", leaf=True,
           performs=agent("ExamPlatform"))                                  # J32, J36
g53 = goal(AchieveGoal, "G-53", "TimerPausedAndQuestionsHidden <b>While</b> SupportRequestOpen", leaf=True,
           performs=agent("ExamPlatform"))                 # alternative 1; stated in aJ; questions hidden from V1-5
g118 = goal(MaintainGoal, "G-118", "EachPauseRecordedWithStudentReasonAndDuration", leaf=True,
            performs=agent("ExamPlatform"))                                 # aA, aN (decision C3); reason from V1-2
g54 = goal(AchieveGoal, "G-54", "SupportTimeCreditedBack <b>If</b> SupportRequestClosed", leaf=True,
           performs=agent("ExamPlatform"), missing=True)                    # alternative 2
g55 = goal(AchieveGoal, "G-55", "SaveReconnectAndSubmitInstructionsShown", leaf=True,
           performs=agent("ExamPlatform"))                                  # J57, J82
g57 = goal(AchieveGoal, "G-57", "DeviceReadinessCheckedBeforeExam", leaf=True,
           performs=agent("ExamPlatform"))                                  # J21
g58 = soft("Minimize", "G-58", "ProctoringSoftwareLoadOnStudentDevice", leaf=True,
           category="non-functional (performance)")                         # J21, J60
g39 = goal(MaintainGoal, "G-39", "CompletedAnswersSavedContinuously", leaf=True,
           performs=agent("ExamPlatform"), category="non-functional (reliability)")  # A94
# MERGED G-59 (J18, J60, J85) into G-40 (A94)
g40 = goal(AchieveGoal, "G-40", "StudentResumedWithWorkAndRemainingTime <b>If</b> ResumePossible",
           leaf=True, performs=agent("ExamPlatform"))
g41 = goal(AchieveGoal, "G-41", "EquivalentRetakeArranged <b>If Not</b> ResumePossible", leaf=True,
           performs=agent("Instructor", True))                              # A94
g9 = soft("Minimize", "G-9", "ExamRestrictionsBeyondResourcePolicy", leaf=True,
          category="non-functional (usability)")                            # A58

# ============================================================================================
# Intermediate goals
# ============================================================================================
g6 = goal(AchieveGoal, "G-6", "ExamSessionMonitoredForProhibitedResourceUse",
          refinements=[ref([g7, g116, g117, g8], "P6")])                    # A14
g4 = goal(MaintainGoal, "G-4", "OnlyPermittedResourcesUsed",
          refinements=[ref([g5], "H6"), ref([g6, g115], "H6")],             # OR-refinement (C1: second chosen)
          category="non-functional (security/integrity)")                   # A14, A26
g107 = goal(MaintainGoal, "G-107", "ExamTakenByRegisteredStudent",
            refinements=[ref([g108, g109], "P6")], category="non-functional (security)")  # N27
g2 = goal(AvoidGoal, "G-2", "UnauthorizedHelpUsedDuringExam",
          refinements=[ref([g3, g4, g10, g107], "H4")],
          category="non-functional (security/integrity)")                   # A7, A10, A14
g12 = goal(AchieveGoal, "G-12", "RoutineAnswersAutoGraded",
           refinements=[ref([g13, g14], "P1", complete=True)])              # A22
g23 = goal(MaintainGoal, "G-23", "ConsistentFlagReviewAcrossTAs",
           refinements=[ref([g24], "H4")], category="non-functional (consistency)")  # A58
g61 = goal(AvoidGoal, "G-61", "OrdinaryCircumstancesTreatedAsSuspicious",
           refinements=[ref([g62, g63, g21], "P3")])                        # J9, J53, J65, A40
g19 = goal(AchieveGoal, "G-19", "UnusualBehaviorFlaggedWithReviewableEvidence",
           refinements=[ref([g20, g61, g68], "H4")])                        # A14, A40
g64 = goal(AchieveGoal, "G-64", "FlagExplainedByStudent <b>If</b> FlagRaised",
           refinements=[ref([g65, g66], "H5")])                             # J18, J99
g76 = goal(AchieveGoal, "G-76", "BenignExplanationsChecked",
           refinements=[ref([g77, g78, g79], "H4")])                        # N27, N32
g80 = goal(AchieveGoal, "G-80", "ScreeningOutcomeDetermined",
           refinements=[ref([g81, g82], "H10", complete=True)])             # N21, N37, N57
g73 = goal(AchieveGoal, "G-73", "ReportScreened <b>If</b> ReportReceived",
           refinements=[ref([g20, g75, g76, g110, g80], "H4")])             # N21, N23, N37
g86 = goal(AchieveGoal, "G-86", "StudentResponseConsidered <b>Before</b> Decision",
           refinements=[ref([g87, g88, g89], "P4")])                        # N11, N37
g83 = goal(AchieveGoal, "G-83", "DueProcessProvided <b>If</b> FormalCaseOpened",
           refinements=[ref([g84, g85, g86, g90], "H5")],
           category="non-functional (fairness)")                            # N11, N32, N37
g60 = goal(MaintainGoal, "G-60", "FlagsHandledWithContext",
           refinements=[ref([g61, g64, g75, g68], "H4")],
           category="non-functional (fairness)")                            # J65, J71, J99
g94 = goal(MaintainGoal, "G-94", "ChainOfCustodyIntact",
           refinements=[ref([g95, g96, g97], "P5", complete=True)],
           category="non-functional (integrity)")                           # N23, N71
g69 = goal(AvoidGoal, "G-69", "DiagnosisDisclosedToInstructors",
           refinements=[ref([g70, g71], "H11")],
           category="non-functional (confidentiality)")                     # J109-J114
g48 = goal(AchieveGoal, "G-48", "ReducedDistractionSettingProvided",
           refinements=[ref([g49, g50], "P7")])                             # J9, J53
# MERGED G-45 (J9) into G-29 (A78, A83)
g29 = goal(AchieveGoal, "G-29", "ApprovedAccommodationsAppliedAutomatically <b>If</b> AccommodationApproved",
           refinements=[ref([g30, g31], "P3")])
g32 = goal(MaintainGoal, "G-32", "AccommodationApplicationVerifiable",
           refinements=[ref([g33, g34], "H5")])                             # A83
# MERGED G-44 (J9, J12, J16, J40) into G-27 (A29, A33, A78, A83, A88)
g27 = goal(MaintainGoal, "G-27", "ApprovedAccommodationsAppliedAccuratelyAndConfirmedToStudent",
           refinements=[ref([g28, g29, g32, g46, g47, g48], "H4")],
           category="non-functional (accuracy)")
g35 = goal(MaintainGoal, "G-35", "ExamTimingEquitableAcrossStudents",
           refinements=[ref([g29, g36], "H9")], category="non-functional (fairness)")  # A7
g52 = goal(AchieveGoal, "G-52", "HelpObtainedWithoutLosingExamTime <b>If</b> StudentRequestsSupport",
           refinements=[ref([g53, g118], "H6"), ref([g54], "H6")])          # J9, J18, J85 (OR, C3: first chosen)
g43 = soft("Reduce", "G-43", "ExamStressFromUncertainty",
           refinements=[ref([g27, g51, g52, g55], "H4")],
           category="non-functional (usability)")                           # J80, J104
g38 = goal(AchieveGoal, "G-38", "ExamContinuedFairly <b>If</b> SessionDisrupted",
           refinements=[ref([g39, g40, g41], "H10")])                       # A94, A96, J60
g56 = goal(MaintainGoal, "G-56", "ExamSessionReliableOnStudentDevice",
           refinements=[ref([g57, g58], "H4")],
           category="non-functional (availability)")                        # J21, J60, J85
g37 = goal(MaintainGoal, "G-37", "StudentExamWorkAndTimeIntact",
           refinements=[ref([g38, g56], "H8")],
           category="non-functional (reliability)")                         # A94, A96, J80

# ============================================================================================
# High-level goals (roots)
# ============================================================================================
# MERGED G-42 (J9, J80) into G-1 (A7)
g1 = soft("Maximize", "G-1", "ExamsAccuratelyMeasureEachStudentsOwnKnowledge",
          refinements=[ref([g2, g9, g35, g37, g43, g60], "H12")])
# MERGED G-106 (N57, N68) into G-11 (A52, A68, A75)
g11 = soft("Reduce", "G-11", "ExamAndIntegrityCaseAdministrativeWorkload",
           refinements=[ref([g12, g15, g16, g17, g103], "H4")])
# MERGED G-72 (N6, N9, N37) into G-18 (A36, A38, A40, A52). Milestones from flag to appeal.
g18 = goal(AchieveGoal, "G-18", "SuspectedMisconductResolvedFairlyAndConsistently",
           refinements=[ref([g19, g22, g111, g112, g64, g25, g73, g83, g91], "P1")])
# MERGED G-105 (N6, N53, N68) into G-26 (A40, A75, A88)
g26 = soft("Minimize", "G-26", "HonestStudentsWronglyFlaggedOrInvestigated",
           refinements=[ref([g20, g61, g75, g76], "H7")])
g92 = goal(MaintainGoal, "G-92", "CompleteEvidentiaryRecordAvailable",
           refinements=[ref([g17, g94], "P5", complete=True)],
           category="non-functional (integrity)")                           # N6, N15, N18
g98 = goal(MaintainGoal, "G-98", "StudentAndCaseDataPrivacyProtected",
           refinements=[ref([g69, g99, g100, g101], "H3")],
           category="non-functional (privacy)")                             # J109, N15, N45, N76
g102 = goal(MaintainGoal, "G-102", "OutcomesConsistentAcrossTAsCoursesAndGroups",
            refinements=[ref([g23, g103, g104], "H5")],
            category="non-functional (consistency)")                        # A58, N32, N57

# ============================================================================================
# Obstacles and conflicts
# ============================================================================================
# Merged obstacle: A94 (connection or system fails) + J21/J60 (exam freezes on an old laptop)
o1 = Obstacle("ConnectionDeviceOrSystemFailureDuringExam")

CONFLICTS = {
    # --- Conflicts involving sprint goals (decision in docs/goal-model.md section 4) ---
    # C1 (Alan vs Alan, A58): blocking resources makes the open-note exam too restrictive.
    # Decision: compromise, fullscreen only (G-115).
    "C1": (g5, g9),
    # C2 (Alan vs Jordan, A14 vs J75): session monitoring vs. exam stress.
    # Decision: compromise, no camera; page leaves, pastes and timing only (G-7, G-116, G-117),
    # disclosed on the start page (G-51).
    "C2": (g6, g43),
    # C3 (Jordan vs Alan): pausing the timer during support opens an unmonitored window.
    # Decision: prioritize G-53; questions are hidden while help is open, and every pause is
    # recorded with the student's reason (G-118). Maximum pause length is open for Alan.
    "C3": (g53, g2),
    # C4 (Jordan vs Alan, found in both members' models): the student wants to explain a flag
    # first; the instructor wants to review it first.
    # Decision: prioritize G-111; the student must be asked before any referral (G-65, G-66).
    "C4": (g64, g111),
    # --- Conflicts outside the sprint (preserved, unresolved) ---
    # C5 (Jordan vs Nkechi, J99 vs N21/N37): explain a flag before a formal case is opened.
    # HW2 proposal G-110 stays in the model; needs the integrity office to confirm.
    "C5": (g64, g81),
    # C6 (Alan vs Nkechi, A36/A38 vs N48): who decides on a case. Ashley's model reads this as
    # two stages (instructor screens, office decides). Needs stakeholder clarification.
    "C6": (g25, g90),
    # C7 (Nkechi vs Nkechi, N73 vs N76): delete recordings after retention vs. keep the full
    # record for appeals. Needs a policy decision.
    "C7": (g101, g92),
}

ROOTS = [g1, g11, g18, g26, g92, g98, g102]
LINKS = [ObstructionLink(g37, o1), ResolutionLink(g38, o1)] + \
        [ConflictLink(a, b) for a, b in CONFLICTS.values()]

if __name__ == "__main__":
    output = render(ROOTS, LINKS)
    print(output)
    print(generate_pako_link(output, "edit",
                             config={"theme": "default",
                                     "themeVariables": {"fontFamily": "Segoe UI Symbol, Helvetica"}}))
    print("\nSprint goals:", len(SPRINT))
    print("\nGoals:", len(GOALS), "| Merged away:", sum(len(v) for v in MERGED.values()),
          "| Not in transcripts:", sorted(MISSING, key=lambda x: int(x[2:])))
