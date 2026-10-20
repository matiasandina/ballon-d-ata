import csv
from pathlib import Path

from src.data_quality import DETAIL_SCHEMA, MAIN_SCHEMA, build_report


def write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def test_audit_separates_warnings_from_blocking_failures(tmp_path):
    main = tmp_path / "main.csv"
    detail = tmp_path / "detail.csv"
    write_csv(main, MAIN_SCHEMA, [[2024, 1, "Ada", "One", "A", "", "", "Forward"]])
    write_csv(detail, DETAIL_SCHEMA, [[1, "Ada", "A", "One", 0, "", "", "", "", "", 0, 2004, 0]])

    report = build_report(main, detail)

    assert report["summary"]["failure_count"] == 0
    assert report["summary"]["warning_count"] > 0
    assert report["summary"]["status"] == "pass_with_warnings"


def test_duplicate_player_year_is_a_blocking_failure(tmp_path):
    main = tmp_path / "main.csv"
    detail = tmp_path / "detail.csv"
    row = [2024, 1, "Ada", "One", "A", 10, 100, "Forward"]
    write_csv(main, MAIN_SCHEMA, [row, row])
    write_csv(detail, DETAIL_SCHEMA, [])

    report = build_report(main, detail)

    assert report["summary"]["status"] == "fail"
    assert any(item["code"] == "duplicate_player_year" for item in report["findings"])
