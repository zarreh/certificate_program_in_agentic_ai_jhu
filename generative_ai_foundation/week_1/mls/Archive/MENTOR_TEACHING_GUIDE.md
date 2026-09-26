# Clinic Tracker MLS — Complete Mentor Pack

**Session:** Generative AI Foundations, Week 1 Mentor-Led Session
**Topic:** AI-assisted coding with Codex in VS Code — human judgement, not syntax
**Build:** Clinic Spend Tracker, six pieces, five passes of the same loop
**Duration:** 150 minutes

> **Rule zero, said out loud at the start and again at the end: synthetic data only.
> Never real patient information — not in a prompt, not in a file, not in a screenshot.**

---

## Contents

- [Part 0 — The business problem](#part-0--the-business-problem)
- [Part A — Your prep, before the session](#part-a--your-prep-before-the-session)
- [Part B — Concept cheat sheet](#part-b--concept-cheat-sheet)
- [Part C — Minute-by-minute run of show](#part-c--minute-by-minute-run-of-show)
- [Part D — The complete prompt script (all five passes → `solution_pack`)](#part-d--the-complete-prompt-script)
- [Part E — Drift, failure, and troubleshooting](#part-e--drift-failure-and-troubleshooting)
- [Part F — What to hand out, and when](#part-f--what-to-hand-out-and-when)
- [Appendix — Session-day quick card](#appendix--session-day-quick-card)

**Every prompt in Part D was run against `solution_pack` on this machine. Every "expected
output" block below is copied verbatim from a real run, not typed from memory.**

### Files in this pack that you actually run

| File | Used in | Purpose |
|---|---|---|
| `starter_pack/check_entry_checks.py` | §D.1 | Pass 1 checks — already in the learners' pack |
| `mentor_kit/spot_the_flaw.py` | §C.9 | Hands-on Round 1 — the two rival implementations |
| `mentor_kit/add_appointment_checks.py` | §D.2 | Pass 2 checks — learners write their own, this is your reference |
| `mentor_kit/verify_totals.py` | §D.3 | Pass 3 — proves the 240.00 they wrote on paper |
| `mentor_kit/verify_save_load.py` | §D.4 | Pass 4 — the save/load round trip |
| `solution_pack/clinic_report.py` | §D.5 | Pass 5 — the finished report |

---

# Part 0 — The business problem

*Read this before §C.4. The scenario is what turns "build a function that validates input" into
"stop a clinic from making a budget decision on numbers that are quietly wrong."*

## Problem Statement

### Business Context

**Riverbend Family Health** is a group of four outpatient clinics. Across the group they see
roughly **1,100 patient appointments per month**, billed against five service categories:
Consultation, Diagnostics, Procedure, Follow-up, and Pharmacy.

Clinic spend is tracked in a **shared spreadsheet** maintained by two practice administrators.
Every appointment is typed in by hand — patient reference, date, category, cost. At month end,
one administrator assembles the spend summary that the Practice Manager takes into the partners'
budget meeting. That reconciliation takes roughly **11 hours per month**, and the summary is
retyped from scratch each time, because last month's spreadsheet cannot be reopened as data —
only read.

The spreadsheet has **no validation**. Anyone with the link can type anything into any cell. An
internal review across the last two quarters found:

- **Silent bad entries** — 6% of rows were missing a patient reference, a date, or both. They
  still totalled into the monthly figure, because a blank cell sums as zero rather than raising
  anything.
- **Negative costs used as a workaround** — administrators entered negative amounts to cancel
  out earlier typing mistakes rather than correcting the original row. 31 such rows in one
  quarter. Category totals looked plausible; the underlying visit counts were wrong.
- **Zero-cost visits deleted** — free follow-ups were removed by an administrator who assumed a
  cost of 0 meant a data-entry error. **Follow-up volume was understated by 14%.**
- **Category drift** — "Consult", "consultation", and "Consultation" were treated as three
  separate categories by the pivot table, silently splitting one category across three rows that
  nobody noticed at the bottom of the sheet.
- **Real-world loss** — in the Q3 budget meeting, Diagnostics spend was understated because a
  split category was read as the whole. The partners deferred a second ultrasound unit on those
  numbers. The decision was reversed the following quarter, at a higher price and after a
  two-month backlog had built up.

None of these were spreadsheet crashes. **Every one of them was a total that added up cleanly
and was wrong.** That is the failure mode this session is about.

> *Figures above are illustrative of patterns seen at mid-sized outpatient practices; they are
> not operational data from any real clinic. **Every appointment record used in this session is
> synthetic.***

### Objective

Build **Clinic Spend Tracker, version 1** — a small, checkable Python tool that replaces manual
entry and month-end reconciliation with validated entry, per-category totals, and a spend
summary the Practice Manager can take into the partners' meeting without retyping anything.

- **Refuse bad input at the door** — a missing patient reference, a missing date, an unknown
  category, or a negative cost is rejected *before* it enters the list, not discovered at month
  end. (`check_entry`)
- **Add only validated appointments** — one entry at a time, refused entries leave the list
  untouched. (`add_appointment`)
- **Total spending per category** — all five categories always reported, including those with no
  activity, so a quiet category cannot disappear from a budget meeting. (`total_by_category`)
- **Save the list and reopen it later** — last month becomes data, not a screenshot.
  (`save`, `load`)
- **Produce a manager-readable spend summary** — visits, spend, and share per category, with the
  largest cost driver named. (`build_report`)

**Out of scope for version 1:** no interface, no email or notifications, no database, no real
patient data.

### Why this is the right problem for an AI-assisted coding session

Every failure above is a **decision someone never wrote down**. Is a zero-cost visit valid? Is a
negative cost a refund or a mistake? Should a category with no activity vanish or show as zero?
The spreadsheet had no answer, so each administrator answered differently, and the totals drifted.

An AI coding assistant behaves exactly like those administrators: it will answer every one of
those questions confidently, differently each time, and never tell you it decided. That is why
`project_notes.md` exists, and why it is written **before** any prompt is sent.

| Clinic pain | The written decision (`project_notes.md`) | The check that proves it |
|---|---|---|
| Free follow-ups deleted as "errors" | A cost of zero is **allowed**. Zero means free, not invalid. | *a cost of exactly zero* → accepted |
| Negative amounts used to cancel mistakes | A negative cost is **refused**, not quietly accepted. | *minus 0.01* and *minus 50* → refused |
| Rows with no patient reference or date still totalling | A missing patient reference or date is **refused**. | built into `check_entry` |
| "Consult" / "consultation" splitting a category | An unknown category is **refused**. | *an unknown category* → refused |
| A quiet category dropping out of the pivot | A category with no activity shows as **zero**. It does not disappear. | all five categories present in the report |
| A total that read as the whole but was a part | Totals are checked against a number worked out by hand first. | Consultation must equal **240.00** |

**"The spreadsheet didn't crash. It gave a clean, confident, wrong answer, and a partner made a
purchasing decision on it. That is precisely what AI-generated code does when nobody checks it."**

### Data Description

`appointments_sample.csv` — a **synthetic seven-row extract** standing in for one week at a
single Riverbend site. Small enough that every learner can verify the totals by hand, which is
the entire point.

| Field | Type | Example | Rule |
|---|---|---|---|
| `patient_ref` | text | `PT-001` | Made-up reference. Required. |
| `date` | text | `2026-08-03` | Required. |
| `category` | text | `Consultation` | Must be one of the five valid categories. |
| `cost` | number | `120.00` | Zero or above. Zero is valid. |

**Valid categories:** Consultation, Diagnostics, Procedure, Follow-up, Pharmacy

The seven rows, and what they must total:

| Category | Visits | Spend |
|---|---|---|
| Consultation | 2 | 240.00 |
| Diagnostics | 2 | 550.50 |
| Procedure | 1 | 890.00 |
| Follow-up | 1 | 60.00 |
| Pharmacy | 1 | 15.25 |
| **Total** | **7** | **1,755.75** |

> **If the tool prints anything other than this, the tool is wrong, not the table.**

### The one number that carries the session

Consultation appears twice, at 120.00 each. **240.00.** Learners write it on paper before any
code exists, and check it against the tool three separate times — after `total_by_category`,
in the final report, and again at home this week. A number you committed to before you asked is
the only thing that makes a confident answer verifiable.

---

# Part A — Your prep, before the session

## A.1 Verify your own Codex setup (the day before, not five minutes before)

```bash
codex --version
cat ~/.codex/config.toml
echo $CODEX_LEARNER_KEY
```

If either of the last two prints nothing, the environment variable hasn't loaded into this
shell: run `source ~/.zshrc` (macOS default) or `source ~/.bashrc` (Linux), then retry. If VS
Code specifically can't see the key, **quit VS Code completely** — not just close the window —
and reopen it. VS Code caches environment variables at startup.

Then send one throwaway synthetic prompt through the chat panel to confirm the proxy actually
answers. A configured key that can't reach the proxy looks identical to a working setup right
up until you're live in front of the room.

## A.2 Set up four folders

You'll switch between these all session. Create them now, open each in its own VS Code window,
and fix the window order in your head before you start.

| Folder | Contents | Used for |
|---|---|---|
| **1. LIVE** | Copy of `starter_pack`, **minus** `catch_up_release_at_the_break/` | Everything you type in front of learners. Starts with no `.py` work in it. |
| **2. BROKEN** | Copy of `solution_pack` + the two planted bugs from §A.3 | §C.9 Spot the Flaw and §C.10 Break It, Fix It. Pre-staged, never typed live. |
| **3. REFERENCE** | Untouched `solution_pack` | Your safety net. If live generation goes sideways, switch here and keep moving. |
| **4. KIT** | The four `mentor_kit/*.py` files | Copy the relevant one into LIVE or BROKEN as each block needs it. |

## A.3 Pre-stage the two deliberate bugs (BROKEN folder)

**Bug 1 — for §C.9 Spot the Flaw.** Copy `mentor_kit/spot_the_flaw.py` into BROKEN alongside
`clinic_tracker.py` and `appointments_sample.csv`. Run it once now, privately, so you know it
works:

```
  Version A -> 120.0
  Version B -> 240.0
```

**Bug 2 — for §C.10 Break It, Fix It.** In BROKEN's `clinic_tracker.py`, change the cost check
inside `check_entry` from `<` to `<=`:

```python
        numeric_cost = float(cost)
        if numeric_cost <= 0:              # was:  < 0
            problems.append("cost cannot be negative")
```

Confirm privately that this fails **exactly one** of the five checks:

```
  a good entry                             expected accepted  got accepted  PASS
  a cost of exactly zero                   expected accepted  got refused   FAIL
  a cost of minus 0.01, just below zero    expected refused   got refused   PASS
  a clearly negative cost of minus 50      expected refused   got refused   PASS
  an unknown category                      expected refused   got refused   PASS

  4 of 5 checks passed.
```

That "exactly one" is the whole teaching point — you'll ask learners to predict *which* one.

## A.4 Memorise three numbers

You reference the first one three separate times. Say them the same way every time.

- **240.00** — Consultation, two visits at 120.00 each.
- **1,755.75** — grand total across seven appointments.
- **Procedure (890.00)** — the largest cost driver the report names.

| Category | Visits | Spend | Share |
|---|---|---|---|
| Consultation | 2 | 240.00 | 13.67% |
| Diagnostics | 2 | 550.50 | 31.35% |
| Procedure | 1 | 890.00 | 50.69% |
| Follow-up | 1 | 60.00 | 3.42% |
| Pharmacy | 1 | 15.25 | 0.87% |
| **Total** | **7** | **1,755.75** | 100.00% |

> If the tool prints anything other than this, the tool is wrong, not the table.

## A.5 Re-read three things

1. **[Part 0](#part-0--the-business-problem)** — the Riverbend scenario. You deliver this in 90
   seconds at §C.4 and call back to it twice more. Know the three beats without reading them.
2. `project_notes.md`, section **"Tricky cases we decided on purpose"** — and know which clinic
   failure each decision came from (the table in Part 0 maps them one to one).
3. `project_notes.md`, section **"The pieces"** — you'll point at it live when the AI drifts.

You will point at specific lines of that file at least four times. Know where they sit on screen
so you're not scrolling while talking.

---

# Part B — Concept cheat sheet

## B.1 Three roles, one director

You are the **Director**. Three verbs, in this order, every time:

- **Navigate** — steer what gets built, and what does not get built.
- **Review** — read every line before trusting it.
- **Decide** — accept, reject, or ask again. Nobody else makes this call.

The AI is a fast, fluent, confident collaborator that is sometimes wrong in ways that look right.

## B.2 The 8-step playbook (the general course workflow)

```
1 Define the Goal      → one clear paragraph. What does it do? What does it NOT do?
2 Ask for a Plan       → architecture before code. Components and build order.
3 Convert to Tasks     → each task small enough for one prompt.
4 Implement One Task   → one per prompt. Never bundle. Test before the next.
5 Add Validation Hooks → make assumptions visible as inline comments.
6 Generate Tests       → immediately after each function, not later.
7 Debug and Review     → run checks, feed failures back, apply the review checklist.
8 Refactor and Repeat  → every 3-4 tasks: duplication, TODOs, update the decisions file.
```

## B.3 How the 8 steps map onto this build

Steps 1–3 are **already done for you** — that's exactly what `project_notes.md` is. The session
runs steps 4–8, five times over:

| Pass | Piece | Built where |
|---|---|---|
| 1 | `check_entry` | Together, live, first half (§D.1) |
| 2 | `add_appointment` | Learners, independently (§D.2) |
| 3 | `total_by_category` | Learners, independently (§D.3) |
| 4 | `save` + `load` | One pass, both together (§D.4) |
| 5 | `build_report` | Separate file, `clinic_report.py` (§D.5) |

> **Nothing new is learned between pass one and pass five.** Same prompts, same decisions file,
> same checks, run again. Say this out loud — it's the single most reassuring sentence in the
> session for a learner who feels behind.

## B.4 The 4-step iteration loop, inside every pass

```
Build   → one function. Never more than you can read in 60 seconds.  ← the one-minute rule
  Test  → run it now. Sample inputs. Compare to what you expected. Never skip.
  Inspect → read it line by line. Assumptions you didn't specify? Gaps? Stubs?
  Refine → feed the result or error back. Ask for a specific correction.
    → back to Build
```

## B.5 The four prompt templates (verbatim from the course deck)

| # | Template |
|---|---|
| **1** Planning | *"I want to build [PROJECT]. Before writing any code, give me a high-level plan — what components do I need and what should I build first?"* |
| **2** Task breakdown | *"Here is component [NAME] from our plan. Break it into individual implementation tasks. Keep each task small enough to implement in a single prompt."* |
| **3** Implementation | *"Implement Task [N]: [DESCRIPTION]. Use Python. Keep the code simple and add comments explaining each section. Do not implement any other tasks yet."* |
| **4** Debugging | *"Here is the code and the error it produces: [PASTE CODE] / [PASTE ERROR]. Explain what is wrong and provide a corrected version with comments."* |

## B.6 The 5-point review checklist (run on every generated function)

1. **Does it do what I asked?** Run it with 3 inputs you can verify by hand.
2. **Are there hidden assumptions?** Hard-coded values, assumed types, unrequested logic.
3. **Is anything hard-coded that should be a variable?**
4. **Does it handle bad input?** Negative numbers, empty strings, `None`.
5. **Is any part security-sensitive?** File access, user input. Never trust AI alone here.

## B.7 The debugging loop (when a check fails)

1. Read the failure line carefully, before anything else.
2. Say what it means in your own words.
3. Template 4 — paste **both** the code and the full failure output.
4. Ask for the **root cause**, not just a fix.
5. Apply the fix, then re-run **all** checks — not only the one that failed.
6. Still failing? Paste the new output and repeat. **After two failed attempts, take manual
   control.**

## B.8 The two file types

> **The `.md` file holds the decisions. The `.py` files hold the work.**

`project_notes.md` runs nothing and breaks nothing. That is precisely why it's the right place
for requirements — you can read it, edit it, and argue with it without touching anything that
executes. A decision that only lives in the chat window is a decision the AI will forget.

---

# Part C — Minute-by-minute run of show

Timings match your session plan. Bold quoted lines are meant to be said close to verbatim.

## C.1 — 30 min — Learner and Mentor Introduction

Introductions, then a working setup check for everyone. Nobody proceeds without all four:

1. A clean, empty folder open as their VS Code workspace.
2. `starter_pack` files copied in — **without** `catch_up_release_at_the_break/`.
3. `codex --version` returns a version number in their terminal.
4. The Codex chat panel answers a trivial synthetic prompt.

Anyone failing #3 or #4 → §E.3. Pair them with a working neighbour rather than losing the whole
room to one laptop.

## C.2 — 5 min — Welcome, Learning Outcomes, and Session Expectations

**"Your job today is director, not typist. The AI does the typing. You decide what gets built,
whether it's right, and whether it ships."**

- AI-assisted coding is unpredictable. Reviewing and correcting the differences is part of the
  workflow, not evidence you did it wrong.
- Vocabulary used all session: *decisions file*, *piece*, *pass*, *check*, *drift*, *root cause*.
- Rule zero: synthetic data only, all session, no exceptions.

## C.3 — 5 min — Why Human Judgement Matters More Than Syntax

**"Code that runs successfully can still produce the wrong result. That is the central risk of
this whole way of working, and it's what we're training against today."**

Tell it in clinic terms, and plant the seed for §C.10:

> "Suppose `check_entry` refuses a zero-cost consultation, because someone wrote `<= 0` where
> they meant `< 0`. It runs. No error. It looks completely reasonable. Nobody notices until a
> free follow-up gets rejected in front of a patient. Later today I'm going to introduce that
> exact bug on purpose, and you're going to predict which check catches it — before we run
> anything."

> If you've already given the Riverbend story, say the payoff out loud: **"That is the same
> mistake a human already made in this clinic — an administrator deleted the free follow-ups
> because zero looked like a typo. We're about to make a machine do it faster."** If you're
> running §C.4 before §C.3 on the day, save this callback for then.

Then the three roles: **Navigate, Review, Decide** (§B.1).

**"Forming an expectation before you ask is the whole skill. If you don't know what the answer
should be, you cannot tell whether the AI gave you the right one."**

## C.4 — 5 min — Setup, Ground Rules, and What We Will Build

Show the three areas and name them:

| Area | Verb | What it's for |
|---|---|---|
| Chat panel | **ASK** | Prompts, plans, explanations |
| Editor | **WRITE** | The code and the decisions file |
| Terminal | **RUN** | Checks, scripts, the report |

Introduce the **one-minute rule**: if you cannot read the generated code in about 60 seconds,
the request was too big. Split it.

**Business context — deliver this from [Part 0](#part-0--the-business-problem), in about 90
seconds.** Don't read the whole section aloud; tell it as a story and land the three beats:

1. **Riverbend Family Health**, four outpatient clinics, ~1,100 appointments a month, spend
   tracked in a shared spreadsheet with no validation. Month-end reconciliation takes 11 hours.
2. **What went wrong:** free follow-ups deleted because someone assumed a 0 cost was an error.
   Negative amounts typed in to cancel out mistakes. "Consult" and "Consultation" quietly
   splitting one category into two. **None of it crashed anything.**
3. **What it cost:** a partners' budget meeting read an understated Diagnostics figure, deferred
   an ultrasound unit, and reversed the decision a quarter later at a higher price.

**"The spreadsheet didn't crash. It gave a clean, confident, wrong answer, and somebody spent
money on it. That is exactly what AI-generated code does when nobody checks it."**

Then the scope, read from `project_notes.md`:

> Add an appointment. Total spending by category. Save the list and reopen it later. Produce a
> spend summary a clinic manager can read. **No interface, no notifications, no database, no
> real data.**

**Point at the decisions table in Part 0 while you say this:** every rule in `project_notes.md`
exists because a human already got it wrong once. Zero is allowed *because* someone deleted the
free follow-ups. Unknown categories are refused *because* "Consult" split the pivot table. The
decisions file isn't paperwork — it's the incident log, written down before we prompt.

**Then the paper moment — do not skip it:**

> "Open `appointments_sample.csv`. Consultation appears twice, at 120.00 each. Write **240.00**
> on paper right now, before any code exists. You'll use that number three times today."

## C.5 — 5 min — The 8-Step Loop and the One-Big-Ask Trap

Show §B.2, then the five-pass mapping in §B.3.

Now demonstrate the trap, live, in **LIVE**. Paste this deliberately oversized ask:

```text
Build me the whole clinic tracker: add appointments, total spending by category,
save and load from a file, and print a spend summary.
```

Let it run 20–30 seconds, then stop it and narrate what came back:

- Everything at once, with no natural place to pause and review.
- Features nobody asked for — a CLI menu, an interactive loop, export options, maybe a database.
- No checks. No expectations stated anywhere.
- **"If this is wrong, where is it wrong? You can't answer that. That's the problem."**

**Then delete whatever it produced.** Do not build on it. The deletion is part of the lesson.

**"One small piece at a time isn't slower. It's the only version where you can tell whether
you're winning."**

## C.6 — 10 min — Live Demonstration: Planning, Scope, and Drift

Run **§D.1 Steps 1–3** (plan → drift correction → skeleton). Full prompts in Part D.

The moment that matters is when the AI's plan exceeds `project_notes.md`. **Do not re-explain
the project.** Point it at the file:

**"Watch what I do here. I'm not going to argue with it or re-describe the project. I'm going to
point it back at the decisions file. That file exists precisely so I never have to explain
anything twice."**

## C.7 — 10 min — Live Demonstration: Build One Piece, Predict, and Read It Back

Run **§D.1 Steps 4–6**.

Before prompting, get the five predictions on the whiteboard **from the room, not from you**:

| Input | Should be |
|---|---|
| A good entry | accepted |
| Cost of exactly `0` | accepted |
| Cost of `-0.01` | refused |
| Cost of `-50` | refused |
| Category `"Astrology"` | refused |

Ask the room for the zero case specifically. Some will say refused. **That disagreement is the
lesson** — it's exactly why the decision is written down in `project_notes.md` and not left to
whoever prompts first.

Then generate, then run the "explain it back" prompt, and compare its sentences to the table.

## C.8 — 10 min — Live Demonstration: Decisions File and Running Checks

Run **§D.1 Steps 7–8**.

- Split-screen `project_notes.md` and `clinic_tracker.py`. Point at each "Tricky case" decision
  and its matching line of code. Five decisions, five lines.
- **"The `.md` file is the decisions. The `.py` file is the work. When they disagree, the `.py`
  file is wrong."**
- Run `python check_entry_checks.py` → **5 of 5 checks passed.**
- Walk the two boundary cases: `0` and `-0.01` sit either side of zero on purpose. An everyday
  example like `-50` would never have caught an off-by-one boundary mistake.
- **"Passing checks proves the code behaves as expected for the checks we actually wrote. It
  proves nothing about the ones we didn't."** ← this line sets up §C.9 *and* §C.13.

## C.9 — 10 min — Hands-on Round 1: Spot the Flaw

Pairs, in the **LIVE** folder. Copy `mentor_kit/spot_the_flaw.py` in first.

**Read aloud:**

> "Two versions of the same helper, side by side, in `spot_the_flaw.py`. **Don't run it yet.**
> Using `appointments_sample.csv`, predict on paper what each returns for Consultation. Then run
> it. Judge by behaviour and output, not by which one reads more nicely."

After 5 minutes, run it together:

```
  Version A -> 120.0
  Version B -> 240.0
```

**The reveal:** Version A `return`s inside the loop, so it stops at the *first* matching
transaction. Version B accumulates across *all* matches.

Then the question that makes it stick:

> "Suppose I'd written a check using a category with only one appointment — Procedure, say.
> Version A returns 890.00. Version B returns 890.00. Check passes. **Both** versions pass. And
> one of them is broken. So what does a passing check actually tell you?"

**"A check that passes is only as good as the case you chose to check."**

## C.10 — 10 min — Live Demonstration: Break It, Fix It, and Improve It

Switch to **BROKEN**, which already has the `<=` bug staged (§A.3).

Show the changed line. Then, before running anything:

> **"Predict. Which of the five checks fail? Not 'some'. Name them."**

Take answers. The correct answer is **exactly one** — *"a cost of exactly zero"*, expected
accepted, will come back refused. The `-0.01` and `-50` checks were already refused and stay
refused. This surprises people, and it should.

Run it and confirm — **4 of 5 checks passed**, only the zero case failing.

Now run the root-cause prompt from **§D.6**. Insist on the explanation before the fix:

**"I don't want the patch. I want to know why. If I take the patch without the reason, I've
learned nothing and I'll write this same bug again next week."**

Apply the fix, then re-run **all five** checks, not just the failed one → back to 5 of 5.

**"Re-run everything. A fix that repairs one thing and quietly breaks another is the single most
common way this goes wrong."**

Then "improve it" — extend validation to a case nobody checked, using **§D.7**:

> "Our CSV loader hands `cost` over as text — `"120.00"`, not a number. None of our five checks
> cover that. Is it handled? Nobody in this room knows. Let's find out."

Whichever way it lands, land the point:

**"It turned out to be handled. But we didn't know that until we checked. You don't get credit
for a case you never tested — you just got lucky."**

## C.11 — 35 min — Hands-on Round 2: Run the 8-Step Loop Yourself

This is the block you asked about most, so here it is broken onto a clock.

**Before releasing them (2 min).** Get everyone onto the same starting line:

> "If your `check_entry` from the first half works, keep it. If you fell behind, open
> `catch_up_release_at_the_break/` now — **and rename the file.**"

```bash
cp catch_up_release_at_the_break/clinic_tracker_starter.py clinic_tracker.py
```

> ⚠️ **This rename is essential and no README mentions it.** `check_entry_checks.py` does
> `from clinic_tracker import check_entry`. If the file is still called
> `clinic_tracker_starter.py`, every check fails on import and the learner concludes their code
> is broken. Expect to say this two or three times.

Pairs where possible: one types, one reviews and challenges. Swap at the halfway point.

| Time | What they do | Reference |
|---|---|---|
| 0:00–0:02 | Get onto `clinic_tracker.py`, catch-up file if needed | above |
| 0:02–0:05 | **Predict first.** Write down what `add_appointment` should do for a good entry and for `cost=-50`, before prompting | §D.2 Step 1 |
| 0:05–0:12 | Build `add_appointment` (Template 3 prompt) | §D.2 Step 2 |
| 0:12–0:15 | Explain it back in one sentence, out loud, to their pair | §D.2 Step 3 |
| 0:15–0:22 | Write and run three checks for it | §D.2 Steps 4–5 |
| 0:22–0:30 | Build `total_by_category`, then verify **240.00** | §D.3 |
| 0:30–0:35 | Fix whatever failed, by tracing to root cause — not by re-prompting blindly | §B.7 |

**Circulate and watch for these four things specifically:**

1. **Skipping the prediction** and going straight to the prompt. Stop them. Ask "what *should*
   it do?" before letting them continue.
2. **Accepting code without reading it.** Point at a random line and ask what it does.
3. **A one-big-ask** that builds the remaining pieces at once. Point them back at §C.5.
4. **Re-prompting a failing fix** three or four times. After two, take manual control and read.

**Announce the milestone loudly when the first pair hits it:**

> **"Someone just got 240.00 out of code they didn't write and now understand. That's the whole
> session in one number."**

## C.12 — 5 min — Debrief: What Did the Workflow Catch?

Take live answers, don't lecture. Four questions, in this order:

1. Where did you get stuck, and what did you actually do about it?
2. Did the AI build anything you didn't ask for? **How did you notice?**
3. Did a check pass when the result was wrong — or fail when it should have passed?
4. Can you explain your `add_appointment` in one sentence, without reading the code?

**Steer this deliberately.** The valuable answers are about *incorrect expectations* and *gaps in
validation*, not about syntax errors. If the room is only reporting technical errors, ask
directly: "Did anyone's code run perfectly and give the wrong answer?"

## C.13 — 5 min — Close the Loop: From Working Code to a Verified Answer

Passes 4 and 5 (`save`/`load`, `build_report`) were not built hands-on — there isn't the clock
for it. Don't pretend otherwise. Say it plainly:

> **"Two pieces left. Same loop, same templates, same decisions file, run twice more. Nothing
> new to learn — so I'm going to run mine, and you'll rebuild one yourself this week."**

Switch to **REFERENCE** and run the finished report:

```bash
python clinic_report.py
```

```
SPEND SUMMARY

Category         Visits        Spend    Share
Consultation          2       240.00   13.67%
Diagnostics           2       550.50   31.35%
Procedure             1       890.00   50.69%
Follow-up             1        60.00    3.42%
Pharmacy              1        15.25    0.87%
TOTAL                 7      1755.75  100.00%

Largest cost driver: Procedure (890.00)
```

Point at the Consultation row. **"240.00. The number you wrote on paper before any code existed,
before any prompt was sent. That's what a verified result looks like."**

Then focus them on the numbers, not the formatting:

- Follow-up and Pharmacy appear once each and still show — a category with low activity doesn't
  vanish. **That's the pivot-table bug that cost Riverbend an ultrasound unit, and it cannot
  happen here, because we decided it couldn't before we wrote a line.**
- The report claims Procedure is the largest cost driver. That's a *claim*. It's trustworthy
  because the totals underneath it were checked, not because it printed neatly.
- **"This is the sheet that goes into the partners' meeting. Would you sign it?"** Take the
  answer. The right one is yes — and the reason is the five passing checks and the 240.00 on
  their paper, not that the output looks tidy.

**"Passing checks make the workflow checkable. Verified outputs and sound expectations are what
make the result trustworthy. They are not the same thing."**

## C.14 — 5 min — Scaling Up, Playbook, and Key Takeaways

**Scaling up (30 seconds).** The same loop scales to several AI helpers working in sequence: one
plans, one builds, one checks, one reports. The loop doesn't change. The decisions file becomes
shared context between all of them. That's the bridge to the rest of this program.

**The three practices to name explicitly:**

1. When it drifts, **point it at the file** — don't re-explain the project from scratch.
2. Ask it to **quote the decisions back**, to confirm it's using the intended ones:
   ```text
   Before we continue, quote the section of project_notes.md you are using for this piece,
   and summarise what we have built so far and what the next piece is.
   ```
3. When a result is uncertain, **investigate the untested input condition** rather than assuming
   it's fine because it resembles one you did test.

**The three key takeaways to close on:**

| | |
|---|---|
| **Structure beats cleverness** | Prompting isn't phrasing tricks. Plan → scope → one task at a time. |
| **Short loops win** | Build, Test, Inspect, Refine. Never more than you can read in 60 seconds. |
| **If the AI wrote it, you own it** | You are responsible for correctness, security, and behaviour. Not the AI. |

**Close on rule zero.** Synthetic data only. Then hand out `solution_pack` and set the follow-up:
rebuild one piece independently, and confirm the report prints **1,755.75 across seven
appointments** on your own machine.

---

# Part D — The complete prompt script

Every prompt needed to produce `solution_pack` from an empty folder, in order, with outputs
verified on a real run.

**Before Pass 1, open `project_notes.md` in an editor tab.** Codex reads open files as context.
Half the prompts below depend on it being visible. **If `project_notes.md` doesn't exist yet —
you're starting from a genuinely empty folder, not from `starter_pack` — run §D.0 first.** It
creates the decisions file and the sample data for you, then hands off directly into §D.1 Step 4.

> **A note on exact code, worth saying out loud when it happens.** These prompts specify
> behaviour precisely enough to reproduce the solution's *behaviour*. The AI will still vary
> naming, comment wording, and small structural choices between runs — a `set` vs a `list` for
> `VALID_CATEGORIES`, an inline check vs a `_is_missing` helper. **That variation is fine.** The
> checks are the contract, not the character-by-character code. Say so:
> *"Different from mine, same behaviour, all checks pass. That's an acceptable answer."*

---

## D.0 — Bootstrapping from zero (the `/init` prompt)

Use this when there is **no `starter_pack`** — an empty folder and nothing else. It's what you'd
run to rebuild your own practice copy of this project, or to hand a learner a from-scratch
version of the exercise instead of the pre-supplied files.

It does the work of Templates 1 and 2 in a single pass: it writes the decisions file first
(Step 1 of the 8-step playbook — Define the Goal — made durable instead of said once in chat),
generates the same verifiable sample data used throughout this guide, and then stops for a plan
review before any implementation exists. **It deliberately does not write `clinic_tracker.py` or
`clinic_report.py`.** That's the whole point — a decisions file you didn't have to argue the AI
out of drifting from.

Open an empty folder in VS Code, open the Codex chat panel, and paste this as one message:

```text
I'm starting a new project in this empty folder. Nothing exists yet. Before any code, set the
project up properly, in two steps. Do not skip ahead of these steps.

STEP 1 — Create the decisions file.

Create project_notes.md: plain English, nothing in it runs. This is our shared source of
truth — I will point you back at it whenever you drift from it. Use exactly this content:

# Clinic Tracker: project notes

Role of this file: the shared source of truth for the build, in plain English. Nothing here
runs. When the AI drifts, the relevant section gets pasted back into the chat.

Rule zero: synthetic data only. Never real patient information, at any point.

## What the tool does (version 1)
- Add an appointment: patient reference, date, category, cost
- Total spending by category
- Save the list to a file and reopen it later
- Produce a spend summary a clinic manager can read

## What it does NOT do (version 1)
- No interface
- No email or notifications
- No real data, no database

## What goes in
| Field | Example | Notes |
|---|---|---|
| patient_ref | PT-001 | Made-up reference, required |
| date | 2026-08-03 | Required |
| category | Consultation | Must be one of the valid list below |
| cost | 120.00 | A number, zero or above |

Valid categories: Consultation, Diagnostics, Procedure, Follow-up, Pharmacy

## What comes out
A total per category, a saved file that can be reopened, and a printed spend summary showing
visits, spend, and share per category, with the largest cost driver named.

## Tricky cases we decided on purpose
- A cost of zero is allowed. Zero means free, not invalid.
- A negative cost is refused, not quietly accepted.
- A missing patient reference or date is refused.
- An unknown category is refused.
- An empty list totals to nothing. It does not crash.
- A category with no activity shows as zero in the report. It does not disappear.

## The pieces
Built in this order, because each one depends on the one above it:
1. check_entry - refuse bad input before it gets in
2. add_appointment - add one appointment to the list
3. total_by_category - add up spending per category
4. save - write the list to a file
5. load - read the list back later
6. build_report - turn the totals into something a clinic manager would read
Pieces 1-5 live in clinic_tracker.py. Piece 6 lives in clinic_report.py.

save and load are built together in one pass, because neither is useful without the other, so
six pieces become five passes: (1) check_entry, (2) add_appointment, (3) total_by_category,
(4) save and load together, (5) build_report. Nothing new is learned between pass one and pass
five - same prompts, same decisions file, same checks, run again.

## How we check the pieces
Checks are printed lines, not a test framework: each one prints its name, what was expected,
what was got, and PASS or FAIL. check_entry_checks.py covers five situations: a good entry
(normal, accepted), a cost of exactly zero (edge, accepted), a cost of minus 0.01 (edge,
refused), a cost of minus 50 (failure, refused), and an unknown category (failure, refused).
The two boundary cases sit either side of zero on purpose - boundaries are where errors hide.

## The numbers we expect
(This table gets filled in after appointments_sample.csv is created in Step 1 below — leave a
placeholder for it for now.)

Also create appointments_sample.csv in this same folder, containing exactly these seven
synthetic rows, no more, no fewer:

patient_ref,date,category,cost
PT-001,2026-08-03,Consultation,120.00
PT-002,2026-08-03,Diagnostics,340.50
PT-001,2026-08-10,Follow-up,60.00
PT-003,2026-08-11,Procedure,890.00
PT-004,2026-08-11,Pharmacy,15.25
PT-002,2026-08-12,Consultation,120.00
PT-005,2026-08-12,Diagnostics,210.00

Then fill in "The numbers we expect" in project_notes.md with this table, computed from that
file: Consultation 2 visits / 240.00, Diagnostics 2 / 550.50, Procedure 1 / 890.00, Follow-up 1
/ 60.00, Pharmacy 1 / 15.25, total 7 visits / 1,755.75. End that section with the line: "If the
tool prints anything other than this, the tool is wrong, not the table."

STEP 2 — Plan only. No code yet.

Once project_notes.md and appointments_sample.csv exist, read project_notes.md back to me in
your own words to confirm you've understood it. Then give me a high-level plan: what pieces do
you need to build, in what order, and which file each one lives in.

Do not create clinic_tracker.py or clinic_report.py yet. Do not write any implementation code.
Stop after the plan and wait for me to ask for one piece at a time.
```

**What you get back:** `project_notes.md` and `appointments_sample.csv`, matching the ones this
whole guide is built around, plus a plan that should match "The pieces" table above. Read the
plan back against §B.3 before agreeing to it — if it invents a database, a CLI, or bundles two
pieces into one task, that's drift, and the fix is the same as everywhere else in this guide:
point it at the file you just had it write, and ask again.

**Once the plan is confirmed, you are exactly where §D.1 Step 4 starts** — skip Steps 1–3, they
were just done for you. Continue the five passes from there.

---

## D.1 — Pass 1: `check_entry` (mentor-led, live)

### Step 1 — Ask for a plan (Template 1)

```text
Read project_notes.md in this folder. Before writing any code, give me a high-level plan:
what pieces do I need, and in what order should I build them? Do not write any code yet.
```

**What good looks like:** six pieces in the order given under "The pieces" — `check_entry`,
`add_appointment`, `total_by_category`, `save`, `load`, `build_report` — with `build_report`
noted as living in `clinic_report.py`.

**What drift looks like:** a database layer, a CLI menu, a web interface, notifications, a
`main()` entry point, classes, a `requirements.txt`. Anything in the "What it does NOT do" list.
**This is your teaching moment — do not skip past it if it happens.**

### Step 2 — Correct the drift by pointing at the file

```text
That is more than we agreed. project_notes.md has a section called "What it does NOT do
(version 1)": no interface, no email or notifications, no real data, no database. Redo the
plan using only the six pieces listed under "The pieces", in the order given there.
```

### Step 3 — Generate the skeleton, not the implementation

```text
Create clinic_tracker.py with function signatures only for: check_entry, add_appointment,
total_by_category, save, and load. Each gets a one-line docstring and a `pass` body.

Also add a module-level VALID_CATEGORIES containing exactly: Consultation, Diagnostics,
Procedure, Follow-up, Pharmacy.

Do not implement any function body yet. I will build them one at a time.
```

**Expected shape:**

```python
VALID_CATEGORIES = {"Consultation", "Diagnostics", "Procedure", "Follow-up", "Pharmacy"}


def check_entry(patient_ref, date, category, cost):
    """Validate one appointment/expense entry."""
    pass

# ... four more stubs
```

**Say:** *"Five stubs. That's a to-do list, not a failure. Each stub is one task, and each task
is one prompt."*

### Step 4 — Build `check_entry` (Template 3)

> **Get the five predictions on the board first (§C.7). Then prompt.**

```text
Implement Task 1: fill in check_entry(patient_ref, date, category, cost) in clinic_tracker.py.

Rules, taken from project_notes.md:
- patient_ref is required. Missing means None, empty text, or only spaces.
- date is required, same definition of missing.
- category must be one of VALID_CATEGORIES.
- cost must be a number. Zero is allowed, because zero means free, not invalid.
- A negative cost is refused, not quietly accepted.

Return a list of short problem strings. An empty list means the entry is fine.
Add a comment above each check explaining what it is for.
Do not implement add_appointment, total_by_category, save, load, or build_report yet.
```

**Expected shape** (the solution's version — yours may differ in naming, not behaviour):

```python
def _is_missing(value):
    # Missing means None, empty text, or only spaces.
    return value is None or str(value).strip() == ""


def check_entry(patient_ref, date, category, cost):
    problems = []
    if _is_missing(patient_ref):
        problems.append("patient_ref is required")
    if _is_missing(date):
        problems.append("date is required")
    if category not in VALID_CATEGORIES:
        problems.append("category is not valid")
    try:
        numeric_cost = float(cost)
        if numeric_cost < 0:
            problems.append("cost cannot be negative")
    except (TypeError, ValueError):
        problems.append("cost must be a number")
    return problems
```

**Apply the 5-point review checklist out loud, on screen (§B.6).** Specifically:

- Is the zero boundary `< 0` and not `<= 0`? Point at it. **This is the exact line you break in §C.10.**
- Is `float(cost)` wrapped in a `try`? What happens with `None`? With `"free"`?
- Did it add anything you didn't ask for — a date-format check, a regex on `patient_ref`? If so,
  **that's drift**, and it isn't in `project_notes.md`. Remove it, or explicitly adopt it and
  write it into the decisions file. Don't leave it undecided.

### Step 5 — Read it back

```text
Explain what this function does in plain language, one sentence per rule, as if to a clinic
manager who does not write code. Then list any assumptions you made that I did not ask for.
```

Compare each sentence against the five predictions on the whiteboard. Any mismatch — stop and
resolve it before running anything.

### Step 6 — Add validation hooks (Step 5 of the 8-step playbook)

```text
Add inline comments to check_entry marking any assumption or uncertainty, in this format:
# ASSUMPTION: ...
Do not change any behaviour. Only add comments.
```

**Say:** *"Every ASSUMPTION comment is a debt entry. We're not resolving them now — we're making
them visible, so they can't hide."*

### Step 7 — Run the checks

```bash
python check_entry_checks.py
```

**Expected output, verbatim:**

```
CHECKS FOR check_entry

  a good entry                             expected accepted  got accepted  PASS
  a cost of exactly zero                   expected accepted  got accepted  PASS
  a cost of minus 0.01, just below zero    expected refused   got refused   PASS
  a clearly negative cost of minus 50      expected refused   got refused   PASS
  an unknown category                      expected refused   got refused   PASS

  5 of 5 checks passed.

Now do one by hand, on paper, before you trust any of this:
  Consultation is two visits at 120.00 each. You should see 240.00.
```

If a learner gets the ImportError banner instead, their file isn't named `clinic_tracker.py`, or
it isn't in the same folder. This is the #1 support call of the session.

### Step 8 — Trace the decisions to the code

Split-screen `project_notes.md` and `clinic_tracker.py`. Five written decisions, five lines of
code. Do it pointing at the screen — it takes 90 seconds and it's what makes the decisions file
feel real rather than like paperwork.

---

## D.2 — Pass 2: `add_appointment` (learners, independently)

### Step 1 — Predict, on paper, before prompting

| Action | Expected |
|---|---|
| Add one good entry to an empty list | list has 1 appointment |
| Add one entry with `cost=-50` | list still has 0 — refused, not added |
| Add two good entries | list has 2, in the order added |

### Step 2 — Build it (Template 3)

```text
Implement Task 2: fill in add_appointment(appointments, patient_ref, date, category, cost)
in clinic_tracker.py.

It must:
- Call check_entry first, using the existing validation rules.
- If check_entry returns any problems, refuse the entry by leaving the list unchanged.
- If it is valid, append a dictionary with the keys patient_ref, date, category, and cost,
  where cost is stored as a float.
- Return the appointments list either way, changed or unchanged.

Add a comment above each step. Do not implement total_by_category, save, load, or
build_report yet. Do not modify check_entry.
```

**Expected shape:**

```python
def add_appointment(appointments, patient_ref, date, category, cost):
    problems = check_entry(patient_ref, date, category, cost)
    if problems:
        return appointments
    appointments.append({
        "patient_ref": patient_ref,
        "date": date,
        "category": category,
        "cost": float(cost),
    })
    return appointments
```

**Review checklist — the two points that matter here:**

- Does it *call* `check_entry`, or did it re-implement the validation inline? Duplicated logic is
  a debt entry: two places to fix when one rule changes, and they will drift apart.
- Does it refuse *silently*, or does it raise / print / return `None`? `project_notes.md` says
  refuse and return the list unchanged. Silent refusal is a real design choice worth naming out
  loud — an entry can disappear without anyone being told.

### Step 3 — Explain it back

```text
Explain add_appointment in one sentence, in plain language. Then tell me what happens to the
appointments list when the entry is refused.
```

### Step 4 — Generate the checks (Step 6 of the playbook)

```text
Write checks for add_appointment in a new file called add_appointment_checks.py.

Copy the style of check_entry_checks.py exactly: no test framework, each check prints its
name, what was expected, what was actually got, and PASS or FAIL, then a count at the end.

Cover three situations:
- normal: a good entry is added, so the list length goes from 0 to 1
- failure: an entry with a cost of minus 50 is refused, so the list length stays 0
- normal: two good entries are both added, in the order they were added
```

> A ready-made reference version is in `mentor_kit/add_appointment_checks.py`. Use it if a
> learner is stuck, or to compare against — but let them generate their own first.

### Step 5 — Run the checks

```bash
python add_appointment_checks.py
```

**Expected output from the reference version, verbatim:**

```
CHECKS FOR add_appointment

  a good entry is added                    expected 1         got 1         PASS
  a negative cost is refused               expected 0         got 0         PASS
  two good entries both persist            expected 2         got 2         PASS
  the second entry is second               expected PT-002    got PT-002    PASS

  4 of 4 checks passed.
```

---

## D.3 — Pass 3: `total_by_category` (learners, independently)

### Step 1 — Predict

Consultation totals **240.00**. An empty list totals to all zeros and does not crash. A category
with no activity shows as `0.0` — it does not disappear from the result.

### Step 2 — Build it (Template 3)

```text
Implement Task 3: fill in total_by_category(appointments) in clinic_tracker.py.

It must:
- Start a total of 0.0 for every one of the five valid categories, so that a category with no
  activity still appears with a total of zero rather than disappearing.
- Add each appointment's cost into its matching category.
- Ignore any appointment whose category is not one of the five, in this step.
- Return the dictionary of category totals.
- An empty appointments list must return all zeros, not crash.

Add a comment above each step. Do not implement save, load, or build_report yet.
```

**Expected shape:**

```python
def total_by_category(appointments):
    totals = {
        "Consultation": 0.0,
        "Diagnostics": 0.0,
        "Procedure": 0.0,
        "Follow-up": 0.0,
        "Pharmacy": 0.0,
    }
    for appointment in appointments:
        category = appointment.get("category")
        cost = float(appointment.get("cost", 0))
        if category in totals:
            totals[category] += cost
    return totals
```

**Review checklist — the point that matters here.** Does the totals dictionary start with all
five categories present, or does it build up keys as it encounters them? The second version is
subtly wrong: Pharmacy would vanish from a month with no pharmacy spend, and the clinic manager
would never know a category was missing. This is a written decision in `project_notes.md` —
*"A category with no activity shows as zero in the report. It does not disappear."* Point at it.

### Step 3 — Verify against the number on paper

Copy `mentor_kit/verify_totals.py` into the working folder and run it:

```bash
python verify_totals.py
```

**Expected output, verbatim:**

```
  Consultation        240.00
  Diagnostics         550.50
  Procedure           890.00
  Follow-up            60.00
  Pharmacy             15.25

  Grand total: 1755.75
  Consultation should be 240.00. Grand total should be 1755.75.

  An empty list must total to nothing, not crash:
   {'Consultation': 0.0, 'Diagnostics': 0.0, 'Procedure': 0.0, 'Follow-up': 0.0, 'Pharmacy': 0.0}
```

**This is the 240.00 moment.** Make noise about it.

---

## D.4 — Pass 4: `save` and `load` (one pass, both together)

**Say first:** *"These two get built in one pass, because neither is useful alone. Saving a file
you can't reopen is not a feature."*

### Step 1 — Predict

Save two appointments, reopen the file, get two appointments back with the same totals, and
`cost` comes back as a *number* rather than the text a CSV actually stores. Loading a file that
doesn't exist returns an empty list — it does not crash.

### Step 2 — Build both (Template 3)

```text
Implement Task 4: fill in save(appointments, file_path="appointments.csv") and
load(file_path="appointments.csv") in clinic_tracker.py. Build both in this one pass,
because neither is useful without the other.

save must:
- Write all appointments to a CSV file using the csv module.
- Use the column order: patient_ref, date, category, cost.
- Write a header row.

load must:
- Return an empty list if the file does not exist. It must not crash.
- Read the rows back and return them as a list of dictionaries with the same four keys.
- Convert cost back to a float, because CSV stores everything as text.

Add a comment above each step. Do not implement build_report yet.
```

**Expected shape:**

```python
import csv
from pathlib import Path


def save(appointments, file_path="appointments.csv"):
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["patient_ref", "date", "category", "cost"])
        writer.writeheader()
        for appointment in appointments:
            writer.writerow({...})


def load(file_path="appointments.csv"):
    if not Path(file_path).exists():
        return []
    appointments = []
    with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            appointments.append({..., "cost": float(row.get("cost", 0))})
    return appointments
```

**Review checklist — point 5, security-sensitive, applies here for the first time.** This piece
touches the filesystem. Ask the room:

> "This writes to whatever path it's handed. What happens if that path came from user input?
> We're not fixing that today — version 1 takes no user input. But this is the piece where you
> stop skim-reading, because file access is where the review checklist earns its keep."

**Also flag the `float(row["cost"])` conversion explicitly.** Without it, `total_by_category`
would concatenate strings instead of adding numbers, and Consultation would come back as
`"120.00120.00"` instead of `240.0`. Silent, and completely wrong. **"This is the same class of
bug as Version A in Spot the Flaw. It runs. It's wrong."**

### Step 3 — Verify the round trip

Copy `mentor_kit/verify_save_load.py` in and run it:

```bash
python verify_save_load.py
```

**Expected output, verbatim:**

```
  saved   : 2 appointments
  reopened: 2 appointments
  totals match: True
  cost came back as a number, not text: True
  loading a file that does not exist: []

  All four lines above should read 2, 2, True, True, and [].
```

---

## D.5 — Pass 5: `build_report` (separate file)

**Say first:** *"New file: `clinic_report.py`. The tracker holds the data; the report turns it
into something a clinic manager reads. Different jobs, different files."*

### Step 1 — Predict

Five category rows, all present. Seven visits. 1,755.75 total. Procedure is the largest cost
driver at 890.00 — just over half the spend.

### Step 2 — Build it (Template 3)

```text
Implement Task 5: create a new file clinic_report.py containing build_report(file_path).

It must import VALID_CATEGORIES, load, and total_by_category from clinic_tracker. Do not
re-implement any of them.

It must:
- Load the appointments from file_path, defaulting to "appointments_sample.csv".
- Get the spend totals using total_by_category.
- Count the visits per category as well.
- Print every valid category in this fixed order, even if it has zero activity:
  Consultation, Diagnostics, Procedure, Follow-up, Pharmacy.
- Print, per category: the name, the visit count, the spend, and the share of total spend
  as a percentage.
- Print a TOTAL row with the total visits and the total spend.
- Name the largest cost driver by category and amount at the end.
- If the total spend is zero, shares must be 0.00% rather than a division-by-zero crash.

Use a fixed-width column layout so the numbers line up. Add a comment above each step.
Add a __main__ block that calls build_report("appointments_sample.csv").
```

### Step 3 — Run it

```bash
python clinic_report.py
```

**Expected output, verbatim:**

```
SPEND SUMMARY

Category         Visits        Spend    Share
Consultation          2       240.00   13.67%
Diagnostics           2       550.50   31.35%
Procedure             1       890.00   50.69%
Follow-up             1        60.00    3.42%
Pharmacy              1        15.25    0.87%
TOTAL                 7      1755.75  100.00%

Largest cost driver: Procedure (890.00)
```

> **Column alignment and share rounding will vary between runs. Ignore both.** The check is:
> five categories present, visits total 7, spend totals 1,755.75, Consultation is 240.00,
> Procedure named as the largest driver. **"Validate the numbers, not the formatting."**

### Step 4 — Refactor and repeat (Step 8 of the playbook)

The final prompt of the build, and the one most people skip:

```text
We have now built check_entry, add_appointment, total_by_category, save, load, and
build_report. Review all of it for:
- duplicated logic, especially validation rules written in more than one place
- any TODO or ASSUMPTION comments still unresolved
- anything that contradicts project_notes.md

List what you find. Do not change any code yet.
```

**Say:** *"Every three or four tasks, you stop and pay down debt. Duplication, unresolved TODOs,
decisions that drifted. Skip this pass often enough and you end up with a working program that
nobody can safely change — which is a different kind of broken."*

---

## D.6 — The Break It / root cause prompt (§C.10)

Used after the `<=` bug fails the zero check.

```text
Here is check_entry:

[PASTE THE FUNCTION]

Here is the check that now fails:

  a cost of exactly zero    expected accepted  got refused    FAIL

Explain the root cause of this failure. Do not give me a corrected version yet — I want to
understand why it happens first.
```

**Then, only after the explanation lands:**

```text
Now give me the corrected version, with a comment on the boundary line explaining why it is
"less than zero" and not "less than or equal to zero".
```

Then re-run **all five** checks.

## D.7 — The Improve It / untested condition prompt (§C.10)

```text
Our CSV loader hands cost to check_entry as text, for example "120.00" rather than a number.
None of our five checks cover that.

Add two checks to check_entry_checks.py in the existing style:
- a cost arriving as the text "120.00" should be accepted
- a cost arriving as the text "free" should be refused

Show me only the two new checks. Do not change check_entry.
```

**Expected addition:**

```python
results.append(run_check(
    'a cost arriving as text "120.00"',
    check_entry("PT-001", "2026-08-03", "Consultation", "120.00"),
    should_be_refused=False))

results.append(run_check(
    'a cost arriving as text "free"',
    check_entry("PT-001", "2026-08-03", "Consultation", "free"),
    should_be_refused=True))
```

Both pass against a correct `check_entry`, because the `float(cost)` inside the `try` already
handles them. **That is the lesson, not an anticlimax:** the behaviour was already right, and
until someone wrote the check, nobody in the room could have told you that.

## D.8 — Utility prompts (keep these in a scratch file, open)

**Drift — re-anchor:**
```text
Before we continue, quote the section of project_notes.md you are using for this piece, and
summarise what we have built so far and what the next piece is.
```

**Drift — hard boundary. Append to any implementation prompt:**
```text
Do not implement anything beyond this task. Do not modify any existing code.
```

**Ownership — when someone can't explain their code:**
```text
Explain this function line by line, in plain language, to someone who does not write code.
What would make it break?
```

**Assumption hunting:**
```text
What assumptions did you make in this code that I did not specify?
```

**When the AI has failed twice on the same fix — stop prompting. But if you must:**
```text
Stop trying to patch this. Explain, in plain language, what this code is actually doing
step by step for the input that fails, so I can find the mistake myself.
```

---

# Part E — Drift, failure, and troubleshooting

## E.1 Recognising drift, live

| Sign | What it looks like in this build |
|---|---|
| Scope creep | Builds `add_appointment` when you asked for `check_entry` only |
| Contradicts a decision | Refuses a zero cost; accepts an unknown category |
| Forgets a constraint | Reintroduces a database or CLI after you removed it |
| Invents requirements | Adds date-format validation, a `patient_ref` regex, currency handling |

**Three recovery techniques, in escalating order:**

1. **Explicit boundary** — append *"Do not implement anything beyond this task. Do not modify any
   existing code."* and re-ask.
2. **Point at the file** — quote the relevant `project_notes.md` section back at it (§D.1 Step 2).
3. **Reset and re-anchor** — start a fresh chat, paste `project_notes.md`, restate the current
   piece. Use this when the conversation has gone long and stale.

**"Drift isn't a failure. It's a signal. Short iterations catch it in 30 seconds. Long sessions
let it compound for an hour."**

## E.2 If the live demo goes wrong (it will, once)

This is fine, and you should say so. Options, in order of preference:

1. **Debug it live using the loop in §B.7.** This is the best possible outcome — an unscripted,
   real failure is more convincing than anything you planned.
2. **Time-box it to two attempts.** Then say: *"Two tries is my limit before I take manual
   control. That's a rule, not a mood."* Fix it by hand, out loud.
3. **Switch to REFERENCE.** *"Here's one I built earlier — same prompts, and it landed
   differently. That variation is exactly the thing you have to plan for."*

Never let a broken demo eat more than 4 minutes. The schedule has no slack in it.

## E.3 Setup troubleshooting

| Symptom | Fix |
|---|---|
| `codex --version` → command not found | Close and reopen the terminal/PowerShell window. |
| `cat ~/.codex/config.toml` or `echo $CODEX_LEARNER_KEY` print nothing | `source ~/.zshrc` (macOS) or `source ~/.bashrc` (Linux), then retry. |
| VS Code doesn't see the key | Quit VS Code completely, not just the window. It caches env vars at startup. |
| Managed laptop, npm install fails | `npm config get prefix` — if it's `C:\Program Files\`, `/usr/local`, or `/usr`, they need admin, or a user-scope prefix: `npm config set prefix "$HOME/.npm-global"`. |
| Managed laptop, PowerShell blocks the script | `Get-ExecutionPolicy -List` — `Restricted`/`AllSigned` under MachinePolicy or UserPolicy means Group Policy is blocking. Try `powershell -ExecutionPolicy Bypass -File .\gl-codex-setup.ps1 -LearnerKey "..."`. |
| Managed laptop, can't reach the proxy | `curl -v https://aibe.mygreatlearning.com/openai/v1/` — a 401 or 404 means success (server reached). Timeout or SSL error means the network is blocking or intercepting; needs an IT allowlist request. |
| Managed laptop, extension install greyed out | Extensions are allowlisted by their org. Codex still works from the terminal — pair them with a neighbour for the in-editor parts. |

## E.4 Code troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `check_entry_checks.py` prints the "no clinic_tracker.py" banner | Expected before Pass 1 is finished | Build `check_entry`, save as `clinic_tracker.py` in the same folder |
| Same banner *after* copying the catch-up file | File is still named `clinic_tracker_starter.py` | `cp catch_up_release_at_the_break/clinic_tracker_starter.py clinic_tracker.py` |
| `ModuleNotFoundError: No module named 'clinic_tracker'` | Running from the wrong directory | `cd` into the folder containing `clinic_tracker.py` first |
| Consultation totals `"120.00120.00"` | `cost` never converted to a float on load | Add `float(...)` in `load` — §D.4 |
| A category is missing from the totals | Totals dict built from encountered keys instead of pre-seeded with all five | §D.3, the review-checklist note |
| Total is 120.00 instead of 240.00 | `return` inside the loop instead of accumulating | The §C.9 bug, in the wild |
| `ZeroDivisionError` in the report | Share calculated without guarding a zero total | §D.5, the last bullet of the build prompt |

## E.5 Common learner mistakes to name out loud

- Prompting for the whole app in one go instead of one scoped task.
- Sending the entire project as context for a one-line change.
- Accepting generated code without reading it — *"it ran, so it's fine"*.
- Letting the AI retry a failing fix four or five times instead of stepping in after two.
- Continuing one long stale conversation instead of starting fresh and re-anchoring.
- **Skipping the prediction.** This is the one that actually costs them, and it's invisible
  unless you're circulating and watching.

---

# Part F — What to hand out, and when

| When | What | Why the timing matters |
|---|---|---|
| Before the session | `starter_pack/` **without** `catch_up_release_at_the_break/` — `project_notes.md`, `appointments_sample.csv`, `check_entry_checks.py`, `README.md` | There are no finished `.py` files on purpose. Handing over answers before they build undercuts the whole point. |
| Start of §C.9 | `mentor_kit/spot_the_flaw.py` | Needs `clinic_tracker.py` to exist, so it can't go out earlier. |
| Start of §C.11, only for those who fell behind | `catch_up_release_at_the_break/clinic_tracker_starter.py` | Opening it early means watching the first half instead of doing it — the one thing that stops the session working. |
| During §C.11, on request | `mentor_kit/verify_totals.py` | They should attempt their own checks first. |
| End of session | `solution_pack/` in full, plus `mentor_kit/verify_save_load.py` | The follow-up task needs `save`/`load` to exist. |

**The follow-up task to set, verbatim:**

> "Rebuild one piece on your own — pick whichever one you understood least today. Then run
> `clinic_report.py` and confirm it prints **1,755.75 across seven appointments** on your own
> machine. If it doesn't, you have a bug, and you now know exactly how to find it."

---

# Appendix — Session-day quick card

Print this page. Everything above it is preparation.

**The story (90 sec, §C.4):** Riverbend Family Health, 4 clinics, ~1,100 appointments/month,
spreadsheet with no validation · free follow-ups deleted because 0 looked like a typo · negatives
typed in to cancel mistakes · "Consult" vs "Consultation" split a category · partners deferred an
ultrasound unit on an understated figure, reversed a quarter later at a higher price.
**"It didn't crash. It gave a clean, confident, wrong answer."**

**Numbers:** 240.00 (Consultation) · 1,755.75 / 7 appointments · Procedure 890.00 largest driver

**Three areas:** chat = ASK · editor = WRITE · terminal = RUN

**One-minute rule:** if you can't read it in 60 seconds, the ask was too big.

**Loop:** Build → Test → Inspect → Refine

**Review:** does it do what I asked? · hidden assumptions? · hard-coded? · bad inputs? · security?

**On failure:** read it → say it in your own words → paste code AND error → ask for root cause →
fix → **re-run everything** → two attempts, then take manual control.

**On drift:** boundary → point at the file → reset and re-anchor.

**Commands:**
```bash
python check_entry_checks.py        # 5 of 5
python add_appointment_checks.py    # 4 of 4
python verify_totals.py             # Consultation 240.00, grand total 1755.75
python verify_save_load.py          # 2, 2, True, True, []
python clinic_report.py             # 1755.75 across 7, Procedure largest
```

**The five prompts you cannot skip:**
1. Plan → `Read project_notes.md ... Do not write any code yet.`
2. Scope → `That is more than we agreed ... Redo the plan using only the six pieces.`
3. Build → `Implement Task N ... Do not implement [the others] yet.`
4. Read back → `Explain what this function does in plain language, one sentence per rule.`
5. Root cause → `Explain the root cause of this failure. Do not give me a corrected version yet.`

**Close on:** structure beats cleverness · short loops win · if the AI wrote it, you own it ·
synthetic data only.
