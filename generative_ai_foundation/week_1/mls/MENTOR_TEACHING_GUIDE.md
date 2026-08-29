# Clinic Tracker MLS — Mentor Teaching Guide

**Session:** Applications of AI and Agentic AI in Healthcare — Week 1 Mentor-Led Session
**Tool:** AI-assisted coding with Codex in VS Code
**Build:** Clinic Spend Tracker (synthetic data only)
**Duration:** 150 minutes (30+5+5+5+5+10+10+10+10+10+35+5+5+5 per your agenda screenshot)

**Rule zero, said out loud at the start and repeated whenever it's relevant: synthetic data only.
Never real patient information — not in a prompt, not in a file, not in a screenshot.**

---

## 0. How this guide was built, and what's an assumption

I read every file you attached (`project_notes.md`, both `README.md` files, `check_entry_checks.py`,
`clinic_tracker_starter.py`, the solution pack's `clinic_tracker.py`/`clinic_report.py`,
`appointments_sample.csv`) plus your two agenda screenshots, and I extracted text from the course
PDFs in `lecture_notes/` and `additional_material/` (Codex setup guide, Codex best-practices,
and the five "Video" slide decks) to pin down the exact vocabulary the course uses (the 8-step
playbook, the 4-step iteration loop, the 4 prompt templates, the 5-point review checklist, the
debugging loop).

None of your source files spell out a **minute-by-minute run of show** or give you the **broken
code** needed for "Spot the Flaw" and "Break It, Fix It." I built those in this guide. Anywhere I
filled a gap rather than quoting a source, you'll see:

> 🧭 **Mentor call — not in your source PDFs.** ...

so you can change it if it doesn't match your own deck. In particular, "Slide 33" (mentioned in
`starter_pack/README.md`) is in your Olympus-hosted learner deck, which wasn't part of what you
attached — I couldn't check its exact wording, only paraphrase what the README implies it says.

---

## 1. Before the session (your prep, not the learners')

