# Ballon d'Or data-quality audit

Status: **pass_with_warnings** (0 failures, 2 warnings/findings).

## Main

- File: `data/ballon_dor_all_years.csv`
- Rows: 2,095
- Coverage: 1956–2025 (69 years)
- Schema: `year, rank, player, club, nationality, points, percent, position`
- Duplicate player-year combinations: 0
- Invalid values: 0
- Unusual rank sequences: 0

### Per-year row counts

| Year | Rows |
| ---: | ---: |
| 1956 | 24 |
| 1957 | 23 |
| 1958 | 26 |
| 1959 | 26 |
| 1960 | 26 |
| 1961 | 43 |
| 1962 | 27 |
| 1963 | 25 |
| 1964 | 26 |
| 1965 | 27 |
| 1966 | 23 |
| 1967 | 34 |
| 1968 | 32 |
| 1969 | 31 |
| 1970 | 29 |
| 1971 | 23 |
| 1972 | 27 |
| 1973 | 27 |
| 1974 | 23 |
| 1975 | 32 |
| 1976 | 29 |
| 1977 | 32 |
| 1978 | 30 |
| 1979 | 32 |
| 1980 | 32 |
| 1981 | 34 |
| 1982 | 19 |
| 1983 | 36 |
| 1984 | 26 |
| 1985 | 38 |
| 1986 | 27 |
| 1987 | 34 |
| 1988 | 24 |
| 1989 | 30 |
| 1990 | 23 |
| 1991 | 31 |
| 1992 | 22 |
| 1993 | 30 |
| 1994 | 28 |
| 1995 | 34 |
| 1996 | 32 |
| 1997 | 36 |
| 1998 | 31 |
| 1999 | 31 |
| 2000 | 30 |
| 2001 | 50 |
| 2002 | 26 |
| 2003 | 49 |
| 2004 | 49 |
| 2005 | 49 |
| 2006 | 49 |
| 2007 | 50 |
| 2008 | 30 |
| 2009 | 30 |
| 2010 | 23 |
| 2011 | 23 |
| 2012 | 23 |
| 2013 | 23 |
| 2014 | 23 |
| 2015 | 23 |
| 2016 | 30 |
| 2017 | 30 |
| 2018 | 30 |
| 2019 | 30 |
| 2021 | 30 |
| 2022 | 30 |
| 2023 | 30 |
| 2024 | 30 |
| 2025 | 30 |

### Missing fields

| Field | Missing |
| --- | ---: |
| year | 0 |
| rank | 0 |
| player | 0 |
| club | 0 |
| nationality | 150 |
| points | 115 |
| percent | 0 |
| position | 1975 |

## Voting Detail

- File: `data/ballon_dor_voting_details.csv`
- Rows: 196
- Coverage: 2003–2006 (4 years)
- Schema: `rank, player, nationality, club, points, 1st, 2nd, 3rd, 4th, 5th, votes, year, percent`
- Duplicate player-year combinations: 0
- Invalid values: 0
- Unusual rank sequences: 0

### Per-year row counts

| Year | Rows |
| ---: | ---: |
| 2003 | 49 |
| 2004 | 49 |
| 2005 | 49 |
| 2006 | 49 |

### Missing fields

| Field | Missing |
| --- | ---: |
| rank | 0 |
| player | 0 |
| nationality | 0 |
| club | 0 |
| points | 0 |
| 1st | 168 |
| 2nd | 149 |
| 3rd | 134 |
| 4th | 127 |
| 5th | 118 |
| votes | 0 |
| year | 0 |
| percent | 0 |

## Findings

- **warning — `missing_nationality`:** Nationality is unavailable for some year groups.
  - Details: `{"per_year": {"2016": 30, "2017": 30, "2018": 30, "2019": 30, "2021": 30}}`
- **warning — `missing_voting_scores`:** Points and/or percentages are unavailable for some records; blanks are preserved as unavailable, not zero.
  - Details: `{"per_year": {"2010": {"percent": 0, "points": 23}, "2011": {"percent": 0, "points": 23}, "2012": {"percent": 0, "points": 23}, "2014": {"percent": 0, "points": 23}, "2015": {"percent": 0, "points": 23}}}`

## Known pipeline defects

- **confirmed_defect — `points_forward_fill`:** DataCleaner._clean_numeric_columns() forward-fills a missing point value from the preceding player and can assign an incorrect score.
- **confirmed_defect — `missing_scores_to_zero`:** DataCleaner.clean_multi_year_data() converts missing points and votes to zero, erasing the distinction between unavailable and zero.

## Percentage semantics

- **default:** points divided by the complete annual point total
- **2010-2015:** official FIFA percentage: the captain, coach, and media group percentage shares are weighted equally; it is not raw points divided by the annual point total

Machine-readable details are in `reports/data_quality.json`. Historical values were not repaired by this audit.
