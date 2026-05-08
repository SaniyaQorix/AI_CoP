---
name: qap-dfmea-safety-mechanism-analysis
description: "Use when: judging the effectiveness of available safety mechanisms from design/code evidence and identifying prevention or detection gaps for each DFMEA failure mode."
argument-hint: "Design and code inputs, failure mode list or DFMEA JSON, output target (DFMEA JSON)"
user-invocable: true
---

# QAP DFMEA — Safety Mechanism Analysis
## Input
- Design
- Code

## Purpose
- Judge the effectiveness of currently available safety mechanisms based on design quality and verification evidence.
- Identify gaps in existing safety mechanisms for each analyzed failure mode.

## Catalog (JSON)
- Canonical catalog: `assets/standard_safety_mechanisms.json`
- Use this catalog as the baseline checklist for standard prevention and detection mechanisms that should be considered during analysis.

## Output Convention
- Reference standard mechanisms using the exact catalog identifier followed by the mechanism text specific to the analyzed scenario.
- Required value format: `<SM_ID> <Mechanism specific to scenario>`.
- Do not use only the generic catalog description when a scenario-specific mechanism statement can be written.
- When multiple mechanisms apply in the same DFMEA field, separate entries with `;`.
- Examples: `SM_01 Null check before dereferencing ara::com service handle`; `SM_02 Range check on input timestamp`; `SM_06 Deadline monitoring on periodic execution path; SM_10 Watchdog supervision of execution flow`.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- `DFMEA Analysis[].Failure Analysis[].Current Failure Prevention Mechanisms`
- `DFMEA Analysis[].Failure Analysis[].Current Failure Detection Mechanisms`
