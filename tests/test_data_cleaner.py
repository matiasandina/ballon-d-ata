import pandas as pd

from src.data_cleaner import DataCleaner


def cleaner():
    return DataCleaner(patterns={"reference_notes": r"~~~\[~~~\d+~~~\]"}, column_mappings={"votes": "points"})


def test_rank_parsing_handles_ordinals_and_ties():
    frame = pd.DataFrame({"rank": ["1st", "2nd", "2nd"], "points": [10, 5, 5]})

    result = cleaner().clean_dataframe(frame, 2024)

    assert result["rank"].tolist() == [1.0, 2.0, 2.0]


def test_missing_points_are_not_forward_filled_from_another_player():
    frame = pd.DataFrame({"points": ["10", "", "0"]})

    result = cleaner()._clean_numeric_columns(frame)

    assert result.loc[0, "points"] == 10
    assert pd.isna(result.loc[1, "points"])
    assert result.loc[2, "points"] == 0


def test_multi_year_cleaning_preserves_missing_points_and_votes():
    frame = pd.DataFrame(
        {
            "rank": [1, 2], "player": ["Ada", "Bea"], "nationality": ["A", "B"],
            "club": ["One", "Two"], "points": ["3", None], "total": [10, None],
            "1st": [None, None], "2nd": [None, None], "3rd": [None, None],
            "4th": [None, None], "5th": [None, None], "year": [2004, 2004],
        }
    )

    result = cleaner().clean_multi_year_data(frame)

    assert result["points"].tolist() == [10, pd.NA]
    assert result["votes"].tolist() == [3, pd.NA]


def test_percentage_calculation_uses_complete_total():
    frame = pd.DataFrame({"year": [2024, 2024], "points": [3, 1]})

    result = cleaner().calculate_percentage(frame)

    assert result["percent"].tolist() == [75.0, 25.0]


def test_percentage_calculation_does_not_use_incomplete_total():
    frame = pd.DataFrame({"year": [2018, 2018], "points": [pd.NA, 10]})

    result = cleaner().calculate_percentage(frame)

    assert result["percent"].isna().all()
