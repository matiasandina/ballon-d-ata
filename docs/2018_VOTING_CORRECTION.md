# 2018 voting correction

## Decision

The committed baseline omitted Luka Modrić's winning score while retaining the other 29 scores. Its percentages had consequently been calculated from the incomplete 2,127-point subtotal. This correction adds Modrić's published 753 points and recalculates all 30 percentages using the complete 2,880-point total.

No ranks, player names, clubs, nationality values, positions, or other editions were changed.

## Evidence

- [L'Équipe's contemporaneous complete ranking](https://www.lequipe.fr/Football/Actualites/Le-classement-du-ballon-d-or-france-football-2018-eg/964818), published on 3 December 2018, confirms Modrić first, followed by Cristiano Ronaldo and Antoine Griezmann, and confirms the full rank order.
- [Le Parisien's contemporaneous voting analysis](https://www.leparisien.fr/sports/football/ballon-d-or-la-victoire-de-modric-passee-au-scanner-04-12-2018-7960827.php), published on 4 December 2018, reports Modrić's 753 points and describes the 180-juror ballot: each journalist awarded 6, 4, 3, 2, and 1 points to a top five.
- [The contemporaneous complete score list reported by Maxifoot](https://www.maxifoot.fr/ballon-d-or/le-classement-complet-foot-295780.htm) matches every score already present in the dataset and supplies Modrić's 753. The 30 scores sum to 2,880, also equal to 180 ballots × 16 points per ballot.

The percentage formula is:

```text
player points / 2,880 × 100
```

Values are rounded to four decimal places, consistent with the dataset's generated percentage precision. For example, Modrić is `753 / 2,880 × 100 = 26.1458%` and Ronaldo is `476 / 2,880 × 100 = 16.5278%`.

## Why all percentages changed

The prior percentages used 2,127—the sum of only the 29 non-missing scores—as their denominator. They therefore summed to approximately 100% despite excluding the winner. Inserting only Modrić's points would have left internally inconsistent percentages, so the correction treats the 2018 percentage column as one derived unit.
