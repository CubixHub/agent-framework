# Red Flags — Rationalisation Patterns

The agent will reach for these to skip the protocol. Each is listed with its reality check. Refuse each on sight.

## The "simple question" dodge

> "This is just a simple question. I don't need a skill for this."

**Reality check.** Simple questions still have skills. A "should I use a Map or an object?" question may match a `data-structures-rules` skill or a `typescript-types` skill. The protocol cost is one `find` call and a paragraph of reading. The cost of skipping it is inconsistent answers across sessions.

**Rule.** Run the match anyway. If no skill matches, fine — but you have to *check*, not assume.

## The "context first" dodge

> "Let me read a few files to get context, then I'll decide on a skill."

**Reality check.** Many skills explicitly forbid reading the codebase before a discovery step. The `brainstorming` skill, for instance, requires asking framing questions BEFORE inspecting code, because reading code anchors the agent on the existing approach. By reading first, you have already executed an anti-pattern of a skill that has not yet been chosen.

**Rule.** Discovery happens on the user's message alone. File-reading is a tool call, and the protocol forbids tool calls before announcement.

## The "obvious answer" dodge

> "The user is asking for X. I know how to do X. Let me just do it."

**Reality check.** This is the failure mode the protocol exists to prevent. Direct execution from intuition produces results that vary session-to-session. Skills exist to make the agent's behaviour *repeatable* and *opinionated*. The version of "X" you would freehand is rarely the version the framework wants.

**Rule.** If you "know how to do X", then there is a skill for X, and you should invoke it. The skill is the agent's institutional memory of how this framework does X.

## The "near miss" dodge

> "None of the skills look quite right. The closest one is X but it's not exactly what's being asked. I'll just wing it."

**Reality check.** "Wing it" is a euphemism for "produce work that no skill governs". The protocol's third branch is `skill-creator`, not freelancing. If no skill matches, the answer is *create one* — not skip the protocol.

**Rule.** When no skill matches above 30%, invoke `skill-creator`. The output of the protocol must be a skill invocation.

## The "user didn't ask for a skill" dodge

> "The user just wants the task done. They didn't say `use a skill`. I'll just do it."

**Reality check.** Users do not know which skills exist. They are not asking for a skill; they are asking for an outcome. The protocol decides *how* to produce the outcome consistently. The user's silence about skills is not consent to skip them.

**Rule.** The protocol runs on every turn that involves action. The user's framing of the request is irrelevant.

## The "I already chose" dodge

> "I'm already mid-task. I made my choice. Don't re-discover."

**Reality check.** Re-discovery within a continuing turn of an invoked skill is wrong — but the trigger for the dodge is usually different: the agent invoked a skill, finished it, and is now starting a *new* sub-task without re-running discovery. The new sub-task is a new turn and the protocol applies again.

**Rule.** Discovery runs at the start of every distinct user-facing task. A task that has shifted (build → debug, write → test) is a new task. Re-discover.

## The "this is faster" dodge

> "Reading frontmatter for 20 skills will cost more tokens than just doing the work."

**Reality check.** Frontmatter is 4–6 lines per skill. 20 skills × 5 lines = 100 lines of context. The marginal cost is trivial; the marginal benefit is consistent agent behaviour. The dodge is also self-defeating: if the work could be done in fewer tokens than the discovery step, the work is too small to need a skill, and the discovery would return "no match" cheaply.

**Rule.** Discovery is cheap. Skipping it is expensive. Cost is not a valid reason.

## The "I'll add it to the skill later" dodge

> "I'll do this freehand for now and update the skill afterwards."

**Reality check.** "Later" is "never". The framework grows by capturing patterns into skills as they emerge. If the pattern is happening now, the skill should govern it now.

**Rule.** Either invoke an existing skill or invoke `skill-creator`. There is no "do it freehand and document later" path.

---

## How to refuse a dodge in flight

When the agent catches itself rationalising, the response is:

1. **Stop the in-progress action.** Do not commit, do not produce output.
2. **Announce the dodge.** "I was about to skip discovery — running protocol now."
3. **Re-enter at Step 1.** List skills, score, invoke.
4. **Note the dodge.** Optionally log to memory which dodge pattern triggered, so the protocol can be tightened next session.

The user benefits from seeing the agent catch and correct itself; they do not benefit from the dodge succeeding silently.
