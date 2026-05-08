---
name: qap-dfmea-failure-mode-analysis
description: "Use when: determining possible failures from design/code using HAZOP keywords or DFIs and deriving unique cause-effect relationships for modules in a Qorix Adaptive AUTOSAR DFMEA."
argument-hint: "Design and code inputs, function/member context, output target (DFMEA JSON)"
user-invocable: true
---
# QAP DFMEA — Failure Mode Analysis
## Input
- Design 
- Code

## Purpose
- Determine possible failures using HAZOP keywords/DFI and recognize cause-effect relationships for modules.
- Derive failures or malfunctions from functions, including no function, unintended function, time deviation, and impermissible effects.
- Focus the DFMEA on identifying causes due to random failures arising from incorrect use of modules in the integrated environment and/or hardware (OS only).
- Write `Potential Effect of Failure` from the perspective of the direct API user, caller, or consumer.
- Derive `Potential Failure Mode`, `Potential Effect of Failure`, and `Potential Causes of Failure` from design intent and implementation characteristics, independent of current prevention, detection, or mitigation mechanisms.

## Central Row Construction Rule
- Follow the agent's `Safety_Analysis JSON Update Rules (determinism)` section for unique-row splitting and aggregate no-failure row handling.
- Work jointly with `/qap-dfmea-hazop-keywords-dfi-analysis` so the HAZOP/DFI selection and the failure/effect/cause fields stay one-to-one per unique scenario.
- One row must describe one unique failure mode/effect/cause chain. Do not combine multiple alternative causes, multiple alternative user-visible effects, or multiple concurrency hazards in one row.
- If the same HAZOP keyword or DFI yields multiple distinct causes or multiple distinct user-visible effects, split them into separate rows even when the failure mode wording is similar.
- Use the `None` triad only for an aggregate no-failure row where no distinct failure scenario exists.
- For every function/member, explicitly analyze re-entrancy and thread-safety failure scenarios using code/design evidence of shared mutable state, unsynchronized ownership changes, concurrent execution contexts, callbacks, signal paths, and context switching.

## Output
- Cause-Effect relationships (failure net)

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- `DFMEA Analysis[].Failure Analysis[].Potential Failure Mode`
- `DFMEA Analysis[].Failure Analysis[].Potential Effect of Failure`
- `DFMEA Analysis[].Failure Analysis[].Potential Causes of Failure`
