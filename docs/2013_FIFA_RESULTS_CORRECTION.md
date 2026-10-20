# 2013 FIFA Ballon d'Or correction

## Decision

The apparent Gareth Bale/Andrea Pirlo rank inversion came from an incorrect Pirlo point value, not from unusual ranking semantics. Four rows contained five transcription errors:

| Player | Field | Before | Corrected |
| --- | --- | ---: | ---: |
| Andrea Pirlo | points | 70 | 55 |
| Robert Lewandowski | points | 43 | 45 |
| Xavi | rank | 14 | 15 |
| Xavi | percent | 0.82 | 0.81 |
| Edinson Cavani | points | 12 | 18 |

Gareth Bale's rank 9, 65 points, and 1.32% are confirmed and unchanged. The corrected raw point total is 4,869.

## Evidence

- FIFA's archived official [2013 voting-results PDF](https://web.archive.org/web/20140116094413/http://www.fifa.com/mm/document/ballond%27or/general/02/26/14/03/votes_percentage_al_awards_neutral.pdf) establishes the final ranks and official percentages, including Bale at rank 9 and 1.32%, Pirlo at rank 10 and 1.11%, and Xavi at rank 15 and 0.81%.
- A [contemporaneous detailed results table](https://www.maxifoot.fr/football/article-20734.htm), published the day after the ceremony and linking to FIFA's ballot detail, records each player's media, coach, and captain points. It gives Pirlo `3 + 22 + 30 = 55`, Lewandowski `8 + 24 + 13 = 45`, and Cavani `2 + 9 + 7 = 18`; all player totals sum to 4,869.
- FIFA's archived [juror-level ballot PDF](https://web.archive.org/web/20140116094148/http://www.fifa.com/mm/document/ballond%27or/general/02/26/14/03/fboaward_menplayer2013_neutral.pdf) is the underlying 5/3/1 ballot record.

## Percentage semantics

For the FIFA Ballon d'Or era, `percent` is not `player points / all player points`. FIFA calculated a percentage within each of the three voter groups—national-team captains, national-team coaches, and media—then weighted those three percentage shares equally.

For example, the 2013 group totals were 1,557 media points, 1,656 coach points, and 1,656 captain points. Cristiano Ronaldo's official result is therefore:

```text
((399 / 1,557) + (456 / 1,656) + (510 / 1,656)) / 3 × 100 = 27.99%
```

The audit now exempts 2010–2015 from the generic raw-points percentage calculation and records the alternative semantics explicitly. Official percentages are preserved rather than recomputed.
