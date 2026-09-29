# Interview Coach

A learning agent that helps a candidate prepare for engineering interviews: it teaches from study material and runs mock interviews that probe until the answer is deep enough.

## Language

**Candidate**:
The person preparing for interviews who studies and practises with the coach.
_Avoid_: user, student, learner

**Study mode**:
The mode where the candidate asks about interview topics and gets answers grounded in the study material, with citations and quizzes.
_Avoid_: study buddy, Q&A mode

**Interview mode**:
The mode where the coach runs a mock interview, asks follow-up probes and scores the candidate's answers against a rubric after the session.
_Avoid_: mock, interview coach mode

**Probe**:
A follow-up question in interview mode that pushes on a gap in the candidate's last answer, repeated until the answer is deep enough or the candidate is stuck.
_Avoid_: squeeze, drill-down

**Study material**:
The third-party documents the coach teaches and cites from, downloaded at setup from the sources list and never committed.
_Avoid_: corpus, knowledge base, docs

**Sources list**:
The committed manifest naming each piece of study material, where to download it, its licence, and whether it may be used only locally.
_Avoid_: manifest, source config

**Evaluation set**:
The frozen, committed set of questions with the study-material chunks that answer them, used to measure search and answer quality.
_Avoid_: test set, golden set, benchmark

**Grader**:
A model call that decides pass or fail for one check on one answer, such as whether a claim is supported by the cited passages or whether an interview answer covers a rubric point.
_Avoid_: judge, evaluator, scorer

**Label**:
The owner's own verdict on an example (pass or fail for a check, or which passages answer a question), used as ground truth for measuring graders and search.
_Avoid_: annotation, human grade, gold

## Interview mode

**Track**:
The kind of interview the candidate chooses to practise: system design, AI engineering, .NET or Python.
_Avoid_: category, topic, interview type

**Question card**:
One interview question with what a good answer covers at each level and the probes to ask, drafted from the study material and edited by the owner.
_Avoid_: prompt, scenario, question template

**Rubric check**:
One yes-or-no point a good answer must cover for one skill, graded with a quote from the candidate's own words.
_Avoid_: criterion, rubric item, score

**Level**:
The seniority an answer is judged against: mid, senior or staff.
_Avoid_: grade, band, tier

**Hint ladder**:
The sequence of ever more direct hints a stuck candidate can ask for, ending in the answer itself; every hint used caps the score for that skill.
_Avoid_: help, clue

**Debrief**:
The feedback given after an interview session ends: the verdict per rubric check, the reference answer and the gaps found.
_Avoid_: feedback, report, review

**Simulated candidate**:
An automated stand-in for the candidate that answers from a bank of prepared answers of known quality, used to test interview mode without a person.
_Avoid_: fake user, persona, bot

## Memory

**Candidate model**:
The plain-code record of what the candidate knows per topic: mastery, when the topic is next due for review, and current weak spots, updated from grader verdicts.
_Avoid_: learner model, user profile, memory

**Weak spot**:
A topic or rubric check the candidate recently failed or needed hints for, which steers what to study and ask next.
_Avoid_: gap, weakness, blind spot

**Extracted memory**:
A fact the model pulls out of a finished session, such as a misconception or a preference, stored with the session and turn it came from and never shown to the grader.
_Avoid_: note, insight, fact

