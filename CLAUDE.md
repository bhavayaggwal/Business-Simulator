# CLAUDE.md

Business Startup Simulator: an A-level CS NEA built in Python + PyQt6 + SQL Server.
**Read `docs/PRD.md` before any task.** It is the single source of truth for
scope, formulas, data model, screens, validation, objectives and tests.

## Commands

```
python main.py                         # run the app
python -m unittest discover tests -v   # run automated tests (must stay green)
python setup_db.py                     # create/upgrade the SQL Server database (from iteration 3)
```

## Hard rules

1. **Scope is frozen.** Build only what `docs/PRD.md` §1 lists. If something seems
   missing or useful, ask; don't add it. Holding costs, insolvency and lost-sales
   tracking are deliberately excluded.
2. **Layers.** `logic/` never imports PyQt6 or pyodbc. `ui/` only calls
   `SimulatorService`. Only `data/` touches storage.
3. **Algorithms are hand-written.** Never use `sorted()`, `.sort()`, `bisect` or
   `list.index()` for the sort/search features; use `logic/algorithms.py`.
4. **Money is `Decimal`,** rounded with `engine.money()`. Units are `int`.
5. **Repository parity.** `memory_repository.py` and `sql_repository.py` keep
   identical method names and return types (PRD §3).
6. **Schema changes** go in a new numbered script in `database/`; never edit one
   that has already run.
7. **PyQt6 signal handlers** that are connected to `textChanged` or
   `currentIndexChanged` must accept `*_signal_args`.
8. **Code is read by a student and a moderator.** Short docstrings, plain names,
   comments that explain *why*. No clever one-liners.
9. Keep the existing visual style (`ui/style.py`): ledger palette, Georgia
   headings, statements with bracketed deductions and double-underlined totals.

## Auto-documentation (do this as part of every task, not at the end)

The NEA is marked on evidence. Keep these files current as you work:

| File | Update when | NEA section it feeds |
| --- | --- | --- |
| `docs/DEV_LOG.md` | Any error, bug, failing test or design change: add an entry **while fixing it** | Developmental Testing (AO3.1c) |
| `docs/TEST_RESULTS.md` | After running tests: fill Actual outcome, Pass/Fail, comment | Testing (AO3.1c) |
| `docs/PRD.md` §11 | When an iteration finishes or a decision is made | Prototype / Evaluation |
| `docs/REFINEMENT.md` | When third-party feedback arrives (iteration 4) | Post-Prototype Refinement (AO3.1a) |
| `docs/evidence/` | Note in the log which screenshot the human should take, and its file name | All sections |

DEV_LOG entry format (newest at the bottom):

```
### DL-<n>: <short title>   (<YYYY-MM-DD>, iteration <n>)
- **Problem:** what went wrong, with the exact error message
- **Cause:** why it happened
- **Fix:** what changed (files, functions)
- **Evidence:** screenshot names to capture: docs/evidence/DL-<n>-before.png, -after.png
- **Test:** which test now covers it
```

You can't take screenshots yourself: when evidence is needed, tell the human
exactly what to capture and the file name to save it as.

## Workflow per task

1. State which PRD objective(s) or iteration the task serves.
2. Make the change; run the tests.
3. Update the docs above.
4. Commit with a message like `iter3: add sql_repository (obj 10)`. The Git
   history is development evidence, so commit small and often.
