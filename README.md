# Business Startup Simulator

A desktop simulator that helps students and young entrepreneurs learn how price,
marketing and stock decisions affect revenue, costs, profit and cash.

## Current state: UI prototype

All nine screens work against an **in-memory** data store, so the app runs
without SQL Server. A demo profile (`demo_student`) with a coffee shop and six
months of history is created on start-up. Anything created in the app is lost
when it closes. The SQL Server repository replaces the in-memory one in the next
iteration, without changes to the screens.

## Run it

```
pip install -r requirements.txt
python main.py
```

Run the automated tests (T01–T14 from the test plan):

```
python -m unittest discover tests -v
```

## Structure

```
main.py                 starts the app
logic/                  no UI or SQL code
  models.py             data classes
  engine.py             simulation calculations
  services.py           load -> simulate -> save, plus demo data
  algorithms.py         merge sort, linear search, binary search
  validation.py         input rules and error messages
data/
  memory_repository.py  prototype data store (same methods the SQL one will have)
  seed_data.py          industry defaults (placeholders) and glossary text
ui/                     PyQt6 screens, one file per screen
tests/                  unit tests
docs/                   PRD, development log, test results, evidence
CLAUDE.md               working rules for Claude Code
```
