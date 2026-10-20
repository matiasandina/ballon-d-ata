import csv
from pathlib import Path

import pytest


def test_2018_scores_and_percentages_use_complete_vote_total():
    with Path("data/ballon_dor_all_years.csv").open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["year"] == "2018"]

    assert len(rows) == 30
    assert all(row["points"] and row["percent"] for row in rows)

    total = sum(float(row["points"]) for row in rows)
    winner = next(row for row in rows if row["rank"] == "1.0")

    assert total == 2880
    assert winner["player"] == "Luka Modrić"
    assert float(winner["points"]) == 753
    assert float(winner["percent"]) == pytest.approx(753 / 2880 * 100, abs=0.00005)
    for row in rows:
        assert float(row["percent"]) == pytest.approx(
            float(row["points"]) / total * 100,
            abs=0.00005,
        )


def test_2025_scores_and_percentages_use_complete_vote_total():
    with Path("data/ballon_dor_all_years.csv").open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["year"] == "2025"]

    assert len(rows) == 30
    assert all(row["points"] and row["percent"] for row in rows)

    total = sum(float(row["points"]) for row in rows)
    winner = next(row for row in rows if row["rank"] == "1.0")

    assert total == 6700
    assert winner["player"] == "Ousmane Dembélé"
    assert float(winner["points"]) == 1380
    for row in rows:
        assert float(row["percent"]) == pytest.approx(
            float(row["points"]) / total * 100,
            abs=0.00005,
        )
