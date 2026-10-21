# Development log

Errors met during development and how they were solved. Feeds the
Developmental Testing section (AO3.1c). Newest entry at the bottom.

### DL-1: Screen handlers crashed when a text box changed   (2026-10-18, iteration 1)
- **Problem:** Opening "Start a new business" crashed with
  `TypeError: CreateBusinessScreen.update_summary() takes 1 positional argument but 2 were given`.
- **Cause:** Qt signals pass data to the function they call: `textChanged` sends the
  new text and `currentIndexChanged` sends the new index. Four handlers
  (`update_summary`, `fill_industry_defaults`, `update_plan`, `draw`) were written
  to take no arguments.
- **Fix:** Each handler now accepts `*_signal_args` and ignores them
  (`ui/create_business_screen.py`, `ui/decisions_screen.py`, `ui/graphs_screen.py`).
  Added as rule 7 in `CLAUDE.md` so new screens don't repeat it.
- **Evidence:** the traceback above (found by a scripted run of every screen before
  the first real launch). After screenshot to capture: `docs/evidence/DL-1-after.png`
  showing the create-business screen updating "Initial stock will cost…" as you type.
- **Test:** covered by manual test T23 (end to end).
