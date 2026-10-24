# Business Startup Simulator

A desktop simulator that helps students and young entrepreneurs learn how price,
marketing and stock decisions affect revenue, costs, profit and cash. The core
lesson is that **a business can make a profit and still run out of cash**.

Python · PyQt6 · SQL Server · matplotlib. Light and dark themes in a soft
(neumorphic) style.

## Setting up on a Windows laptop

1. **Python 3.11 or newer** from python.org (tick *Add python.exe to PATH*).
2. **SQL Server 2022 Express** (the free edition) and **SSMS** from Microsoft.
   Express installs as `localhost\SQLEXPRESS`.
3. **ODBC Driver 18 for SQL Server** from Microsoft. SSMS usually installs it already.
4. In this folder, open a terminal and run:

   ```
   pip install -r requirements.txt
   python setup_db.py
   python main.py
   ```

   The first `setup_db.py` creates `config.ini` from `config.example.ini`, creates the
   `BusinessSimulator` database, and runs the scripts in `database/`. If SQL Server
   is a full install rather than Express, change `server` in `config.ini` to
   `localhost` and run `python setup_db.py` again.

To try the app without SQL Server: `python main.py --demo` (demo data, nothing saved).

## Commands

```
python main.py                         run the app (SQL Server)
python main.py --demo                  run with in-memory demo data
python setup_db.py                     create or upgrade the database (safe to repeat)
python -m unittest discover tests -v   run every automated test
```

## How it is built

```
main.py                 starts the app; chooses SQL Server or demo data
setup_db.py             creates the database and runs numbered scripts once each
config.example.ini      database settings (copied to config.ini, never committed)
logic/                  pure Python: no Qt, no SQL
  models.py             data classes
  engine.py             the month's calculations (demand, sales, profit, cash)
  algorithms.py         merge sort, linear search, binary search (hand-written)
  validation.py         input rules and the messages users see
  services.py           the screens' only doorway: load, simulate, save
  errors.py             StorageError: a database problem in plain English
data/                   the only code that touches storage
  memory_repository.py  in-memory store (demo mode and tests)
  sql_repository.py     SQL Server store with identical methods
  connection.py         reads config.ini and opens connections
  seed_data.py          industry defaults and glossary text
database/               numbered SQL scripts: 001 tables, 002 industries, 003 glossary
ui/                     PyQt6 screens, one file per screen
  theme.py              light and dark colour tokens, the style sheet, contrast checks
  soft.py               soft cards, shadows and the dark-mode switch
tests/                  unit tests
docs/                   PRD, development log, test results, evidence
CLAUDE.md               working rules for Claude Code
```

Three layers, each calling only the one below: **ui → logic → data**. `main.py`
decides which repository to use and hands it to `SimulatorService`, so the
screens never know whether data is in memory or in SQL Server.

### Decisions worth knowing

- **Saving a month** inserts the result and updates the business in one SQL
  transaction (`save_month`), so a stored month always matches the business.
  Both repositories have `save_month`, keeping their methods identical.
- **Upper limits on inputs** (price up to £9,999.99, up to 1,000,000 units,
  price sensitivity up to 5) keep every value inside its SQL column type, so
  extreme test data gets a message instead of a database error.
- **Database errors** become `StorageError` with a message the user can act on.
  If SQL Server isn't running at start-up, the app offers *Try again*, *Use demo
  mode* or *Quit*.
- **Themes** are colour tokens named by role. Every text colour meets WCAG AA
  (4.5:1) in both themes (`contrast_ratio` in `ui/theme.py`). The choice is saved
  per Windows user with `QSettings`, not in the database.

## Troubleshooting

| Message | Fix |
|---|---|
| Can't reach SQL Server (…) | Start the *SQL Server (SQLEXPRESS)* service, or check `server` in `config.ini` |
| The database … doesn't exist yet | Run `python setup_db.py` |
| Data source name not found / driver not found | Install *ODBC Driver 18 for SQL Server*, or change `driver` in `config.ini` to a driver listed by `python -c "import pyodbc; print(pyodbc.drivers())"` |
| `ModuleNotFoundError: PyQt6` | Run `pip install -r requirements.txt` |
