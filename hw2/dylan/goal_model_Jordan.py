"""
17-626 HW2 - Goal model extracted from the interview with Jordan Alvarez (student with approved
testing accommodations: extra time and a reduced-distraction setting). Project: Online Exam
Delivery and Proctoring.

Conventions (same as all four models)
- Goal IDs are unique across all transcripts (Alan G-1..G-41, Jordan G-42..G-71,
  Nkechi G-72..G-109); the rendered name is Keyword[G-n: Name].
- SOURCE comments cite transcript turns as "T<n>" = line number in transcript_Jordan.csv.
- Goals not stated in the transcript are listed in MISSING and highlighted YELLOW.
- Each Refinement carries one heuristic (H3-H12) or pattern (P1-P7) code from Appendix A.
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
# Leaf goals
# --------------------------------------------------------------------------------------------
# SOURCE T9: "approved extra time and reduced-distraction setting are applied automatically"
g45 = goal(AchieveGoal, "G-45", "ApprovedAccommodationsAppliedAutomatically", leaf=True,
           performs=by("ExamPlatform", "ApplyAccommodationsToExam"))
# SOURCE T16, T85: "I'd want the accommodations confirmed before I begin"
g46 = goal(AchieveGoal, "G-46", "AccommodationsConfirmedToStudentBeforeStart", leaf=True,
           performs=by("ExamPlatform", "DisplayAccommodationConfirmation"))
# SOURCE T16, T18: "a clear timer showing the extra time"; timer not matching approved time
g47 = goal(AchieveGoal, "G-47", "TimerShowsApprovedExtendedTime", leaf=True,
           performs=by("ExamPlatform", "DisplayAdjustedTimer"),
           category="non-functional (accuracy)")
# SOURCE T53: "a reduced-distraction option that works even when I can't get a private room"
g49 = goal(AchieveGoal, "G-49", "ReducedDistractionExamModeEnabled", leaf=True,
           performs=by("ExamPlatform", "EnableReducedDistractionMode"))
# NOT IN TRANSCRIPT: expectation on the student introduced by the uncontrollability pattern (P7)
g50 = goal(AchieveGoal, "G-50", "QuietestAvailableSpaceArrangedByStudent", leaf=True,
           performs=by("Student", "ChooseExamLocation", environment=True), missing=True)
# SOURCE T32, T36: "One clear page would show my approved time, the exam rules, and the
# reduced-distraction arrangement before I start" (information goal)
g51 = goal(AchieveGoal, "G-51", "ExamRulesTimeAndSettingShownOnOnePage", leaf=True,
           performs=by("ExamPlatform", "ShowExamSummaryPage"))
# NOT IN TRANSCRIPT: alternative design 1 for G-52 (pause the clock during support)
g53 = goal(AchieveGoal, "G-53", "TimerPaused <b>While</b> SupportRequestOpen", leaf=True,
           performs=by("ExamPlatform", "PauseTimer"), missing=True)
# NOT IN TRANSCRIPT: alternative design 2 for G-52 (credit lost time back afterwards)
g54 = goal(AchieveGoal, "G-54", "SupportTimeCreditedBack <b>If</b> SupportRequestClosed", leaf=True,
           performs=by("ExamPlatform", "CreditSupportTime"), missing=True)
# SOURCE T57, T82: "simple instructions for saving answers, reconnecting after a problem, and submitting"
g55 = goal(AchieveGoal, "G-55", "SaveReconnectAndSubmitInstructionsShown", leaf=True,
           performs=by("ExamPlatform", "DisplayRecoveryInstructions"))
# SOURCE T21: "I tested the webcam and noticed my old laptop was running slowly"
g57 = goal(AchieveGoal, "G-57", "DeviceReadinessCheckedBeforeExam", leaf=True,
           performs=by("ExamPlatform", "RunSystemCheck"))
# SOURCE T21, T60: "the proctoring software made my old laptop slow"
g58 = soft("Minimize", "G-58", "ProctoringSoftwareLoadOnStudentDevice", leaf=True,
           category="non-functional (performance)")
# SOURCE T18, T60, T85: "clear recovery if it freezes"; lost time restored
g59 = goal(AchieveGoal, "G-59", "WorkAndTimeRestored <b>If</b> ExamFreezes", leaf=True,
           performs=by("ExamPlatform", "RestoreSessionAndTimer"))
# SOURCE T9, T12, T75: "looking away and fidgeting while thinking ... that's normal for me"
g62 = goal(AvoidGoal, "G-62", "ThinkingBehaviorFlaggedAsMisconduct", leaf=True,
           performs=by("ProctoringMonitor", "IgnoreGazeAndFidgetEvents"))
# SOURCE T50, T53, T57: three roommates; "roommate movement or noise isn't treated as misconduct"
g63 = goal(AvoidGoal, "G-63", "UnavoidableHouseholdEventsFlaggedAsMisconduct", leaf=True,
           performs=by("ProctoringMonitor", "ClassifyEnvironmentalEvents"))
# SOURCE T18, T99: "I should be able to see what was flagged"
g65 = goal(AchieveGoal, "G-65", "FlagDetailsShownToStudent", leaf=True,
           performs=by("ExamPlatform", "ShowFlagDetails"))
# SOURCE T18, T85, T99: "and explain it before a person decides it might be misconduct"
g66 = goal(AchieveGoal, "G-66", "StudentExplanationSubmitted <b>If</b> FlagShown", leaf=True,
           performs=by("Student", "SubmitExplanation", environment=True))
# SOURCE T65, T85: "I'd want a human to review any flag before it's treated as a possible violation"
g67 = goal(AchieveGoal, "G-67", "FlagHumanReviewed <b>Before</b> TreatedAsPossibleViolation", leaf=True,
           performs=by("Reviewer", "ReviewFlag", environment=True))
# SOURCE T16: "any concern handled without interrupting or penalizing me while I'm taking the exam"
g68 = goal(AvoidGoal, "G-68", "StudentInterruptedDuringExamByFlag", leaf=True,
           performs=by("ProctoringMonitor", "DeferFlagHandlingUntilSubmission"))
# SOURCE T109, T114: "the instructor sees only the accommodation they need to apply"
g70 = goal(MaintainGoal, "G-70", "InstructorViewLimitedToApprovedAccommodation", leaf=True,
           performs=by("ExamPlatform", "FilterAccommodationView"),
           category="non-functional (confidentiality)")
# SOURCE T109, T114: "My medical information should stay restricted to disability services"
g71 = goal(MaintainGoal, "G-71", "MedicalDetailsKeptWithinDisabilityServices", leaf=True,
           performs=by("DisabilityServices", "WithholdDiagnosisFromExamSystem", environment=True),
           category="non-functional (confidentiality)")

# --------------------------------------------------------------------------------------------
# Intermediate goals
# --------------------------------------------------------------------------------------------
# SOURCE T9, T53: the platform cannot control the student's room (roommates, noise), so the
# uncontrollable condition is replaced by a controllable exam mode plus an expectation (P7)
g48 = goal(AchieveGoal, "G-48", "ReducedDistractionSettingProvided",
           refinements=[ref([g49, g50], "P7")])
# SOURCE T9, T12, T16, T40: extra time not applied at first; had to check it carried over
g44 = goal(MaintainGoal, "G-44", "ApprovedAccommodationsAppliedAccurately",
           refinements=[ref([g45, g46, g47, g48], "H4")], category="non-functional (accuracy)")
# SOURCE T9, T12, T18, T85: "a support option that doesn't make me lose exam time"
# OR-refinement: two alternative designs, compared by their pros and cons (H6)
g52 = goal(AchieveGoal, "G-52", "HelpObtainedWithoutLosingExamTime <b>If</b> StudentRequestsSupport",
           refinements=[ref([g53], "H6"), ref([g54], "H6")])
# SOURCE T21, T24, T60, T85: "reliable software"; the exam froze on an old laptop
g56 = goal(MaintainGoal, "G-56", "ExamSessionReliableOnStudentDevice",
           refinements=[ref([g57, g58, g59], "H8")], category="non-functional (availability)")
# SOURCE T9, T53, T65: ordinary behavior or surroundings must not count against her (two cases)
g61 = goal(AvoidGoal, "G-61", "OrdinaryBehaviorOrSurroundingsTreatedAsSuspicious",
           refinements=[ref([g62, g63], "P3")])
# SOURCE T18, T99: see the flag (system) and explain it (student) -> split by agent
g64 = goal(AchieveGoal, "G-64", "FlagExplainedByStudent <b>If</b> FlagRaised",
           refinements=[ref([g65, g66], "H5")])
# SOURCE T65, T71, T99: vague term "handle flags with context", refined with my interpretation
g60 = goal(MaintainGoal, "G-60", "FlagsHandledWithContext",
           refinements=[ref([g61, g64, g67, g68], "H4")], category="non-functional (fairness)")
# SOURCE T80, T104: "reducing the stress caused by uncertainty"
g43 = soft("Reduce", "G-43", "ExamStressFromUncertainty",
           refinements=[ref([g44, g51, g52, g55], "H4")], category="non-functional (usability)")

# --------------------------------------------------------------------------------------------
# High-level goals (roots)
# --------------------------------------------------------------------------------------------
# SOURCE T9, T80: "what matters most to you when ... trying to demonstrate what you've learned"
# Refined by asking what Jordan (as an agent) wishes the system to do (H7)
g42 = soft("Maximize", "G-42", "StudentAbleToDemonstrateKnowledge",
           refinements=[ref([g43, g56, g60], "H7")])
# SOURCE T109, T112, T114: privacy; instantiating the confidentiality goal category (H3)
g69 = goal(AvoidGoal, "G-69", "DiagnosisDisclosedToInstructors",
           refinements=[ref([g70, g71], "H3")], category="non-functional (confidentiality)")

# --------------------------------------------------------------------------------------------
# Obstacles
# --------------------------------------------------------------------------------------------
# SOURCE T21, T60: "the exam froze while I was in the middle of a question"
o2 = Obstacle("ExamFreezesOnStudentDevice")

ROOTS = [g42, g69]
LINKS = [
    ObstructionLink(g56, o2),
    ResolutionLink(g59, o2),
]

if __name__ == "__main__":
    output = render(ROOTS, LINKS)
    print(output)
    print(generate_pako_link(output, "edit",
                             config={"theme": "default",
                                     "themeVariables": {"fontFamily": "Segoe UI Symbol, Helvetica"}}))
    print("\nGoals:", len(GOALS), "| Not in transcript:", sorted(MISSING, key=lambda x: int(x[2:])))
