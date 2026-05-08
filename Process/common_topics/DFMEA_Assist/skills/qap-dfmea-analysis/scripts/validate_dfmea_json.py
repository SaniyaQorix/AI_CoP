# (c) Qorix 2026
"""Validate deterministic DFMEA Stage 1 invariants for Safety_Analysis JSON.

This validator focuses on the invariants enforced by the live DFMEA agent and
its supporting skills before JSON review or Excel synchronization. Structural
violations are reported as blocking errors. Semantic checks that cannot be
proven purely from structure are reported as heuristic warnings.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Set, Tuple


TRIAD_KEYS: Tuple[str, ...] = (
    "Potential Failure Mode",
    "Potential Effect of Failure",
    "Potential Causes of Failure",
)

STAGE1_NA_KEYS: Tuple[str, ...] = (
    "Current Failure Prevention Mechanisms",
    "Current Failure Detection Mechanisms",
    "Design Traceability",
    "Requirement Traceability",
    "Safety/Non Safety",
)

DESIGN_ID_PATTERN = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*_SDD_[0-9]{4}$")

USER_PERSPECTIVE_TERMS: Tuple[str, ...] = (
    "application",
    "caller",
    "user",
    "client",
    "consumer",
    "process",
    "thread",
    "downstream",
    "observer",
)

MULTI_SCENARIO_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\band/or\b", re.IGNORECASE),
    re.compile(r"\beither\b", re.IGNORECASE),
    re.compile(r"\balternatively\b", re.IGNORECASE),
    re.compile(r",\s+or\s+", re.IGNORECASE),
    re.compile(r";"),
)

MECHANISM_LANGUAGE_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bmitigated by\b", re.IGNORECASE),
    re.compile(r"\bdetected by\b", re.IGNORECASE),
    re.compile(r"\bprevented by\b", re.IGNORECASE),
    re.compile(r"\bprotected by\b", re.IGNORECASE),
    re.compile(r"\bhandled by\b", re.IGNORECASE),
    re.compile(r"\bguarded by\b", re.IGNORECASE),
    re.compile(r"\bSM_[0-9]+\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class Finding:
    """One validation finding emitted by the DFMEA invariant checker.

    Attributes:
        level: Severity of the finding. `error` blocks downstream workflow,
            while `warning` flags a heuristic checklist concern.
        code: Stable machine-readable identifier for the rule.
        function: Name of the DFMEA function entry.
        row: One-based failure-row index within the function entry.
        message: Human-readable explanation of the issue.
    """

    level: str
    code: str
    function: str
    row: int
    message: str


@dataclass(frozen=True)
class ValidationSummary:
    """Aggregate validation result for one DFMEA JSON document."""

    functions_checked: int
    error_count: int
    warning_count: int


def _normalize_text(value: Any) -> str:
    """Convert any cell-like value to collapsed text.

    Args:
        value: Arbitrary JSON value.

    Returns:
        A trimmed string with internal whitespace collapsed to single spaces.
    """

    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _normalized_value(value: Any) -> str:
    """Return lower-cased normalized text for rule comparisons."""

    return _normalize_text(value).lower()


def _normalize_hazop_token(token: str) -> str:
    """Normalize a HAZOP keyword to the catalog representation.

    Args:
        token: Raw token taken from `HAZOP Keywords/<DFI>`.

    Returns:
        Upper-cased token with canonical slash spacing.
    """

    normalized = _normalize_text(token).upper()
    normalized = re.sub(r"\s*/\s*", " / ", normalized)
    return normalized


def _normalize_catalog_hazop_keywords(keywords: Iterable[str]) -> Set[str]:
    """Normalize the HAZOP keyword set loaded from the catalog."""

    return {_normalize_hazop_token(keyword) for keyword in keywords}


def _split_keyword_tokens(raw_value: Any) -> List[str]:
    """Split a DFMEA keyword field into individual catalog tokens.

    Args:
        raw_value: Raw `HAZOP Keywords/<DFI>` field value.

    Returns:
        A list of normalized tokens.
    """

    text = _normalize_text(raw_value)
    if not text:
        return []

    tokens = [token.strip() for token in text.split(",") if token.strip()]
    normalized_tokens: List[str] = []
    for token in tokens:
        if token.upper().startswith("DFI_"):
            normalized_tokens.append(token.upper())
        else:
            normalized_tokens.append(_normalize_hazop_token(token))
    return normalized_tokens


def _default_catalog_path() -> Path:
    """Return the default HAZOP/DFI catalog path used by the DFMEA skills."""

    return (
        Path(__file__).resolve().parents[2]
        / "qap-dfmea-hazop-keywords-dfi-analysis"
        / "assets"
        / "hazop_dfi_catalog.json"
    )


def _load_catalog(catalog_path: Path) -> Tuple[Set[str], Set[str]]:
    """Load the canonical HAZOP and DFI sets from the shared catalog.

    Args:
        catalog_path: Path to `hazop_dfi_catalog.json`.

    Returns:
        Two sets: normalized HAZOP keywords and DFI identifiers.
    """

    document = json.loads(catalog_path.read_text(encoding="utf-8"))
    hazop_keywords = _normalize_catalog_hazop_keywords(
        entry["keyword"] for entry in document["hazop"]["keywords"]
    )
    dfi_identifiers = {
        _normalize_text(entry["identifier"]).upper()
        for entry in document["dfi"]["definitions"]
    }
    return hazop_keywords, dfi_identifiers


def _read_dfmea_json(json_path: Path) -> Dict[str, Any]:
    """Read the canonical DFMEA JSON document from disk.

    Args:
        json_path: Path to the DFMEA JSON file.

    Returns:
        Parsed JSON object.

    Raises:
        ValueError: If the top-level JSON shape is incompatible.
    """

    document = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("DFMEA JSON must be a JSON object.")
    analysis = document.get("DFMEA Analysis")
    if not isinstance(analysis, list):
        raise ValueError("DFMEA JSON must contain a list under 'DFMEA Analysis'.")
    return document


def _classify_tokens(
    tokens: Sequence[str],
    hazop_keywords: Set[str],
    dfi_identifiers: Set[str],
) -> Tuple[str, List[str]]:
    """Classify one keyword field as HAZOP, DFI, mixed, or invalid.

    Args:
        tokens: Normalized tokens from one row.
        hazop_keywords: Valid HAZOP set.
        dfi_identifiers: Valid DFI set.

    Returns:
        A pair of `(classification, invalid_tokens)`.
    """

    invalid_tokens = [
        token for token in tokens if token not in hazop_keywords and token not in dfi_identifiers
    ]
    if invalid_tokens:
        return "invalid", invalid_tokens

    has_hazop = any(token in hazop_keywords for token in tokens)
    has_dfi = any(token in dfi_identifiers for token in tokens)
    if has_hazop and has_dfi:
        return "mixed", []
    if has_hazop:
        return "hazop", []
    if has_dfi:
        return "dfi", []
    return "invalid", []


def _row_has_none_triad(row: Dict[str, Any]) -> Tuple[bool, bool]:
    """Determine whether the Stage 1 triad represents a `None` scenario.

    Returns:
        Tuple of `(all_none, partial_none)`.
    """

    values = [_normalized_value(row.get(key, "")) for key in TRIAD_KEYS]
    all_none = all(value == "none" for value in values)
    partial_none = any(value == "none" for value in values) and not all_none
    return all_none, partial_none


def _validate_none_row_fields(
    findings: List[Finding],
    function_name: str,
    row_index: int,
    row: Dict[str, Any],
) -> None:
    """Validate Stage 1 `NA` propagation for a `None` triad row."""

    for key in STAGE1_NA_KEYS:
        if _normalized_value(row.get(key, "")) != "na":
            findings.append(
                Finding(
                    level="error",
                    code="none-row-stage1-na",
                    function=function_name,
                    row=row_index,
                    message=f"Field '{key}' must be 'NA' when the failure mode/effect/cause triad is 'None'.",
                )
            )


def _validate_design_traceability(
    findings: List[Finding],
    function_name: str,
    row_index: int,
    row: Dict[str, Any],
) -> None:
    """Validate design traceability IDs for non-`None` rows."""

    raw_traceability = _normalize_text(row.get("Design Traceability", ""))
    if not raw_traceability or _normalized_value(raw_traceability) == "na":
        findings.append(
            Finding(
                level="error",
                code="design-traceability-missing",
                function=function_name,
                row=row_index,
                message="Non-'None' failure rows must contain explicit design IDs in Design Traceability.",
            )
        )
        return

    entries = [entry.strip() for entry in raw_traceability.split(",") if entry.strip()]
    for entry in entries:
        if not DESIGN_ID_PATTERN.fullmatch(entry):
            findings.append(
                Finding(
                    level="error",
                    code="design-traceability-format",
                    function=function_name,
                    row=row_index,
                    message=(
                        "Design Traceability must contain only explicit design IDs in the "
                        f"format <FC/MID>_SDD_NNNN. Invalid entry: '{entry}'."
                    ),
                )
            )


def _check_effect_perspective(
    findings: List[Finding],
    function_name: str,
    row_index: int,
    effect_text: str,
) -> None:
    """Emit a warning when the effect text may not be user-facing."""

    lowered = effect_text.lower()
    if any(term in lowered for term in USER_PERSPECTIVE_TERMS):
        return
    findings.append(
        Finding(
            level="warning",
            code="effect-perspective-heuristic",
            function=function_name,
            row=row_index,
            message=(
                "Potential Effect of Failure may not be written from the direct user or caller perspective. "
                "Review the wording manually."
            ),
        )
    )


def _check_multi_scenario_text(
    findings: List[Finding],
    function_name: str,
    row_index: int,
    field_name: str,
    field_text: str,
) -> None:
    """Emit a warning when one field appears to combine multiple scenarios."""

    if any(pattern.search(field_text) for pattern in MULTI_SCENARIO_PATTERNS):
        findings.append(
            Finding(
                level="warning",
                code="multi-scenario-heuristic",
                function=function_name,
                row=row_index,
                message=(
                    f"Field '{field_name}' may combine multiple scenarios in one row. "
                    "Review whether the row should be split further."
                ),
            )
        )


def _check_mechanism_language(
    findings: List[Finding],
    function_name: str,
    row_index: int,
    field_name: str,
    field_text: str,
) -> None:
    """Emit a warning when Stage 1 text appears to reference mechanisms."""

    if any(pattern.search(field_text) for pattern in MECHANISM_LANGUAGE_PATTERNS):
        findings.append(
            Finding(
                level="warning",
                code="mechanism-language-heuristic",
                function=function_name,
                row=row_index,
                message=(
                    f"Field '{field_name}' may reference prevention or detection mechanisms. "
                    "Review whether the row is still mechanism-independent."
                ),
            )
        )


def _validate_function_entry(
    function_entry: Dict[str, Any],
    hazop_keywords: Set[str],
    dfi_identifiers: Set[str],
) -> List[Finding]:
    """Validate one function-level DFMEA entry against Stage 1 invariants."""

    findings: List[Finding] = []
    function_name = _normalize_text(function_entry.get("Function", "")) or "<missing Function>"
    raw_rows = function_entry.get("Failure Analysis")
    if not isinstance(raw_rows, list) or not raw_rows:
        return [
            Finding(
                level="error",
                code="missing-failure-analysis",
                function=function_name,
                row=0,
                message="Function entry must contain a non-empty 'Failure Analysis' list.",
            )
        ]

    hazop_failure_tokens: Set[str] = set()
    hazop_none_tokens: Set[str] = set()
    dfi_failure_tokens: Set[str] = set()
    dfi_none_tokens: Set[str] = set()
    hazop_none_row_count = 0
    dfi_none_row_count = 0

    for row_index, raw_row in enumerate(raw_rows, start=1):
        if not isinstance(raw_row, dict):
            findings.append(
                Finding(
                    level="error",
                    code="row-not-object",
                    function=function_name,
                    row=row_index,
                    message="Each Failure Analysis row must be a JSON object.",
                )
            )
            continue

        tokens = _split_keyword_tokens(raw_row.get("HAZOP Keywords/<DFI>", ""))
        if not tokens:
            findings.append(
                Finding(
                    level="error",
                    code="missing-keywords",
                    function=function_name,
                    row=row_index,
                    message="Row is missing HAZOP or DFI tokens in 'HAZOP Keywords/<DFI>'.",
                )
            )
            continue

        classification, invalid_tokens = _classify_tokens(tokens, hazop_keywords, dfi_identifiers)
        if classification == "invalid":
            detail = ", ".join(invalid_tokens) if invalid_tokens else "unknown tokens"
            findings.append(
                Finding(
                    level="error",
                    code="invalid-keywords",
                    function=function_name,
                    row=row_index,
                    message=f"Row contains invalid HAZOP/DFI tokens: {detail}.",
                )
            )
            continue

        if classification == "mixed":
            findings.append(
                Finding(
                    level="error",
                    code="mixed-keyword-types",
                    function=function_name,
                    row=row_index,
                    message="One row may contain either HAZOP keywords or DFI identifiers, but not both.",
                )
            )
            continue

        all_none, partial_none = _row_has_none_triad(raw_row)
        if partial_none:
            findings.append(
                Finding(
                    level="error",
                    code="partial-none-triad",
                    function=function_name,
                    row=row_index,
                    message="Failure mode/effect/cause must either all be 'None' or all describe a concrete scenario.",
                )
            )

        if all_none:
            _validate_none_row_fields(findings, function_name, row_index, raw_row)
            if classification == "hazop":
                hazop_none_row_count += 1
                hazop_none_tokens.update(tokens)
            else:
                dfi_none_row_count += 1
                dfi_none_tokens.update(tokens)
            continue

        if classification == "hazop":
            hazop_failure_tokens.update(tokens)
        else:
            dfi_failure_tokens.update(tokens)

        _validate_design_traceability(findings, function_name, row_index, raw_row)

        for field_name in TRIAD_KEYS:
            field_text = _normalize_text(raw_row.get(field_name, ""))
            if not field_text:
                findings.append(
                    Finding(
                        level="error",
                        code="missing-triad-field",
                        function=function_name,
                        row=row_index,
                        message=f"Field '{field_name}' must not be empty on a concrete failure row.",
                    )
                )
                continue

            _check_multi_scenario_text(findings, function_name, row_index, field_name, field_text)
            _check_mechanism_language(findings, function_name, row_index, field_name, field_text)

            if field_name == "Potential Effect of Failure":
                _check_effect_perspective(findings, function_name, row_index, field_text)

    missing_hazop = hazop_keywords - (hazop_failure_tokens | hazop_none_tokens)
    if missing_hazop:
        findings.append(
            Finding(
                level="error",
                code="hazop-coverage-missing",
                function=function_name,
                row=0,
                message=(
                    "Function is missing explicit HAZOP coverage decisions for: "
                    + ", ".join(sorted(missing_hazop))
                    + "."
                ),
            )
        )

    missing_dfi = dfi_identifiers - (dfi_failure_tokens | dfi_none_tokens)
    if missing_dfi:
        findings.append(
            Finding(
                level="error",
                code="dfi-coverage-missing",
                function=function_name,
                row=0,
                message=(
                    "Function is missing explicit DFI coverage decisions for: "
                    + ", ".join(sorted(missing_dfi))
                    + "."
                ),
            )
        )

    if hazop_none_row_count > 1:
        findings.append(
            Finding(
                level="error",
                code="hazop-none-row-count",
                function=function_name,
                row=0,
                message="At most one aggregate HAZOP no-failure row is allowed per function entry.",
            )
        )

    if dfi_none_row_count > 1:
        findings.append(
            Finding(
                level="error",
                code="dfi-none-row-count",
                function=function_name,
                row=0,
                message="At most one aggregate DFI no-failure row is allowed per function entry.",
            )
        )

    overlapping_hazop = hazop_failure_tokens & hazop_none_tokens
    if overlapping_hazop:
        findings.append(
            Finding(
                level="error",
                code="hazop-overlap-none",
                function=function_name,
                row=0,
                message=(
                    "These HAZOP keywords appear in both concrete-failure rows and the aggregate no-failure row: "
                    + ", ".join(sorted(overlapping_hazop))
                    + "."
                ),
            )
        )

    overlapping_dfi = dfi_failure_tokens & dfi_none_tokens
    if overlapping_dfi:
        findings.append(
            Finding(
                level="error",
                code="dfi-overlap-none",
                function=function_name,
                row=0,
                message=(
                    "These DFI identifiers appear in both concrete-failure rows and the aggregate no-failure row: "
                    + ", ".join(sorted(overlapping_dfi))
                    + "."
                ),
            )
        )

    return findings


def validate_dfmea_document(
    json_path: Path,
    catalog_path: Path,
) -> Tuple[ValidationSummary, List[Finding]]:
    """Validate one DFMEA JSON document and return findings.

    Args:
        json_path: Path to the DFMEA JSON file.
        catalog_path: Path to the canonical HAZOP/DFI catalog.

    Returns:
        A summary object and a flat list of findings.
    """

    document = _read_dfmea_json(json_path)
    hazop_keywords, dfi_identifiers = _load_catalog(catalog_path)
    analysis_entries = document.get("DFMEA Analysis", [])

    findings: List[Finding] = []
    for raw_function_entry in analysis_entries:
        if not isinstance(raw_function_entry, dict):
            findings.append(
                Finding(
                    level="error",
                    code="function-entry-not-object",
                    function="<document>",
                    row=0,
                    message="Each item in 'DFMEA Analysis' must be a JSON object.",
                )
            )
            continue
        findings.extend(_validate_function_entry(raw_function_entry, hazop_keywords, dfi_identifiers))

    error_count = sum(1 for finding in findings if finding.level == "error")
    warning_count = sum(1 for finding in findings if finding.level == "warning")
    summary = ValidationSummary(
        functions_checked=len(analysis_entries),
        error_count=error_count,
        warning_count=warning_count,
    )
    return summary, findings


def _format_text_output(summary: ValidationSummary, findings: Sequence[Finding]) -> str:
    """Render the validation result in a compact human-readable format."""

    lines = [
        "DFMEA validation summary:",
        f"  Functions checked: {summary.functions_checked}",
        f"  Errors: {summary.error_count}",
        f"  Warnings: {summary.warning_count}",
    ]
    if not findings:
        lines.append("  Result: PASS")
        return "\n".join(lines)

    lines.append("")
    for finding in findings:
        row_suffix = f" row {finding.row}" if finding.row > 0 else ""
        lines.append(
            f"{finding.level.upper()} [{finding.code}] {finding.function}{row_suffix}: {finding.message}"
        )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser for the DFMEA validator."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate deterministic Stage 1 invariants for a canonical Safety_Analysis_DFMEA JSON document."
        )
    )
    parser.add_argument(
        "--json",
        dest="json_path",
        required=True,
        type=Path,
        help="Path to the canonical DFMEA JSON file to validate.",
    )
    parser.add_argument(
        "--catalog",
        dest="catalog_path",
        default=_default_catalog_path(),
        type=Path,
        help="Optional path to hazop_dfi_catalog.json. Defaults to the shared DFMEA catalog.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Return a failing exit code when warnings are present.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI entry point for DFMEA invariant validation."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        summary, findings = validate_dfmea_document(args.json_path, args.catalog_path)
    except Exception as exc:  # pragma: no cover - CLI safety net
        print(f"Validation failed to run: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        payload = {
            "summary": asdict(summary),
            "findings": [asdict(finding) for finding in findings],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(_format_text_output(summary, findings))

    if summary.error_count > 0:
        return 1
    if args.fail_on_warning and summary.warning_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())