"""
17-626 HW2 - Goal model extracted from the interview with Dr. Nkechi Okoye (oversees the
university academic integrity office). Project: Online Exam Delivery and Proctoring.

Conventions (same as all four models)
- Goal IDs are unique across all transcripts (Alan G-1..G-41, Jordan G-42..G-71,
  Nkechi G-72..G-109); the rendered name is Keyword[G-n: Name].
- SOURCE comments cite transcript turns as "T<n>" = line number in transcript_Nkechi.csv.
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
# SOURCE T29, T53, T66: a flag links "the event to its timestamp, source data, and surrounding context"
g74 = goal(AchieveGoal, "G-74", "FlagLinkedToTimestampSourceAndContext", leaf=True,
           performs=by("ProctoringMonitor", "AttachProvenanceToFlag"))
# SOURCE T21, T29, T32: "Automated flags are treated as triage indicators only, not as proof"
g75 = goal(AvoidGoal, "G-75", "AutomatedFlagTreatedAsMisconductFinding", leaf=True,
           performs=by("Investigator", "TriageFlagForHumanReview", environment=True),
           category="non-functional (fairness)")
# SOURCE T27, T32: compare against "any documented accommodations"
g77 = goal(AchieveGoal, "G-77", "FlagComparedAgainstDocumentedAccommodations", leaf=True,
           performs=by("Investigator", "CheckAccommodationContext", environment=True))
# SOURCE T32, T48: "legitimate technical ... explanations"; consult technical staff
g78 = goal(AchieveGoal, "G-78", "FlagComparedAgainstTechnicalEvents", leaf=True,
           performs=by("Investigator", "CheckSessionAndDeviceMetadata", environment=True))
# SOURCE T41, T45, T66: "separates the student's exam conduct from incidental household activity"
g79 = goal(AchieveGoal, "G-79", "EnvironmentalEventsSeparatedFromExamConduct", leaf=True,
           performs=by("Investigator", "ClassifyEnvironmentalEvents", environment=True))
# SOURCE T21, T37: "decision about whether to open a formal case"
g81 = goal(AchieveGoal, "G-81", "FormalCaseOpened <b>If</b> EvidenceMeetsPreliminaryThreshold",
           leaf=True, performs=by("Investigator", "OpenFormalCase", environment=True))
# SOURCE T6, T57: "avoid pursuing unfounded cases"; cases "dismissed, withdrawn, or found unsupported"
g82 = goal(AchieveGoal, "G-82", "ReportDismissed <b>If Not</b> EvidenceMeetsPreliminaryThreshold",
           leaf=True, performs=by("Investigator", "DismissReport", environment=True))
# SOURCE T11, T37: "providing notice of the allegation"
g84 = goal(AchieveGoal, "G-84", "StudentNotifiedOfAllegation", leaf=True,
           performs=by("CaseManagementSystem", "SendAllegationNotice"))
# SOURCE T11, T15, T37: "a student-facing view of the allegation and supporting material"
g85 = goal(AchieveGoal, "G-85", "EvidenceMadeAvailableToStudent", leaf=True,
           performs=by("CaseManagementSystem", "PublishStudentCaseView"))
# SOURCE T37: "allow a response within the specified period"
g87 = goal(AchieveGoal, "G-87", "ResponseRecorded <b>If</b> SubmittedWithinResponsePeriod", leaf=True,
           performs=by("CaseManagementSystem", "RecordStudentResponse"))
# SOURCE T11, T32: "a meaningful opportunity to review the evidence and submit a response"
g88 = goal(AchieveGoal, "G-88", "ResponseSubmittedByStudent", leaf=True,
           performs=by("Student", "SubmitResponse", environment=True))
# SOURCE T11: "... before an adjudicative decision is made"
g89 = goal(MaintainGoal, "G-89", "DecisionWithheld <b>Unless</b> ResponsePeriodEnded", leaf=True,
           performs=by("CaseManagementSystem", "LockDecisionUntilPeriodEnds"))
# SOURCE T11, T37, T48, T59: an authorized reviewer assesses the complete record; reasons documented
g90 = goal(AchieveGoal, "G-90", "DecisionMadeOnFullRecordWithReasons", leaf=True,
           performs=by("AuthorizedReviewer", "DecideAndDocumentReasons", environment=True))
# SOURCE T37: "Any appeal is handled with the same record"
g91 = goal(AchieveGoal, "G-91", "AppealReviewedOnSameRecord <b>If</b> AppealFiled", leaf=True,
           performs=by("AppealReviewer", "ReviewAppeal", environment=True))
# SOURCE T15, T53, T73: "one secure case record with a clear chronology"
g93 = goal(MaintainGoal, "G-93", "EvidenceChronologyAndDecisionsKeptInOneCaseRecord", leaf=True,
           performs=by("CaseManagementSystem", "StoreCaseRecord"))
# SOURCE T23: "identifiable provenance, preserved metadata"
g95 = goal(MaintainGoal, "G-95", "EvidenceMetadataPreserved", leaf=True,
           performs=by("CaseManagementSystem", "PreserveEvidenceMetadata"),
           category="non-functional (integrity)")
# SOURCE T71, T73: "who accessed, added, changed, or relied on each piece of material"
g96 = goal(MaintainGoal, "G-96", "AccessAndChangesAuditLogged", leaf=True,
           performs=by("CaseManagementSystem", "WriteAuditLog"),
           category="non-functional (accountability)")
# SOURCE T71: "timestamps that cannot be casually altered"
g97 = goal(MaintainGoal, "G-97", "AuditTimestampsTamperResistant", leaf=True,
           performs=by("CaseManagementSystem", "SealAuditEntries"),
           category="non-functional (integrity)")
# SOURCE T15, T32: "controlled access"; "restricted to authorized personnel"
g99 = goal(AvoidGoal, "G-99", "UnauthorizedCaseRecordAccess", leaf=True,
           performs=by("CaseManagementSystem", "EnforceRoleBasedAccess"),
           category="non-functional (confidentiality)")
# SOURCE T41, T45: "unnecessary images of family members are handled as a privacy matter"
g100 = goal(AvoidGoal, "G-100", "IrrelevantThirdPartyImagesReliedOnAsEvidence", leaf=True,
            performs=by("Investigator", "RedactThirdPartyImages", environment=True),
            category="non-functional (privacy)")
# SOURCE T76: "deleted after the approved retention period unless an active case requires preservation"
g101 = goal(AchieveGoal, "G-101", "ExamRecordingsDeleted <b>If</b> RetentionExpired <b>And Not</b> ActiveCase",
            leaf=True, performs=by("CaseManagementSystem", "PurgeExpiredRecordings"),
            category="non-functional (privacy)")
# SOURCE T15: "reliable reporting on case outcomes and recurring problem areas"
g103 = goal(AchieveGoal, "G-103", "CaseOutcomeReportsGenerated", leaf=True,
            performs=by("CaseManagementSystem", "GenerateOutcomeReports"))
# SOURCE T32: "We also monitor outcomes for inconsistencies across courses and student groups"
g104 = goal(AchieveGoal, "G-104", "InconsistentOutcomePatternsReviewed", leaf=True,
            performs=by("IntegrityOffice", "ReviewOutcomePatterns", environment=True))
# SOURCE T27, T29: identity verification; "a face-identity mismatch"
g108 = goal(AchieveGoal, "G-108", "FaceIdentityMatchChecked", leaf=True,
            performs=by("ProctoringMonitor", "CompareFaceToRoster"))
# NOT IN TRANSCRIPT: accuracy goal introduced by the unmonitorability pattern (P6)
g109 = goal(MaintainGoal, "G-109", "FaceMatchAccurateAcrossStudentGroups", leaf=True,
            performs=by("ProctoringMonitor", "ValidateMatchAccuracy"),
            category="non-functional (accuracy)", missing=True)

# --------------------------------------------------------------------------------------------
# Intermediate goals
# --------------------------------------------------------------------------------------------
# SOURCE T27, T32: check benign explanations (accommodations, technical, environmental)
g76 = goal(AchieveGoal, "G-76", "BenignExplanationsChecked",
           refinements=[ref([g77, g78, g79], "H4")])
# SOURCE T21, T37, T57: screening ends either in a formal case or a dismissal (H10 complement)
g80 = goal(AchieveGoal, "G-80", "ScreeningOutcomeDetermined",
           refinements=[ref([g81, g82], "H10", complete=True)])
# SOURCE T21, T23, T37: "intake ... an initial screening for a specific and sufficiently supported concern"
g73 = goal(AchieveGoal, "G-73", "ReportScreened <b>If</b> ReportReceived",
           refinements=[ref([g74, g75, g76, g80], "H4")])
# SOURCE T11, T37: guard = a response was submitted within the period (guard introduction)
g86 = goal(AchieveGoal, "G-86", "StudentResponseConsidered <b>Before</b> Decision",
           refinements=[ref([g87, g88, g89], "P4")])
# SOURCE T11, T32, T37: notice, evidence access, response, impartial decision -> split by agent
g83 = goal(AchieveGoal, "G-83", "DueProcessProvided <b>If</b> FormalCaseOpened",
           refinements=[ref([g84, g85, g86, g90], "H5")], category="non-functional (fairness)")
# SOURCE T23: provenance, metadata, chain of custody (conjoined conditions -> divide and conquer)
g94 = goal(MaintainGoal, "G-94", "ChainOfCustodyIntact",
           refinements=[ref([g95, g96, g97], "P5", complete=True)],
           category="non-functional (integrity)")

# --------------------------------------------------------------------------------------------
# High-level goals (roots)
# --------------------------------------------------------------------------------------------
# SOURCE T6, T9, T37: "fair, consistent outcomes"; intake -> screening -> case -> decision -> appeal
g72 = goal(AchieveGoal, "G-72", "MisconductCasesResolvedFairlyAndConsistently",
           refinements=[ref([g73, g83, g91], "P1")])
# SOURCE T6, T15, T18: "evidence that can withstand an appeal"; complete record kept together
g92 = goal(MaintainGoal, "G-92", "CompleteEvidentiaryRecordAvailable",
           refinements=[ref([g93, g94], "P5", complete=True)],
           category="non-functional (integrity)")
# SOURCE T15, T32, T45, T57, T76: privacy complaints, controlled access, retention
# Found by instantiating the confidentiality/privacy goal category (H3)
g98 = goal(MaintainGoal, "G-98", "CaseDataPrivacyProtected",
           refinements=[ref([g99, g100, g101], "H3")], category="non-functional (privacy)")
# SOURCE T32, T57: "monitor outcomes for inconsistencies"; outcomes resolved consistently
g102 = goal(MaintainGoal, "G-102", "OutcomesConsistentAcrossCoursesAndGroups",
            refinements=[ref([g103, g104], "H5")], category="non-functional (consistency)")
# SOURCE T6, T53, T68: "reduce unfounded cases"; poorly contextualized alerts create unfairness
g105 = soft("Reduce", "G-105", "UnfoundedCasesOpened",
            refinements=[ref([g74, g75, g76], "H8")])
# SOURCE T57, T68: "reduce administrative effort"; what the office (agent) wishes for (H7)
g106 = soft("Reduce", "G-106", "IntegrityOfficeAdministrativeEffort",
            refinements=[ref([g93, g103], "H7")])
# SOURCE T27, T29: identity verification. The system cannot monitor who is really taking the
# exam, so a monitorable counterpart (face match) plus an accuracy goal is introduced (P6)
g107 = goal(MaintainGoal, "G-107", "ExamTakenByRegisteredStudent",
            refinements=[ref([g108, g109], "P6")], category="non-functional (security)")

ROOTS = [g72, g92, g98, g102, g105, g106, g107]
LINKS = [
    # Intra-stakeholder conflict (T73 vs T76): deleting recordings after the retention period
    # vs. keeping the complete record for an appeal that "occurs months after the examination".
    # Boundary condition: an appeal is filed after the retention period has expired.
    ConflictLink(g101, g92),
]

if __name__ == "__main__":
    output = render(ROOTS, LINKS)
    print(output)
    print(generate_pako_link(output, "edit",
                             config={"theme": "default",
                                     "themeVariables": {"fontFamily": "Segoe UI Symbol, Helvetica"}}))
    print("\nGoals:", len(GOALS), "| Not in transcript:", sorted(MISSING, key=lambda x: int(x[2:])))