1. **Confirm your own Codex setup works**, using a throwaway synthetic prompt — don't wait until
   you're live to discover the proxy is misconfigured.
   ```bash
   codex --version
   cat ~/.codex/config.toml
   echo $CODEX_LEARNER_KEY
   ```
   If either verification command prints nothing, reload your shell config
   (`source ~/.zshrc` or `source ~/.bashrc`) and try again. If VS Code doesn't see the key,
   quit VS Code completely (don't just close the window) and reopen it.

2. **Set up three separate folders on your machine**, all copies of `starter_pack` (minus the
   `catch_up_release_at_the_break` subfolder, which you keep separately and don't open until the
   break):
   - **Live-build copy** — this is what you type into, in front of the learners, during every
     "Live Demonstration" block.
   - **Break-it copy** — a second copy where you pre-stage the deliberate bugs for
     "Hands-on Round 1: Spot the Flaw" and "Live Demonstration: Break It, Fix It, and Improve It"
     (see §3.9 and §3.10 — you want these ready *before* you're live, not typed under time pressure).
   - **Reference copy** — the finished `solution_pack`, open in a separate window, so you can
     sanity-check any surprising AI output against a known-good answer without fumbling for files
     mid-session.

3. **Memorise the three numbers** you'll reference three separate times, per the starter README:
   - Consultation: 2 visits × 120.00 = **240.00**
   - Full report total: 7 appointments, **1,755.75** grand total (see table below)
   - The category breakdown:

     | Category | Visits | Spend |
     |---|---|---|
     | Consultation | 2 | 240.00 |
     | Diagnostics | 2 | 550.50 |
     | Procedure | 1 | 890.00 |
     | Follow-up | 1 | 60.00 |
     | Pharmacy | 1 | 15.25 |
     | **Total** | **7** | **1,755.75** |

4. **Rehearse the three-pane layout** you'll ask learners to keep open the whole session:
   **chat panel = ASK, editor = WRITE, terminal = RUN.**

5. Skim `project_notes.md` and `starter_pack/README.md` one more time immediately before the
   session — they are short, and you will be pointing learners back to specific lines of
   `project_notes.md` live.

---

## 2. The mental model (your cheat sheet — screen-share or read from this section)

### 2.1 Three roles, one director
You are the **Director**: **Navigate** (steer what gets built), **Review** (read every line before
trusting it), **Decide** (accept, reject, or ask again). The AI is a fast, confident, sometimes
wrong collaborator — never a search engine for correct code.

### 2.2 The 8-step playbook (from Video 5, generalised)
```
Define the Goal → Ask for a Plan → Convert to Tasks → Implement One Task →
Add Validation Hooks → Generate Tests → Debug and Review → Refactor and Repeat
```
This is the **general** course playbook. For the clinic tracker, it's been pre-scoped into five
concrete passes, already decided for you in `project_notes.md`:

| Pass | Piece | Where it happens |
|---|---|---|
| 1 | `check_entry` | Built together, live, first half |
| 2 | `add_appointment` | Learners build alone, second half |
| 3 | `total_by_category` | Learners build alone, second half |
| 4 | `save` and `load` | See §3.13 — time-boxed, likely mentor-led |
| 5 | `build_report` | See §3.13 — time-boxed, likely mentor-led |

### 2.3 The 4-step iteration loop, inside every pass
```
Build (one function, never more than you can read in 60 seconds — the "one-minute rule")
  → Test (run it now, don't skip)
    → Inspect (read it line by line — assumptions? gaps? stubs?)
      → Refine (feed the result/error back, ask for a specific correction)
        → back to Build
```
Repeat until the piece passes its checks **and** you can explain it in plain English.

### 2.4 The four prompt templates (verbatim from the course deck)
1. **Planning:** *"I want to build [PROJECT]. Before writing any code, give me a high-level
   plan — what components do I need and what should I build first?"*
2. **Task breakdown:** *"Here is component [NAME] from our plan. Break it into individual
   implementation tasks. Keep each task small enough to implement in a single prompt."*
3. **Implementation:** *"Implement Task [N]: [DESCRIPTION]. Use Python. Keep the code simple
   and add comments explaining each section. Do not implement any other tasks yet."*
4. **Debugging:** *"Here is the code and the error it produces: [PASTE CODE] / [PASTE ERROR].
   Explain what is wrong and provide a corrected version with comments."*

### 2.5 The 5-point code review checklist (run this on every generated function)
1. Does it do what I asked? (run it with 3 inputs you can verify by hand)
2. Are there hidden assumptions? (hard-coded values, assumed types, unrequested logic)
3. Is anything hard-coded that should be a variable?
4. Does it handle bad input? (negative numbers, empty strings, `None`)
5. Is any part of it security-sensitive? (file access, user input — never trust AI output alone here)

### 2.6 The debugging loop (for when a check fails)
1. Read the error/failed-check line carefully, before anything else.
2. Try to explain, in your own words, what it's saying.
3. Use Template 4 — paste **both** the code and the full error/failure output.
4. Ask the AI to explain the **root cause**, not just hand you a fix.
5. Apply the fix and re-run **all** checks, not just the one that failed.
6. If it still fails, paste the new error and repeat.

### 2.7 The two file types
> The `.md` file holds the decisions. The `.py` files hold the work.

`project_notes.md` runs nothing and breaks nothing — it's the shared, persistent memory the AI
doesn't have. Every time the AI drifts, the fix is: point it back at `project_notes.md`, don't
re-explain from scratch.

---

## 3. Minute-by-minute run of show

### 3.1 — 30 min — Learner and Mentor Introduction
Logistics only. Confirm everyone has: a clean empty folder opened as their VS Code workspace,
the `starter_pack` files copied in (not `catch_up_release_at_the_break`), and a working Codex
setup (`codex --version` in their terminal). Fix any setup problems now — see §5 Troubleshooting.

### 3.2 — 5 min — Welcome, Learning Outcomes, and Session Expectations
Talking points:
- You are the director, not the typist — the AI writes, you decide.
- Reviewing and correcting AI output is part of the workflow, not a failure of it.
- Ground rule: synthetic data only, always.
- Vocabulary to introduce now, used all session: *decisions file*, *piece*, *pass*, *check*,
  *drift*, *root cause*.

### 3.3 — 5 min — Why Human Judgement Matters More Than Syntax
Talking point + one concrete story, in clinic terms (mirrors the "silent bug" example in Video 3):
> "Code can run with zero errors and still be wrong. Imagine `check_entry` refuses a $0
> consultation because someone typed `<= 0` instead of `< 0`. It runs. It looks reasonable.
> Nobody notices until a real free follow-up gets rejected. We're going to manufacture exactly
> this bug later this session, on purpose, so you know what it feels like to catch one."
(This previews §3.10 — plant the seed now.)

### 3.4 — 5 min — Setup, Ground Rules, and What We Will Build
- Show the three panes: chat = **ASK**, editor = **WRITE**, terminal = **RUN**.
- Introduce the **one-minute rule**: if you can't read the generated code in about 60 seconds,
  the request was too big — split it.
- Business context (read straight from `project_notes.md` "What the tool does (version 1)"):
  add an appointment, total spend by category, save/reopen the list, print a spend summary.
- State the target numbers out loud: *Consultation, two visits at 120.00 each — you should see
  240.00.* Ask everyone to write it on paper before any code exists.

### 3.5 — 5 min — The 8-Step Loop and the One-Big-Ask Trap
- Show the 8-step playbook diagram (§2.2) and the 5-pass mapping table (§2.2).
- Live, in your **break-it copy**, paste this deliberately oversized ask so learners see the
  failure mode before you show them the fix:

  ```text
  Build me the whole clinic tracker: add appointments, total spending by category,
  save and load from a file, and print a spend summary.
  ```
  Point out what typically comes back: everything at once, extra features nobody asked for
  (a CLI menu, print formatting choices, maybe email/export stubs), and no natural place to
  stop and review. Don't fully build any of it — cut it off after the plan/first draft appears,
  and move straight into §3.6, which repairs this the right way.

### 3.6 — 10 min — Live Demonstration: Planning, Scope, and Drift
In your **live-build copy**, with `project_notes.md` open in the editor tab (so it's in context):

**Prompt 1 — ask for a plan, scoped to the decisions file:**
```text
Read project_notes.md in this folder. Before writing any code, give me a high-level plan:
what pieces do I need, and in what order should I build them?
```
Compare the plan against the "The pieces" section of `project_notes.md`. If the AI invents
extra components (a database, a CLI, email), that's drift — call it out immediately.

**Prompt 2 — correct the drift by pointing back at the file:**
```text
That's more than we asked for. Only build check_entry for now, using the rules under
"What goes in" and "Tricky cases we decided on purpose" in project_notes.md. Do not implement
add_appointment, total_by_category, save, load, or build_report yet.
```

**Prompt 3 — generate the skeleton, not the implementation:**
```text
Show me a skeleton for clinic_tracker.py: function signatures for check_entry, add_appointment,
total_by_category, save, and load, each with a one-line docstring but no implementation
(use `pass`). I will implement them one at a time.
```
This mirrors `catch_up_release_at_the_break/clinic_tracker_starter.py` — you're generating the
same shape of file the safety-net copy already has.

### 3.7 — 10 min — Live Demonstration: Build One Piece, Predict, and Read It Back
**Before prompting, say the predictions out loud** (write them where everyone can see):
a good entry → accepted; cost of exactly `0` → accepted; cost of `-0.01` → refused;
cost of `-50` → refused; an unknown category → refused.

**Prompt (Template 3, Implementation):**
```text
Implement Task: write check_entry(patient_ref, date, category, cost) in clinic_tracker.py.

Rules:
- patient_ref and date are required (missing means refused).
- category must be exactly one of: Consultation, Diagnostics, Procedure, Follow-up, Pharmacy.
- cost must be a number. Zero is allowed (free is not invalid). Negative is refused.
Return a list of problem strings. An empty list means the entry is fine.
Add comments explaining each check. Do not implement any other function yet.
```

**Read it back — ask the AI to explain its own output:**
```text
Explain what this function does in plain language, one sentence per rule. What assumptions
did you make that I did not explicitly ask for?
```
Compare the explanation, sentence by sentence, against the five predictions from the top of
this block. Any mismatch is worth pausing on.

### 3.8 — 10 min — Live Demonstration: Decisions File and Running Checks
- Open `project_notes.md` side-by-side with `clinic_tracker.py`. Point at "Tricky cases we
  decided on purpose" and show each rule has a matching line of code.
- Run the provided checks:
  ```bash
  python check_entry_checks.py
  ```
  Expected output: **5 of 5 checks passed.**
- Walk through why the two boundary checks (`0` and `-0.01`) sit either side of zero on purpose —
  an everyday example (like `-50`) would never catch an off-by-one boundary mistake.

### 3.9 — 10 min — Hands-on Round 1: Spot the Flaw
Pair activity. Give learners these two versions of a helper function (put them on screen, or in
a handout — they are not in any provided file, write them into your **break-it copy** ahead of
time):

```python
# Version A
def total_for_category(appointments, category):
    for appointment in appointments:
        if appointment["category"] == category:
            return appointment["cost"]
    return 0.0
```

```python
# Version B
def total_for_category(appointments, category):
    total = 0.0
    for appointment in appointments:
        if appointment["category"] == category:
            total += appointment["cost"]
    return total
```

**Instructions to read aloud:**
> "Using `appointments_sample.csv`, predict the output of both versions for `category=
> "Consultation"` before running either. Which one is correct? You should see 240.00 from
> exactly one of them."

Reveal: **Version A is wrong** — it returns after the *first* matching transaction (120.00),
not the total across all matches. Version B accumulates correctly (240.00). The bug is invisible
if you only test with one matching row — this is the same "silent bug" failure mode from §3.3,
now made concrete.

### 3.10 — 10 min — Live Demonstration: Break It, Fix It, and Improve It
In your **break-it copy**, edit `check_entry`'s cost check from:
```python
if cost_value < 0:
```
to:
```python
if cost_value <= 0:
```
**Before running anything, ask learners to predict:** which of the 5 checks in
`check_entry_checks.py` will now fail? (Answer: only *"a cost of exactly zero"* — expected
accepted, will now come back refused. The other four are unaffected.)

Run it to confirm:
```bash
python check_entry_checks.py
```

**Root-cause prompt (Template 4, Debugging):**
```text
Here is check_entry: [paste the function]. Here is the check that now fails:
"a cost of exactly zero    expected accepted got refused    FAIL"
Explain the root cause of this failure — don't just give me a fix.
```
Apply the fix (`<` instead of `<=`), then **re-run all 5 checks, not just the failed one**:
```bash
python check_entry_checks.py
```
Expected: back to **5 of 5 checks passed.**

**Improve it — investigate an untested input condition:**
```text
Our CSV loader will hand cost to check_entry as text, e.g. "120.00", not a float. Add a check
to check_entry_checks.py for a cost value arriving as text from a spreadsheet: "120.00"
should be accepted, and "free" should be refused. Show me the two new checks.
```
This one is a good teaching moment either way: the existing `float(cost)` conversion already
handles both cases correctly, so learners see that testing an untested condition is what
proves it works — you don't get credit for a case you never checked.

### 3.11 — 35 min — Hands-on Round 2: Run the 8-Step Loop Yourself
Read this block aloud before releasing learners to work independently, in pairs where possible
(one types, one reviews and challenges).

**Step 0 — get everyone onto the same file.** If your own `check_entry` from the first half
works, keep using it. If you fell behind, run this from inside your `starter_pack` folder:
```bash
cp catch_up_release_at_the_break/clinic_tracker_starter.py clinic_tracker.py
```
> 🧭 **Mentor call — not stated in the source files.** `check_entry_checks.py` does
> `from clinic_tracker import check_entry`, so the file must be named exactly
> `clinic_tracker.py` in your project root — the catch-up file's original name won't import.
> Worth saying explicitly, since neither `README.md` mentions the rename.

**Step 1 — build `add_appointment` (Template 3):**
```text
Implement Task: write add_appointment(appointments, patient_ref, date, category, cost) in
clinic_tracker.py. It must call check_entry first. If check_entry returns any problems, return
the appointments list unchanged — do not add the entry. If it's valid, append a dict with keys
patient_ref, date, category, and cost (as a float) to appointments, then return the list.
Add comments. Do not implement total_by_category, save, load, or build_report yet.
```
Predict before running: adding one good entry → list length 1. Adding one entry with
`cost=-50` → list length unchanged.

Write 3 checks for it yourself, copying the pattern from `check_entry_checks.py` (name, expected,
got, PASS/FAIL) — a good entry is added; a bad entry is refused and the list doesn't grow; two
good entries both persist, in order.

**Step 2 — build `total_by_category` (Template 3):**
```text
Implement Task: write total_by_category(appointments) in clinic_tracker.py. Return a dict with
one key per valid category (Consultation, Diagnostics, Procedure, Follow-up, Pharmacy), each
starting at 0.0, and add up the cost of every appointment into its matching category. An empty
list of appointments must return all-zero totals, not crash. Add comments. Do not implement
save, load, or build_report yet.
```

**Step 3 — verify against the number you wrote down at the start.** Since `save`/`load` aren't
built yet, use this small script to load the seven sample rows by hand and confirm the totals:
```python
from clinic_tracker import add_appointment, total_by_category

appointments = []
add_appointment(appointments, "PT-001", "2026-08-03", "Consultation", 120.00)
add_appointment(appointments, "PT-002", "2026-08-03", "Diagnostics", 340.50)
add_appointment(appointments, "PT-001", "2026-08-10", "Follow-up", 60.00)
add_appointment(appointments, "PT-003", "2026-08-11", "Procedure", 890.00)
add_appointment(appointments, "PT-004", "2026-08-11", "Pharmacy", 15.25)
add_appointment(appointments, "PT-002", "2026-08-12", "Consultation", 120.00)
add_appointment(appointments, "PT-005", "2026-08-12", "Diagnostics", 210.00)

print(total_by_category(appointments))
```
Expected: `Consultation: 240.0` — the number learners wrote on paper before the session started.
Full totals: Diagnostics 550.5, Procedure 890.0, Follow-up 60.0, Pharmacy 15.25.

While pairs work, circulate and watch for: skipping the predict-before-run step, accepting code
without reading it, and one-big-ask requests that build all remaining pieces at once.

### 3.12 — 5 min — Debrief: What Did the Workflow Catch?
Discussion questions, read aloud, take a few live answers:
- Where did you get stuck, and what did you do about it?
- Did the AI build anything you didn't ask for? How did you notice?
- Did any check pass when the result was actually wrong, or fail when it should have passed?
- Could you explain, out loud, what your `add_appointment` does — in one sentence?

### 3.13 — 5 min — Close the Loop: From Working Code to a Verified Answer
Only `check_entry`, `add_appointment`, and `total_by_category` were built hands-on in the time
available. `save`/`load` and `build_report` are Passes 4 and 5 — same loop, same templates,
just not enough clock time to do them independently in this session.

> 🧭 **Mentor call — not explicit in your source files.** Two ways to close this gap, pick
> based on how much time you actually have left:
> - **If you have 5+ spare minutes:** live-build `save`/`load` and `build_report` yourself,
>   narrating each as "same loop, same templates, just running it two more times" — this is
>   literally true per `project_notes.md`'s "Six pieces, five passes" section.
> - **If you're out of time (the more likely case with a 35-minute Round 2):** switch your
>   screen to the `solution_pack` copy and run the finished report directly:
>   ```bash
>   python clinic_report.py
>   ```
>   Say plainly that this is the mentor's pre-built version, not something they typed — the
>   point of this block is verifying the number, not typing more code under time pressure.

Either way, run it and get:
```
SPEND SUMMARY

Category         Visits        Spend    Share
Consultation          2       240.00    13.67%
Diagnostics           2       550.50    31.36%
Procedure             1       890.00    50.71%
Follow-up             1        60.00     3.42%
Pharmacy              1        15.25     0.87%
TOTAL                 7      1755.75  100.00%

Largest cost driver: Procedure (890.00)
```
Point at the Consultation row and compare it to the 240.00 learners wrote on paper at the start.
Reinforce: passing checks proves the code is checkable, not that it's automatically correct —
the report is trustworthy because you verified it, not because it ran.

### 3.14 — 5 min — Scaling Up, Playbook, and Key Takeaways
Talking points:
- The same loop scales to multiple AI helpers working sequentially: plan → build → check → report.
- The decisions file (`project_notes.md`) is persistent project context — when the AI drifts,
  point it back at the file; ask it to quote the relevant section back to confirm it's using
  the intended decisions, rather than re-explaining from scratch.
- Investigate untested input conditions when results remain uncertain — don't assume a case is
  covered just because it looks similar to one you did test (§3.10's CSV-text example).
- Three key takeaways to close on (from the course's own Video 5 summary):
  1. Structure beats cleverness — plan → scope → one task at a time.
  2. Short loops win — build, test, inspect, refine, never more than you can read in 60 seconds.
  3. If the AI wrote it, you own it — you are responsible for correctness, not the AI.
- Restate the synthetic-data rule one final time.
- Hand out `solution_pack` now. Per `starter_pack/README.md`, the follow-up task is: rebuild one
  piece independently, and confirm the report prints **1,755.75 across seven appointments** on
  their own machine.

---

## 4. Copy-paste prompt library (everything in one place)

**Planning**
```text
Read project_notes.md in this folder. Before writing any code, give me a high-level plan:
what pieces do I need, and in what order should I build them?
```
```text
That's more than we asked for. Only build check_entry for now, using the rules under
"What goes in" and "Tricky cases we decided on purpose" in project_notes.md. Do not implement
add_appointment, total_by_category, save, load, or build_report yet.
```
```text
Show me a skeleton for clinic_tracker.py: function signatures for check_entry, add_appointment,
total_by_category, save, and load, each with a one-line docstring but no implementation
(use `pass`). I will implement them one at a time.
```

**Implementation — check_entry**
```text
Implement Task: write check_entry(patient_ref, date, category, cost) in clinic_tracker.py.

Rules:
- patient_ref and date are required (missing means refused).
- category must be exactly one of: Consultation, Diagnostics, Procedure, Follow-up, Pharmacy.
- cost must be a number. Zero is allowed (free is not invalid). Negative is refused.
Return a list of problem strings. An empty list means the entry is fine.
Add comments explaining each check. Do not implement any other function yet.
```
```text
Explain what this function does in plain language, one sentence per rule. What assumptions
did you make that I did not explicitly ask for?
```

**Implementation — add_appointment**
```text
Implement Task: write add_appointment(appointments, patient_ref, date, category, cost) in
clinic_tracker.py. It must call check_entry first. If check_entry returns any problems, return
the appointments list unchanged — do not add the entry. If it's valid, append a dict with keys
patient_ref, date, category, and cost (as a float) to appointments, then return the list.
Add comments. Do not implement total_by_category, save, load, or build_report yet.
```

**Implementation — total_by_category**
```text
Implement Task: write total_by_category(appointments) in clinic_tracker.py. Return a dict with
one key per valid category (Consultation, Diagnostics, Procedure, Follow-up, Pharmacy), each
starting at 0.0, and add up the cost of every appointment into its matching category. An empty
list of appointments must return all-zero totals, not crash. Add comments. Do not implement
save, load, or build_report yet.
```

**Debugging / root cause**
```text
Here is check_entry: [paste the function]. Here is the check that now fails:
"a cost of exactly zero    expected accepted got refused    FAIL"
Explain the root cause of this failure — don't just give me a fix.
```

**Extending validation to an untested case**
```text
Our CSV loader will hand cost to check_entry as text, e.g. "120.00", not a float. Add a check
to check_entry_checks.py for a cost value arriving as text from a spreadsheet: "120.00"
should be accepted, and "free" should be refused. Show me the two new checks.
```

---

## 5. Troubleshooting quick reference (from the Codex setup guide)

| Symptom | Fix |
|---|---|
| `codex --version` → "command not found" | Close and reopen the terminal/PowerShell window, try again. |
| `cat ~/.codex/config.toml` or `echo $CODEX_LEARNER_KEY` return nothing | Environment variable only loads in new shells: `source ~/.zshrc` (macOS default) or `source ~/.bashrc` (Linux), then retry. |
| VS Code doesn't pick up the new key | Quit VS Code completely (not just the window) and reopen — it caches env vars at startup. |
| Corporate/managed laptop, install fails silently | Check `npm config get prefix` — if it points to `C:\Program Files\`, `/usr/local`, or `/usr`, the learner needs admin/sudo or a user-scope npm prefix (`npm config set prefix "$HOME/.npm-global"`). |
| Corporate laptop, PowerShell blocks the setup script | `Get-ExecutionPolicy -List` — if `MachinePolicy`/`UserPolicy` show `Restricted`/`AllSigned`, Group Policy is blocking it; ask IT, or try `powershell -ExecutionPolicy Bypass -File .\gl-codex-setup.ps1 -LearnerKey "..."`. |
| Corporate laptop, can't reach the proxy | `curl -v https://aibe.mygreatlearning.com/openai/v1/` — a 401/404 means success (reached the server); a timeout or SSL error means the network is blocking/intercepting it — needs an IT allowlist request. |
| Corporate laptop, can't install the VS Code extension | Extensions may be locked down to an allowlist — Codex still works from the terminal in the meantime. |
| `check_entry_checks.py` fails immediately with an import error | Expected before Pass 1 is done — the message tells them to build `check_entry`, save it as `clinic_tracker.py` in the same folder, then re-run. |
| Learner's checks import fails after copying the catch-up file | The catch-up file is named `clinic_tracker_starter.py`; it must be copied/renamed to `clinic_tracker.py` for the `from clinic_tracker import check_entry` import to work (see §3.11 Step 0). |

**Common mistakes to watch for during the session** (from the course's best-practices doc):
prompting for the whole app in one go instead of one scoped task; sending the whole project as
context for a one-line change; accepting generated code without reading or testing it; letting
the AI retry a failing fix repeatedly instead of stepping in after one or two attempts.

---

## 6. Materials — what to hand out, and when

| When | What | Why |
|---|---|---|
| Session start | `starter_pack` **without** `catch_up_release_at_the_break` | Nobody should see the finished `check_entry` before building it themselves. |
| Only if a learner falls behind, at/after the break | `catch_up_release_at_the_break/clinic_tracker_starter.py` | Puts them back on the same footing for Round 2 — opening it earlier means watching instead of doing. |
| End of session | `solution_pack` (finished `clinic_tracker.py`, `clinic_report.py`) | Per the README: learners rebuild one piece on their own afterward and confirm 1,755.75 across seven appointments. |

---

## 7. Open questions for you

1. **Passes 4–5 (save/load, build_report):** I recommended defaulting to running the
   `solution_pack` version live in §3.13 given only 5 minutes are scheduled. If you'd rather
   guarantee hands-on time for those two pieces, you may need to trim §3.9 or §3.10 by a few
   minutes — let me know and I can re-balance the clock.
2. **"Slide 33"** in the starter README refers to your Olympus-hosted deck, which I don't have —
   if it says something more specific than "rebuild one piece, confirm 1,755.75," tell me and
   I'll fold the exact wording into §3.14.
3. Want this trimmed into a **one-page printable cheat sheet** (just §2 and §4) for you to keep
   next to your keyboard during the live session, separate from this full walkthrough?
