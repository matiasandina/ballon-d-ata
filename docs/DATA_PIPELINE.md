# Data pipeline and reproducibility

## Current flow

`main.py` creates year/URL/table configurations for 1956–2025, excluding 2020. `WebScraper` downloads the relevant Wikipedia page, `TableExtractor` converts one or two HTML tables into rows, and `DataCleaner` normalizes headers, text, ranks, scores, and percentages. The scraper combines the results and writes:

- `data/ballon_dor_all_years.csv`
- `data/ballon_dor_voting_details.csv` (the additional 2003–2006 voting tables)

This is a live-page scraper, not a reproducible source snapshot. A later Wikipedia edit, table-layout change, partial request failure, or changed parsing rule can change the output. Errors in `scrape_year()` are logged and skipped, so a run can finish with missing years. There is no source provenance per row. The committed CSVs are therefore the baseline for this PR; they were not regenerated or edited.

## Install and run offline checks

Python 3.12 or newer and [uv](https://docs.astral.sh/uv/) are required.

```bash
uv sync --frozen --all-groups
uv run pytest
uv run python scripts/audit_data.py --check
```

The check exits non-zero for structural failures such as a schema mismatch, invalid numeric values, or duplicate player-year keys. Known missing data, score/rank questions, and source-verification items are warnings and do not block CI.

Generate the committed reports with:

```bash
uv run python scripts/audit_data.py
```

That command is entirely offline and reads, but does not modify, the CSVs. It writes `reports/data_quality.json` and `reports/data_quality.md`.

## Safely regenerate scraper output for comparison

`main.py` writes fixed relative paths and will overwrite CSVs if run at the repository root. Run it from an isolated directory instead:

```bash
repo_path="$PWD"
scratch_path="$(mktemp -d)"
mkdir -p "$scratch_path/data"
cd "$scratch_path"
uv run --project "$repo_path" python "$repo_path/main.py"
```

This operation requires network access and is intentionally absent from CI. Compare files in `$scratch_path/data/` with the committed baseline; do not copy them back without reviewing every difference and verifying affected source pages.

## Baseline at commit `f566a8e`

| Dataset | Rows | Coverage | Schema |
| --- | ---: | --- | --- |
| Main | 2,095 | 1956–2025; 69 editions, with 2020 absent | `year, rank, player, club, nationality, points, percent, position` |
| Voting detail | 196 | 2003–2006; 49 rows per year | `rank, player, nationality, club, points, 1st, 2nd, 3rd, 4th, 5th, votes, year, percent` |

Neither dataset has a duplicated `(player, year)` combination. Exact per-year counts and field-level missingness are recorded in the generated reports.

## Baseline defects and limitations

The audit confirmed two unsafe transformations in the baseline code:

1. `_clean_numeric_columns()` forward-filled blank points and could copy one player's score to the next player. It now preserves the blank as missing.
2. `clean_multi_year_data()` converted missing points and votes to zero. It now uses pandas nullable integers so zero, missing, and unavailable remain distinct.

Percentage generation also used `sum()` across incomplete score data. It now declines to calculate a year's percentages if any point value is missing. This prevents a recurrence of the 2018 failure mode. These changes affect future scraper runs only; the committed historical CSVs remain unchanged.

Other limitations remain intentionally out of scope: ranking gaps and ties vary by edition, table meanings change across eras, nationality and position are not consistently published, club strings retain the scraper's `~~~` separator, and percentages from the FIFA Ballon d'Or era may have semantics that are not directly derivable from the adjacent `points` field.

## Prioritized follow-up corrections

1. **Verify and restore the 2018 winner score from an authoritative source.** Luka Modrić has blank points and percent; the other 29 percentages were calculated against only their 2,127 points and sum to approximately 100%. After verifying the missing score, recompute or replace the full 2018 percentage set together.
2. **Determine whether 2025 voting scores were published.** All 30 rankings are present, while every points and percent value is blank. Preserve these as unavailable unless a suitable source is identified.
3. **Verify 2013 field semantics and the source rows.** Gareth Bale is rank 9 with 65 points while Andrea Pirlo is rank 10 with 70. Several 2013 stored percentages also do not match a simple points/annual-total calculation. Do not swap ranks, scores, or recompute percentages until the source definitions are established.
4. **Backfill nationality only with source evidence.** It is blank for every row in 2016–2019 and 2021. Decide whether nationality means citizenship, national team, or the label published by the award source before adding values.
5. **Review score/percentage semantics for 2010–2015.** Several years contain percentages but no points, and the calculated consistency rule flags 2013 records. These fields span the FIFA Ballon d'Or format and require source-specific interpretation.

Any historical correction should cite a stable source, include a focused fixture/regression test, and update both generated reports. Decisions about nationality definitions, voting-era schema, tied ranks, and whether an unpublished score is represented as blank rather than a separate status field require manual agreement.
