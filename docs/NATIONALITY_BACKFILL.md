# National-team backfill for 2016–2019 and 2021

## Definition

The scraper maps source columns labelled `National team` to the historical CSV column named `nationality`. For this dataset, the field therefore means the senior national team represented in the relevant award edition. It does not attempt to encode birthplace, multiple citizenships, or eligibility for other teams.

## Correction

All 150 rows in 2016, 2017, 2018, 2019, and 2021 had blank nationality values. They have been backfilled with the national-team country published alongside each edition's results. Country names use the English vocabulary already present in the dataset, such as `Brazil`, `South Korea`, and `Bosnia and Herzegovina`.

No ranks, scores, percentages, clubs, player names, positions, or other editions were changed.

## Sources and cross-checks

France Football's complete result lists published by L'Équipe provide the player-country pairs:

- [2016 complete ranking](https://www.lequipe.fr/Football/Actualites/Le-classement-complet-du-ballon-d-or-france-football-2016-eg/759441)
- [2017 complete ranking](https://www.lequipe.fr/Football/Diaporama/Le-classement-du-ballon-d-or-2017/6472)
- [2018 complete ranking](https://www.lequipe.fr/Football/Actualites/Le-classement-du-ballon-d-or-france-football-2018-eg/964818)
- [2019 complete ranking](https://www.lequipe.fr/Football/Actualites/Le-classement-complet-du-ballon-d-or-france-football-2019-eg/1086014)
- [2021 complete ranking](https://www.lequipe.fr/France-Football/Actualites/Le-classement-du-ballon-d-or-2021/1302150)

As an independent internal check, 92 of the 150 rows could be matched unambiguously to the same player's populated national-team value in another edition. The source lists resolved the other 58 rows and the ambiguous `Luis Suárez` name, which is shared with a historical Spanish player elsewhere in the dataset.
