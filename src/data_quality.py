"""Offline validation and reporting for the committed Ballon d'Or CSV files."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAIN_SCHEMA = ["year", "rank", "player", "club", "nationality", "points", "percent", "position"]
DETAIL_SCHEMA = [
    "rank", "player", "nationality", "club", "points", "1st", "2nd", "3rd",
    "4th", "5th", "votes", "year", "percent",
]
NUMERIC_COLUMNS = {"year", "rank", "points", "percent", "1st", "2nd", "3rd", "4th", "5th", "votes"}
REQUIRED_TEXT = {"player", "club"}


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    path: Path
    schema: list[str]


def _read_csv(spec: DatasetSpec) -> tuple[list[str], list[dict[str, str]]]:
    with spec.path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _number(value: str) -> float | None:
    if value.strip() == "":
        return None
    try:
        number = float(value)
    except ValueError:
        return math.nan
    return number


def _record(code: str, severity: str, message: str, **context: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "severity": severity, "message": message}
    if context:
        result["context"] = context
    return result


def _audit_dataset(spec: DatasetSpec) -> dict[str, Any]:
    header, rows = _read_csv(spec)
    years = Counter(row.get("year", "") for row in rows)
    missing = {column: sum(not row.get(column, "").strip() for row in rows) for column in header}
    issues: list[dict[str, Any]] = []

    if header != spec.schema:
        issues.append(_record("schema_mismatch", "failure", "CSV schema or column order differs from the expected contract.", expected=spec.schema, actual=header))

    duplicate_keys = [
        {"player": player, "year": year, "count": count}
        for (player, year), count in sorted(Counter((r.get("player", ""), r.get("year", "")) for r in rows).items())
        if count > 1
    ]
    if duplicate_keys:
        issues.append(_record("duplicate_player_year", "failure", "Player-year combinations must be unique.", records=duplicate_keys))

    invalid_values: list[dict[str, Any]] = []
    for line, row in enumerate(rows, start=2):
        for column in REQUIRED_TEXT & set(header):
            if not row[column].strip():
                invalid_values.append({"line": line, "column": column, "value": row[column], "reason": "required value is blank"})
        for column in NUMERIC_COLUMNS & set(header):
            value = _number(row[column])
            if value is not None and (math.isnan(value) or math.isinf(value)):
                invalid_values.append({"line": line, "column": column, "value": row[column], "reason": "not a finite number"})
            elif value is not None and column in {"year", "rank", "points", "votes", "1st", "2nd", "3rd", "4th", "5th"} and value < 0:
                invalid_values.append({"line": line, "column": column, "value": row[column], "reason": "negative value"})
            elif value is not None and column == "percent" and not 0 <= value <= 100:
                invalid_values.append({"line": line, "column": column, "value": row[column], "reason": "outside 0..100"})
    if invalid_values:
        issues.append(_record("invalid_value", "failure", "Invalid required or numeric values were found.", records=invalid_values))

    unusual_rankings: list[dict[str, Any]] = []
    by_year: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_year[row.get("year", "")].append(row)
    for year, group in sorted(by_year.items()):
        ranks = [_number(r.get("rank", "")) for r in group]
        bad = [rank for rank in ranks if rank is None or math.isnan(rank) or rank <= 0 or not rank.is_integer()]
        if bad:
            unusual_rankings.append({"year": int(year), "reason": "blank, non-positive, or non-integer rank", "values": bad})
        numeric = [int(rank) for rank in ranks if rank is not None and not math.isnan(rank) and rank > 0 and rank.is_integer()]
        if numeric and numeric != sorted(numeric):
            unusual_rankings.append({"year": int(year), "reason": "ranks are not in ascending file order"})
    if unusual_rankings:
        issues.append(_record("unusual_ranking", "warning", "Rank sequences that may need source verification were found.", records=unusual_rankings))

    coverage = sorted(int(year) for year in years if year.isdigit())
    return {
        "path": str(spec.path),
        "row_count": len(rows),
        "schema": header,
        "year_coverage": {"minimum": min(coverage) if coverage else None, "maximum": max(coverage) if coverage else None, "years": coverage},
        "per_year_counts": {year: years[str(year)] for year in coverage},
        "missing_fields": missing,
        "duplicate_player_year": duplicate_keys,
        "unusual_rankings": unusual_rankings,
        "invalid_values": invalid_values,
        "issues": issues,
        "_rows": rows,
    }


def _main_dataset_findings(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, str]] = dataset["_rows"]
    by_year: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_year[int(row["year"])].append(row)
    findings: list[dict[str, Any]] = []

    missing_nationality = {
        year: sum(not row["nationality"].strip() for row in group)
        for year, group in sorted(by_year.items())
        if any(not row["nationality"].strip() for row in group)
    }
    if missing_nationality:
        findings.append(_record("missing_nationality", "warning", "Nationality is unavailable for some year groups.", per_year=missing_nationality))

    missing_scores = {
        year: {"points": sum(not r["points"].strip() for r in group), "percent": sum(not r["percent"].strip() for r in group)}
        for year, group in sorted(by_year.items())
        if any(not r["points"].strip() or not r["percent"].strip() for r in group)
    }
    if missing_scores:
        findings.append(_record("missing_voting_scores", "warning", "Points and/or percentages are unavailable for some records; blanks are preserved as unavailable, not zero.", per_year=missing_scores))

    inconsistencies: list[dict[str, Any]] = []
    incomplete_totals: list[dict[str, Any]] = []
    for year, group in sorted(by_year.items()):
        points = [_number(r["points"]) for r in group]
        percents = [_number(r["percent"]) for r in group]
        if any(value is None for value in points):
            if any(value is not None for value in percents):
                incomplete_totals.append({
                    "year": year,
                    "missing_points": sum(value is None for value in points),
                    "missing_players": [r["player"] for r, value in zip(group, points) if value is None],
                    "available_percent_sum": round(sum(value for value in percents if value is not None), 4),
                    "reason": "a percentage denominator cannot be validated while points are missing",
                })
            continue
        total = sum(value for value in points if value is not None)
        if total <= 0 or any(value is None for value in percents):
            continue
        for row, point, percent in zip(group, points, percents):
            assert point is not None and percent is not None
            expected = point * 100 / total
            if abs(expected - percent) > 0.05:
                inconsistencies.append({"year": year, "player": row["player"], "points": point, "percent": percent, "calculated_percent": round(expected, 4)})
    if incomplete_totals:
        findings.append(_record("incomplete_percentage_denominator", "confirmed_defect", "Stored percentages coexist with missing points, so totals calculated from this file are incomplete.", records=incomplete_totals))
    if inconsistencies:
        findings.append(_record("points_percentage_inconsistency", "warning", "Stored percentages differ from points divided by the complete annual point total by more than 0.05 percentage points.", records=inconsistencies))

    inversions: list[dict[str, Any]] = []
    for year, group in sorted(by_year.items()):
        ordered = sorted(group, key=lambda r: float(r["rank"]))
        for earlier, later in zip(ordered, ordered[1:]):
            a, b = _number(earlier["points"]), _number(later["points"])
            if a is not None and b is not None and float(earlier["rank"]) < float(later["rank"]) and a < b:
                inversions.append({"year": year, "higher_ranked": earlier["player"], "higher_ranked_points": a, "lower_ranked": later["player"], "lower_ranked_points": b})
    if inversions:
        findings.append(_record("rank_points_inversion", "source_verification", "A lower-ranked player has more points than the preceding higher-ranked player. Ranking and score semantics must be verified before correction.", records=inversions))
    return findings


def build_report(main_path: Path, detail_path: Path) -> dict[str, Any]:
    specs = [DatasetSpec("main", main_path, MAIN_SCHEMA), DatasetSpec("voting_detail", detail_path, DETAIL_SCHEMA)]
    datasets: dict[str, Any] = {}
    all_findings: list[dict[str, Any]] = []
    for spec in specs:
        try:
            audited = _audit_dataset(spec)
        except (FileNotFoundError, OSError) as error:
            datasets[spec.name] = {"path": str(spec.path), "issues": [_record("unreadable_dataset", "failure", str(error))]}
            continue
        datasets[spec.name] = audited
        all_findings.extend(audited["issues"])
    if "main" in datasets and "_rows" in datasets["main"]:
        all_findings.extend(_main_dataset_findings(datasets["main"]))
    for dataset in datasets.values():
        dataset.pop("_rows", None)
    failures = sum(finding["severity"] == "failure" for finding in all_findings)
    warnings = sum(finding["severity"] != "failure" for finding in all_findings)
    return {
        "format_version": 1,
        "summary": {"status": "fail" if failures else "pass_with_warnings" if warnings else "pass", "failure_count": failures, "warning_count": warnings},
        "datasets": datasets,
        "findings": all_findings,
        "known_pipeline_defects": [
            {"code": "points_forward_fill", "severity": "confirmed_defect", "message": "DataCleaner._clean_numeric_columns() forward-fills a missing point value from the preceding player and can assign an incorrect score."},
            {"code": "missing_scores_to_zero", "severity": "confirmed_defect", "message": "DataCleaner.clean_multi_year_data() converts missing points and votes to zero, erasing the distinction between unavailable and zero."},
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Ballon d'Or data-quality audit", "", f"Status: **{report['summary']['status']}** ({report['summary']['failure_count']} failures, {report['summary']['warning_count']} warnings/findings).", ""]
    for name, data in report["datasets"].items():
        lines.extend([f"## {name.replace('_', ' ').title()}", "", f"- File: `{data['path']}`"])
        if "row_count" in data:
            coverage = data["year_coverage"]
            lines.extend([
                f"- Rows: {data['row_count']:,}",
                f"- Coverage: {coverage['minimum']}–{coverage['maximum']} ({len(coverage['years'])} years)",
                f"- Schema: `{', '.join(data['schema'])}`",
                f"- Duplicate player-year combinations: {len(data['duplicate_player_year'])}",
                f"- Invalid values: {len(data['invalid_values'])}",
                f"- Unusual rank sequences: {len(data['unusual_rankings'])}",
                "", "### Per-year row counts", "",
                "| Year | Rows |", "| ---: | ---: |",
                *[f"| {year} | {count} |" for year, count in data["per_year_counts"].items()],
                "", "### Missing fields", "", "| Field | Missing |", "| --- | ---: |",
                *[f"| {field} | {count} |" for field, count in data["missing_fields"].items()],
            ])
        lines.append("")
    lines.extend(["## Findings", ""])
    for finding in report["findings"]:
        lines.append(f"- **{finding['severity']} — `{finding['code']}`:** {finding['message']}")
        context = finding.get("context")
        if context:
            lines.append(f"  - Details: `{json.dumps(context, ensure_ascii=False, sort_keys=True)}`")
    lines.extend(["", "## Known pipeline defects", ""])
    for finding in report["known_pipeline_defects"]:
        lines.append(f"- **{finding['severity']} — `{finding['code']}`:** {finding['message']}")
    lines.extend(["", "Machine-readable details are in `reports/data_quality.json`. Historical values were not repaired by this audit.", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", type=Path, default=Path("data/ballon_dor_all_years.csv"))
    parser.add_argument("--detail", type=Path, default=Path("data/ballon_dor_voting_details.csv"))
    parser.add_argument("--json", type=Path, default=Path("reports/data_quality.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/data_quality.md"))
    parser.add_argument("--check", action="store_true", help="Do not write reports; exit non-zero only for blocking failures.")
    args = parser.parse_args(argv)
    report = build_report(args.main, args.detail)
    if not args.check:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.markdown.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    return 1 if report["summary"]["failure_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
