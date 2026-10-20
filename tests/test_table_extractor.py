from pathlib import Path

from bs4 import BeautifulSoup

from src.table_extractor import TableExtractor


def test_extracts_single_header_table_and_preserves_blank_cell():
    html = Path("tests/fixtures/single_header_table.html").read_text(encoding="utf-8")
    table = BeautifulSoup(html, "html.parser").find("table")
    extractor = TableExtractor(config=None)

    headers = extractor.extract_headers(table)
    rows = extractor.extract_rows(table, year=2024, headers=headers)

    assert headers == ["Rank", "Player", "Votes"]
    assert rows == [["1st", "Ada Striker", "10"], ["2nd", "Bea Keeper", ""]]


def test_inserts_missing_rank_when_source_row_is_short():
    table = BeautifulSoup(
        "<table><tr><th>Rank</th><th>Player</th></tr><tr><td>Ada</td></tr></table>",
        "html.parser",
    ).find("table")

    rows = TableExtractor(config=None).extract_rows(table, 2024, ["Rank", "Player"])

    assert rows == [["MISSING_RANK", "Ada"]]
