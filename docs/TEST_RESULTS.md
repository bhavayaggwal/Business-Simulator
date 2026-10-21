# Test results

Test plan: `docs/PRD.md` §10. Types: Valid, Extreme, Invalid, Erroneous.
Automated tests: `python -m unittest discover tests -v`.
Every failed test needs a commentary saying how it will be (or was) fixed.

| ID | Description | Type | Test data | Expected | Actual | Result | Commentary / evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | Full month calculation | Valid | Worked example | Profit £250, cash £4,150, stock 850 | As expected | Pass | Automated, 2026-10-18 |
| T02 | Price lowers demand | Valid | £5, £10 | 400, 141 | As expected | Pass | Automated, 2026-10-18 |
| T03 | Marketing diminishing returns | Valid | £0, £500, £1,000 | 400, 551, 607 | As expected | Pass | Automated, 2026-10-18 |
| T04 | Market factor in range | Extreme | 1,000 factors | All 0.90–1.10 | As expected | Pass | Automated, 2026-10-18 |
| T05 | Sales capped by stock | Extreme | Demand 500, stock 300 | Sold 300, stock 0 | As expected | Pass | Automated, 2026-10-18 |
| T06 | Demand equals stock | Extreme | Demand 300, stock 300 | Sold 300, stock 0 | As expected | Pass | Automated, 2026-10-18 |
| T07 | Months carry over | Valid | 2 months | Opening = previous closing | As expected | Pass | Automated, 2026-10-18 |
| T08 | Merge sort, descending, stable | Valid | Profits 250, −40, 600, 250, 10 | Months 3, 1, 4, 5, 2 | As expected | Pass | Automated, 2026-10-18; ascending also tested |
| T09 | Merge sort edge cases | Extreme | Empty; one record | Empty; same record | As expected | Pass | Automated, 2026-10-18 |
| T10 | Binary search | Valid / Extreme / Invalid | Find 4, 1, 6, 7 in months 1–6 | Found ×3; 7 not found | As expected | Pass | Automated, 2026-10-18 |
| T11 | Linear search | Valid / Invalid | "cof", "zzz" | Coffee Shop match; none | As expected | Pass | Automated, 2026-10-18; blank-search message to check manually |
| T12 | Price validation | Extreme / Invalid / Erroneous | 0.01, 0, −5, "abc", 1.234 | Accept; reject ×4 | As expected | Pass | Automated, 2026-10-18 |
| T13 | Units to buy validation | Erroneous | 2.5, −1, "abc" | All rejected | As expected | Pass | Automated, 2026-10-18 |
| T14 | Cash check boundary | Extreme | Buy 350, then 351 | Accept; reject (£1,002) | As expected | Pass | Automated, 2026-10-18 |
| T15 | Industries differ | Valid | Same decisions, Gym vs Bakery | Different demand | | | |
| T16 | Profiles separate | Valid | Profile A (2 businesses), switch to B | B sees none of A's | | | |
| T17 | Data persists | Valid | 3 months, close, reopen | All reload unchanged | | | Needs SQL layer (iteration 3) |
| T18 | Decisions saved per month | Valid | Different price each month | History shows each | | | |
| T19 | Graphs match data | Valid | 6 months | Points match History | | | |
| T20 | Help content | Valid | Open Help | ≥ 8 terms + how-to | | | |
| T21 | Navigation and feedback | Valid | All screens from hub | ≤ 2 clicks; explanation | | | |
| T22 | Info boxes | Valid | Hover ⓘ on results | < 0.5 s, matches Help | | | |
| T23 | End to end | Valid | Create + 6 months | No errors | | | |
