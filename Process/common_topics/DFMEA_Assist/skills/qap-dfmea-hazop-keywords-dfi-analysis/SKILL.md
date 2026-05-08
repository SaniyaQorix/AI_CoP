---
name: qap-dfmea-hazop-keywords-dfi-analysis
description: "Use when: selecting/validating HAZOP keywords and DFIs for DFMEA failure scenarios using code/design evidence."
argument-hint: "Failure mode/cause context; expected output is one or more Safety_Analysis `HAZOP Keywords/<DFI>` values"
user-invocable: true
---
# QAP DFMEA — HAZOP Keywords and DFI Mapping
## When to Use
- Use when mapping DFMEA failure modes/causes to a HAZOP keyword and a DFI identifier.
- Use when reviewing whether the selected HAZOP keyword/DFI is consistent with code/design evidence.
## Catalog (JSON)
- Canonical catalog: [hazop_dfi_catalog.json](./assets/hazop_dfi_catalog.json)
- Use only the listed HAZOP keywords and DFIs unless the user explicitly extends the catalog.

## Mandatory Coverage Checks
- For each analyzed function/member, screen every HAZOP keyword and every DFI from the catalog.
- When two or more HAZOP keywords produce no distinct failure scenario for the same function/member, place all of them in one consolidated no-failure row; do not omit non-applicable HAZOP keywords.
- When two or more DFIs produce no distinct failure scenario for the same function/member, place all of them in one consolidated no-failure row; do not omit non-applicable DFIs.
- Explicitly assess re-entrancy and thread-safety for every function/member. DFI_1 must be considered for shared mutable state, concurrent callers, re-entrant callbacks or signal handlers, move/destruction races, unsynchronized ownership transfer, and context switching.
- Where concurrency can destabilize state or data, also consider applicable HAZOP keywords such as `UNSTABLE` and `CORRUPT`; if no concurrency-related scenario applies, include the corresponding DFI or HAZOP item in the appropriate consolidated no-failure row instead of omitting it.

## Output Convention
- Update `DFMEA Analysis[].Failure Analysis[].HAZOP Keywords/<DFI>`.
- For a unique failure scenario, preferred value formats are `<HAZOP keyword>` or `<DFI identifier>` depending on the evidence.
- Follow the agent's `Safety_Analysis JSON Update Rules (determinism)` section for row splitting and aggregate no-failure merge handling.
## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- `DFMEA Analysis[].Failure Analysis[].HAZOP Keywords/<DFI>`
