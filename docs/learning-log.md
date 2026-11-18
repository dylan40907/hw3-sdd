# Learning Log

## 1. Sprint Planning and Requirements Selection

Here's some info about v1 you might need to write this Ashley you can delete it: the handout says the goals we left out and why have to be in this section. The list is in section 0 of docs/goal-model.md so just explain it in your own words. The IDs come from my HW2 model since it had a little more detail and G-111 to G-118 are new. G-112, G-115 and G-116 are not from any interview so they're yellow. C5 to C7 are left unresolved on purpose because the handout says not to remove conflicts. In clarify I also decided some things you might want to mention like 3 or more students make a group and each student in a group gets their own flag.

## 2. Prototype Evaluation

I evaluated V1 by using it as the student, the instructor, and the integrity office and by reading the code against the spec. The results are in the traceability matrix in [docs/traceability.md](traceability.md). All 76 tests passed but that only shows the code does what the spec says. It doesn't show the spec is what the stakeholders needed so walking through the app mattered more than the tests.

Before implementing I ran Spec Kit's analyze step. It ended up finding two problems in the plan. One was that the pre-filled students in an answer group would never get a flag and the other was that groups would never be made if a student closed the tab before the end time. We fixed both before building because otherwise V1 would have had real implementation defects.

I found five issues. All five are requirements issues and I found no implementation defects. I've listed them below:

**V1-1: one action makes several flags.** If a student left the page and then submitted an answer the instructor got two flags. If the answer was in a group they then got a third one. Each one had to be reviewed and asked about and referred separately. This is exactly what REQ-12 said ("every recorded signal becomes a flag") so it's a requirements issue. It shows we wrote the requirement around what the system detects and not around how Alan works. Alan wants less review work (G-11) and Okoye wants one case record per student (D-Okoye L53). The spec needed to change to one flag per student per exam that collects all their signals.

**V1-2: the help request has no reason.** The student could open help but there was no reason field and nobody ended up getting the request. Every pause was saved with the same label so the instructor couldn't tell a technical problem from anything else. A student could also leave help open as long as they wanted which is the risk behind conflict C3. The spec never said the student gives a reason so this is a requirements issue. It needed a spec change so the student picks or types a reason. It also needs clarification from Alan since he's the only one who can say if a pause seems to be too long.

**V1-3: a fast answer after a dropped connection still gets flagged.** The page leave was marked "connection lost" correctly. But if the student answered within 30 seconds of coming back it still counted as a fast answer. That treats an outage like something suspicious which Alan specifically said to avoid (D-Alan L40, G-21). The spec had an exception for the page leave but not for the fast answer. The spec needed to change so there's no fast answer signal after a connection loss or a help request.

**V1-4: any shared wrong answer makes a group.** Three students with the same easy mistake get grouped even if honest students make that mistake all the time. Alan's example was the same wrong answer "to four decimal places" (D-Alan L10) so he means an unusual mistake. Our spec didn't define unusual because we didn't really know how or what that meant. This needs clarification from Alan and isn't something we can fix ourselves so we kept it open.

**V1-5: the agent added things we didn't specify.** V1 hides the questions while help is open and asks for a confirmation before Finish exam. Neither of these features is in the spec we made. Hiding the questions is probably an actual good answer to C3 but we didn't decide to make it ourselves, the agent did. Since this was missing from the spec it's a requirements issue. The fix was to put it in the spec so it's a decision we confirmed and can trace later.

Overall the agent built what we wrote but sometimes too literally. The problems came from things we wrote that were too open ended (V1-1) or left out (V1-2 and V1-3). Other things we couldn't decide without more of Alan's input (V1-4) or didn't decide at all (V1-5).

## 3. Revisions and Learning

### Reflection

**Which decisions required your judgment rather than relying solely on AI?**

Dylan: The agent asked questions during clarify and I answered them on my own. For example it asked if students with the same wrong answer get one shared flag or one flag each. That decision would decide who the instructor contacts so it needed me because I actually read the interviews. I also had to decide which findings were implementation defects and which were requirements issues. The agent told me the code matched the spec but not that the spec was wrong for Alan. V1-5 is the clearest case of this here. The agent added behavior on its own and I had to notice we never actually decided on that.

Ashley:

**How did prototyping change your understanding of stakeholder needs?**

Dylan: When we wrote "every signal becomes a flag" it looked ok to start. However clicking through it as the instructor it ended up as a pile of flags for one student. That made me realize Alan cares about how many decisions he has to make and not how many things the system detects. The help request was similar as Jordan's need sounded simple (which was don't lose time) but once it actually existed you could see it needed a reason and a limit to work for Alan too.

Ashley:

**How did spec-driven development help maintain consistency between the requirements and implementation?**

Dylan: Every FR in the spec points back to a REQ and a goal. Every task names its FR and the tests are named after the FR they check so the traceability matrix was mostly just following IDs. The analyze step also compared the spec and plan and tasks before any code existed and actually caught two gaps. The downside is it's only as consistent as the spec so a missing requirement would keep being missing all the way into the code.

Ashley:

**What evidence from your work would you present to management to demonstrate the value you contributed beyond AI-generated specifications and code?**

Dylan: I would present the V1 evaluation. Every test passed and there were no implementation defects but there were still five requirements issues that we had to find by checking the prototype against the interview transcripts. I'd also show the clarify answers and the two analyze fixes since those were decisions the agent needed us to make. Also the traceability matrix which shows each feature traces back to an actual stakeholder quote.

Ashley:
