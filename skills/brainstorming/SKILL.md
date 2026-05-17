---
name: brainstorming
description: Invoke before ANY creative work — building features, designing components, adding functionality, modifying behavior — to explore intent and requirements BEFORE proposing implementation. Outputs a plan, not code.
---

# When to use

- "Build me a ...", "Add a feature for ...", "Design a ...".
- Before EnterPlanMode for non-trivial implementation tasks.
- When requirements are vague or seemingly simple ("just add a button").
- When you're tempted to start coding "and figure out the details as we go".

# How to execute

## Step 1 — Stop. Do not write code yet.

## Step 2 — Probe intent with the 5 questions
1. **What is the user trying to accomplish?** (Not what they asked for; what is
   the underlying job-to-be-done.)
2. **What's the smallest test of "done"?** (One observable behavior that proves
   the feature works.)
3. **What's the failure mode if we do this wrong?** (What would frustrate them?
   What data could we lose?)
4. **What constraint matters most?** (Time? Quality? Cost? Compatibility?)
5. **What ALREADY exists in this codebase that's close?** (Don't reinvent.)

If you can't answer all 5 from context, ASK the user via AskUserQuestion (Claude
Code) or a clarifying question (Codex / Pi). Do not assume.

## Step 3 — Propose 2-3 distinct approaches
Not one approach with variations. Two-to-three genuinely different solutions.
For each:
- One-paragraph description.
- Main tradeoff (speed vs. quality, generality vs. simplicity, etc.).
- Rough effort (XS / S / M / L / XL).

## Step 4 — Recommend one with a tradeoff statement
"I recommend option B because [primary reason]. The cost is [explicit trade]."

## Step 5 — Wait for the user's pick BEFORE coding
Even when one option is obviously best — naming the tradeoff out loud surfaces
hidden constraints. Only after the user picks (or explicitly says "go with your
recommendation") does implementation begin.

# Output shape
A short markdown block with:
- 1-line restatement of intent.
- 2-3 approaches, each with tradeoff + effort.
- Your recommendation.
- An invitation to pick or push back.

# Anti-patterns (refuse)
- Skipping straight to implementation.
- Presenting one option as a menu of variations.
- Hiding the tradeoff ("it's just better").
- Writing > 50 lines of code without an approved approach.
