---
name: qap-dfmea-stage-3-analysis
description: "Use when: executing DFMEA Stage 3 (action taken, closure evidence, traceability, status, remarks)."
argument-hint: "Recommended actions list (or DFMEA JSON), implementation evidence, updated artifact links, status values"
user-invocable: true
---

# QAP DFMEA — Stage 3 Analysis
- When the agent is processing multiple features or full-module scope, operate on the current feature batch only; the agent is responsible for iterating feature-by-feature.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- `DFMEA Analysis[].Failure Analysis[].Action Taken for the Recommendations`
- `DFMEA Analysis[].Failure Analysis[].Traceability`
- `DFMEA Analysis[].Failure Analysis[].Status`
- `DFMEA Analysis[].Failure Analysis[].Remarks`
