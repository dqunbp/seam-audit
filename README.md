# seam-audit

An [Agent Skill](https://agentskills.io) that front-loads contract checking to design time: before writing any code that crosses a module boundary, the agent must enumerate the **seams** (every point where the new code relies on someone else's contract), read the real source of each contract instead of imagining it, and write down `assumption → evidence → enforcement → risk` plus the unhappy paths *with their recovery*.

## Why

Bugs that surface in code review almost never live in the new "core" of a feature. They sit at the seams — where new code meets existing subsystems and external dependencies. Reviewers catch them because in review the real code is in front of you; at design time it's imagined, and the generative mode fills in how the neighbor *probably* looks.

This is an old result. Margaret Hamilton's error analysis of the Apollo flight software found that **~73% of errors were interface errors** — modules disagreeing about data, timing, or control at their boundaries. Her answer was "Development Before the Fact": prevent interface errors at definition time instead of finding them in test. This skill is the informal, evidence-driven version of that idea for coding agents:

- **Read, don't infer** — every assumption about a neighbor's contract must cite what was actually read.
- **Temporal seams are seams** — duplicate, late, concurrent, and missing events are contract violations too (Hamilton's largest error class).
- **Enforce, don't document** — assumptions held only by convention are red flags; lift them to types, validators, or constraints where cheap.
- **Recovery is part of the design** — every unhappy path gets a `failure → reaction → observability` line before coding starts.

## Install

```sh
npx skills add dqunbp/seam-audit
```

Or copy `SKILL.md` into your skills directory (e.g. `~/.claude/skills/seam-audit/SKILL.md` for Claude Code).

## Use

The skill triggers before non-trivial multi-module work ("new feature", "seam audit", "check the seams", "before writing code"). Output is a seam-audit table plus the unhappy-path/recovery list — then implementation proceeds.

## References

- M. Hamilton, W. Hackler, *Universal Systems Language: Lessons Learned from Apollo* (IEEE Computer, 2008) — the interface-error analysis and Development Before the Fact.
- M. Feathers, *Working Effectively with Legacy Code* — the "seam" term.

## License

MIT
