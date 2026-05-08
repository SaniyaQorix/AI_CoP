---
name: qap-dfmea-code-analysis
description: "Use when: analyzing implementation code under the canonical module folder to identify DFMEA-relevant feature-scoped functions/members and gather failure and safety-mechanism evidence (Qorix Adaptive AUTOSAR)."
argument-hint: "Module root or FC/MID, feature or functional cluster scope, list of functions/members or public interfaces (optional), coding language (C++), optional daemon evidence output for Stage 1"
user-invocable: true
---

# QAP DFMEA — Code Analysis
## Input
- Canonical module root `./<fc>/` or `./<fc>/<mid>/`
- Source code under `dev/`
- Optional feature, function/member, public interface, or failure scenario context
- Use `/qap-dfmea-folder-structure` when the canonical module root or artifact path must be inferred.

## Build Context
- The module build system is a mix of Conan and CMake.
- Inspect Conan manifests, CMake build definitions, toolchain files, presets, and generated build inputs to understand module composition, dependencies, compile units, and interface exposure.

## Purpose
- For daemons, provide implementation evidence in the exact `Function`, `Function Description`, and `Functional Parameters` form used by `Safety_Analysis_DFMEA` so `/qap-dfmea-stage-1-analysis` can update those fields consistently for the functions/members selected under the agent's central rules.
- Gather implementation evidence for failure modes, causes, prevention mechanisms, detection mechanisms, and re-entrancy or thread-safety hazards.

## Extraction Focus
- Public API or service interfaces exposed by the module.
- Functions/members selected for analysis by `/qap-dfmea-stage-1-analysis` under the agent's `Safety_Analysis JSON Update Rules (determinism)` section.
- Inputs, outputs, parameters, and configuration that define interface behavior.
- Resource handling, timing behavior, state handling, error handling, and dependency interactions relevant to failure scenarios.
- Shared mutable state, object lifetime transfer, destructor interactions, callback or signal re-entry paths, synchronization primitives or their absence, and any code reachable from multiple execution contexts.

## Stage 1 Daemon Evidence Shape
- Provide one evidence item per daemon function/member in the following exact structure:
	- `Function`: exact daemon function/member name as it should appear in the live sheet.
	- `Function Description`: concise interface responsibility or behavioral summary as it should appear in the live sheet.
	- `Functional Parameters`: exact signature, method contract, or concise parameter/return form as it should appear in the live sheet.
- Use implementation signatures, call contracts, and data-flow evidence to keep these three fields aligned with the live workbook format.
- This skill remains an evidence provider only; `/qap-dfmea-stage-1-analysis` performs the actual DFMEA JSON update.

## Owned DFMEA JSON Keys (Safety_Analysis_DFMEA)
- None (evidence provider). This skill supports Stage 1 with daemon interface identification and supports downstream failure and safety-mechanism analysis with implementation evidence.
