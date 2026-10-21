# Business Startup Simulator: PRD

A Python desktop app that lets students and young entrepreneurs run a virtual
startup month by month and see how their decisions affect revenue, costs, profit
and cash. Built as an A-level Computer Science NEA (The College of Richard
Collyer, centre 65131).

**Core teaching point:** a business can make a profit and still run out of
cash. Every design choice serves that lesson.

---

## 1. Scope

Scope is fixed by the school-marked analysis documents. **Anything not listed
here is out of scope, even if it seems like a good idea.**

**In scope**
- User profiles (username only), each student's businesses kept separate
- Business creation with industry selection
- Monthly decisions: price, marketing spend, stock to buy
- Simulation engine: demand, sales, stock, revenue, costs, profit, cash
- Storage in SQL Server between sessions
- History with merge sort, linear search, binary search
- Graphs (line, pie, bar) and a summary report
- Help screen and hover info boxes on key terms
- Input validation with specific messages

**Extension (only after objectives 1–18 are met):** demand forecasting from past sales.

**Out of scope:** holding costs, insolvency rules, lost-sales tracking, loans,
interest, tax, depreciation, multiple products, multiplayer, web deployment.

---

## 2. Stack

| Area | Decision |
| --- | --- |
| Language | Python 3 |
| GUI | PyQt6 |
| Database | Microsoft SQL Server Express on the student's Windows laptop, managed in SSMS, accessed via `pyodbc` |
| Graphs | matplotlib embedded in PyQt6 (static graphs, one point per month) |
| Info boxes | PyQt6 tooltips, text from the `GlossaryTerm` table |
| Sorting | Merge sort, hand-written |
| Searching | Linear search (business name, industry); binary search (month in a history) |
| Tests | `unittest` (no extra dependency) |

---

## 3. Architecture

Three layers. Each calls only the layer below it.

| Layer | Folder | Rule |
| --- | --- | --- |
| UI | `ui/` | PyQt6 screens. Calls `SimulatorService` only. |
| Logic | `logic/` | Pure Python. **No PyQt6, no SQL.** `services.py` loads state, runs the engine, saves results. |
| Data | `data/` | The only code that touches storage. |

The engine never touches the database; the random market factor is generated in
`services.py` and passed in, so tests can fix it at 1.00.

**Repository interface.** `data/memory_repository.py` (prototype) and the
upcoming `data/sql_repository.py` must have identical methods:

```
get_profiles()                     add_profile(username) -> UserProfile
get_industries()                   get_industry(industry_id)
add_business(business) -> Business get_business(business_id)
get_businesses_for_user(user_id)   update_business(business)
add_result(result)                 get_results(business_id)   # ordered by month_no
get_glossary()
```

---

## 4. Simulation rules

### Demand
```
Demand          = floor(BaseDemand × PriceEffect × MarketingEffect × MarketFactor)
PriceEffect     = (ReferencePrice ÷ Price) ^ Sensitivity
MarketingEffect = 1 + MaxBoost × (1 − e^(−Spend ÷ k))      # diminishing returns
MarketFactor    = random, 0.90 to 1.10 each month
```

### Costs and cash
Stock is **paid for when bought** but only **counts as a cost when sold**.

| Cost | Calculation | Hits profit | Hits cash |
| --- | --- | --- | --- |
| Stock purchases | units bought × unit cost | No | Yes, when bought |
| Cost of goods sold (COGS) | units sold × unit cost | Yes | No (already paid) |
| Marketing | set by user | Yes | Yes |
| Fixed costs | set per industry | Yes | Yes |

```
TotalCosts  = COGS + Marketing + FixedCosts
Profit      = Revenue − TotalCosts
ClosingCash = OpeningCash + Revenue − StockPurchases − Marketing − FixedCosts
```

### Order each month
1. Validate: stock purchases + marketing ≤ opening cash.
2. Add purchased stock.
3. Calculate demand.
4. Units sold = min(demand, opening stock + units bought).
5. Closing stock = opening stock + units bought − units sold.
6. Revenue = price × units sold.
7. COGS, marketing, fixed costs → total costs → profit.
8. Closing cash.
9. Save the month; closing cash and stock become next month's opening values.

**Setup:** month 1 opening cash = starting capital − (initial stock × unit cost).

### Worked example (used in test T01)
Unit cost £2, fixed £800, opening cash £5,000, opening stock 300. Price £5,
marketing £300, buy 1,000. Demand 450.
→ Sold 450, closing stock 850, revenue £2,250, COGS £900, total costs £2,000,
**profit £250**, **closing cash £4,150 (−£850)**.

---

## 5. Data model (SQL Server)

Money is `DECIMAL`, unit counts are `INT`.

**UserProfile**: user_id INT IDENTITY PK · username NVARCHAR(30) NOT NULL UNIQUE · created_at DATETIME2

**Industry**: industry_id INT IDENTITY PK · name NVARCHAR(50) UNIQUE · base_demand INT · reference_price DECIMAL(10,2) · unit_cost DECIMAL(10,2) · fixed_cost DECIMAL(10,2) · price_sensitivity DECIMAL(4,2) · max_marketing_boost DECIMAL(4,2) · marketing_k DECIMAL(10,2)

**Business**: business_id INT IDENTITY PK · user_id FK · industry_id FK · name NVARCHAR(60) (unique per user) · starting_capital DECIMAL(12,2) · base_demand, reference_price, unit_cost, fixed_cost, price_sensitivity (copied from industry, user may edit) · price DECIMAL(10,2) · marketing_budget DECIMAL(10,2) · current_month INT · cash DECIMAL(12,2) · stock INT · created_at DATETIME2

**MonthlyResult**: result_id INT IDENTITY PK · business_id FK · month_no INT (unique per business) · price, marketing_spend, stock_purchase_cost DECIMAL(10,2) · units_purchased INT · market_factor DECIMAL(4,3) · demand, units_sold, opening_stock, closing_stock INT · revenue, cogs, fixed_cost, total_costs, profit, opening_cash, closing_cash DECIMAL(12,2)

**GlossaryTerm**: term_id INT IDENTITY PK · term NVARCHAR(50) UNIQUE · definition NVARCHAR(200) · example NVARCHAR(200)

**SchemaVersion**: script_name NVARCHAR(100) PK · applied_at DATETIME2 (used only by `setup_db.py`)

Copying the industry values into `Business` is deliberate: once a user edits
them they describe that business, not the industry. All other tables are 3NF.

**Saving a month** = insert `MonthlyResult` + update `Business` in **one transaction**.

---

## 6. Database setup on the student's laptop

The repo holds the database **structure** as numbered scripts, never the database itself.

```
database/001_create_tables.sql
database/002_seed_industries.sql      # from data/seed_data.py
database/003_seed_glossary.sql        # from data/seed_data.py
setup_db.py                           # creates DB if missing, runs scripts not yet in SchemaVersion
config.example.ini                    # committed; copied to config.ini (git-ignored)
```

```ini
[database]
server = localhost\SQLEXPRESS
database = BusinessSimulator
driver = ODBC Driver 18 for SQL Server
trusted_connection = yes
trust_server_certificate = yes
```

Schema changes = a **new** numbered script. Never edit a script that has already run.

---

## 7. Screens

| Screen | Purpose | Objectives |
| --- | --- | --- |
| Profile select | Choose or create a username | 3 |
| Dashboard | List businesses; linear search by name/industry | 3, 11 |
| Create business | Name, industry (pre-fills editable defaults), capital, price, stock, marketing | 1, 2, 16 |
| Business hub | Cash, stock, last month's profit and revenue; links to all business screens | 1, 17 |
| Decisions | Price, marketing, units to buy; live "cash left after purchases" | 4, 16 |
| Month results | Sales and stock, profit and loss beside cash statement, plain-English explanations | 5, 6, 8, 9, 17 |
| History | Table of months; merge sort by any figure; binary search "go to month" | 12, 13 |
| Graphs | Revenue/profit/cash over time; cost breakdown pie; revenue vs costs bars; compare two businesses | 3, 14 |
| Help | Glossary + how to use each screen | 15 |

Navigation bar on every screen: Your businesses, Business hub, Help, Switch profile.
Every figure label on business screens has an ⓘ tooltip (objective 18).

---

## 8. Validation

| Field | Rule | Message |
| --- | --- | --- |
| Username | 3–30 letters, numbers, `_`; unique | "Username must be 3–30 letters, numbers or underscores." / "That username is already taken." |
| Business name | 1–60 chars; unique per profile | "You already have a business with that name." |
| Starting capital | > 0 and < £10,000,000 | "Starting capital must be more than £0." |
| Price | > 0, ≤ 2 decimal places | "Price must be more than £0." |
| Initial stock | whole ≥ 0; cost ≤ capital | "You can't afford that much stock with your starting capital." |
| Marketing | ≥ 0; ≤ cash left | "Marketing budget is more than the cash you have left." |
| Units to buy | whole ≥ 0 | "Units to buy must be a whole number of 0 or more." |
| Monthly plan | units × unit cost + marketing ≤ cash | "You don't have enough cash: this plan costs £X but you have £Y." |
| Search | not blank | "Enter a name or industry to search for." |
| Go to month | whole, 1 to current month | "Month not simulated yet." |

---

## 9. Objectives and success criteria

| # | Objective | Success criterion | Test |
| --- | --- | --- | --- |
| 1 | Create and manage a business risk-free | Create a business, run 6 months, no errors | T23 |
| 2 | Industries with their own values | ≥ 3 industries; same decisions → different demand | T15 |
| 3 | Multiple simulations, compare | 2+ businesses per profile; compare on graphs | T16 |
| 4 | Monthly decisions | Price, marketing, stock changeable and saved per month | T18 |
| 5 | Engine calculations | Match hand-calculated values | T01 |
| 6 | Price and marketing affect demand | Price up → demand down; marketing has diminishing returns | T02, T03 |
| 7 | Controlled variation | Market factor always 0.90–1.10 | T04 |
| 8 | Months carry over | Opening = previous closing | T07 |
| 9 | Sales ≤ stock | Units sold capped at available stock | T05, T06 |
| 10 | Data persists | Close and reopen, all data reloads | T17 |
| 11 | Search name/industry | Linear search returns all matches or "no results" | T11 |
| 12 | Find a month | Binary search finds month; missing → message | T10 |
| 13 | Sort history | Merge sort by profit, revenue, costs, cash; both orders; stable | T08, T09 |
| 14 | Graphs | Line, pie, bar match stored data | T19 |
| 15 | Help | ≥ 8 terms + how-to for each screen | T20 |
| 16 | Validation | Invalid inputs rejected with specific messages | T12–T14 |
| 17 | Clear UI and feedback | Every screen ≤ 2 clicks; results explain the cause | T21 |
| 18 | Info boxes | Tooltip within 0.5 s; text matches Help | T22 |

---

## 10. Test plan

Test types use the school's terms: **Valid, Extreme, Invalid, Erroneous**.
T01–T14 are automated (`tests/test_logic.py`, market factor fixed at 1.00);
T15–T23 are manual with screenshot evidence.

Shared values: unit cost £2, fixed £800, cash £5,000, stock 300, base demand 400,
reference price £5, sensitivity 1.5, max boost 0.6, k £500.

| ID | What | Type | Data | Expected |
| --- | --- | --- | --- | --- |
| T01 | Full month | Valid | Worked example (§4) | Profit £250, cash £4,150, stock 850 |
| T02 | Price lowers demand | Valid | £5, £10, no marketing | 400, 141 |
| T03 | Diminishing marketing | Valid | £0, £500, £1,000 | 400, 551, 607 |
| T04 | Market factor range | Extreme | 1,000 factors | All 0.90–1.10 |
| T05 | Sales capped | Extreme | Demand 500, stock 300 | Sold 300, stock 0 |
| T06 | Demand = stock | Extreme | Demand 300, stock 300 | Sold 300, stock 0 |
| T07 | Carry over | Valid | 2 months | Month 2 opening = month 1 closing |
| T08 | Merge sort desc, stable | Valid | Profits m1 250, m2 −40, m3 600, m4 250, m5 10 | 3, 1, 4, 5, 2 |
| T09 | Merge sort edges | Extreme | Empty; one record | Empty; same record |
| T10 | Binary search | Valid / Extreme / Invalid | Months 1–6; find 4, 1, 6, 7 | Found, found, found, "Month not simulated yet." |
| T11 | Linear search | Valid / Invalid | "cof" (industry), "zzz", blank | Coffee Shop matches; none; message |
| T12 | Price | Extreme / Invalid / Erroneous | 0.01, 0, −5, "abc", 1.234 | Accept; reject ×4 |
| T13 | Units to buy | Erroneous | 2.5, −1, "abc" | All rejected |
| T14 | Cash check | Extreme | Cash £1,000, cost £2, marketing £300; buy 350, 351 | Accept; reject (£1,002) |
| T15 | Industries differ | Valid | Same decisions, Gym vs Bakery | Different demand |
| T16 | Profiles separate | Valid | Profile A with 2 businesses; switch to B | B sees none of A's |
| T17 | Persistence | Valid | 3 months, close, reopen | All reload unchanged |
| T18 | Decisions saved | Valid | Different price each month | History shows each |
| T19 | Graphs match | Valid | 6 months | Points match History table |
| T20 | Help | Valid | Open Help | ≥ 8 terms + how-to |
| T21 | Navigation | Valid | All screens from hub | ≤ 2 clicks; explanation shown |
| T22 | Info boxes | Valid | Hover each ⓘ on results | Shows < 0.5 s, matches Help |
| T23 | End to end | Valid | Create + 6 months | No errors, consistent figures |

---

## 11. Current state

**Done (iteration 1, UI prototype):**
- All 9 screens in PyQt6, ledger visual style (`ui/style.py`)
- Engine, merge sort, linear and binary search, validation: complete
- In-memory repository with demo data (`demo_student`, "Bean There", 6 months)
- T01–T14 automated and passing
- Not yet run on a real display (PyQt6 was unavailable when it was built)

**Open decisions**
- [ ] Gym: what is its "unit" and its "stock"? (the model assumes physical products)
- [ ] Industry default values in `data/seed_data.py` are placeholders; confirm with the business teacher
- [ ] Confirm the laptop can install SQL Server Express, SSMS, ODBC Driver 18

---

## 12. Build plan (remaining)

| # | Iteration | Done when |
| --- | --- | --- |
| 2 | Run prototype on Windows; fix any Qt issues; capture a screenshot of every screen | App runs; screenshots in `docs/evidence/prototype/` |
| 3 | SQL Server layer: scripts 001–003, `setup_db.py`, `config.example.ini`, `data/connection.py`, `data/sql_repository.py`; `main.py` uses SQL (keep `--demo` flag for the in-memory version); catch DB errors (NFR4) | T17 passes; app survives a stopped SQL Server with a clear message |
| 4 | Post-prototype feedback from teacher/classmate (human step) → design updates | Feedback and changes recorded in `docs/REFINEMENT.md` |
| 5 | Manual tests T15–T23 with evidence | `docs/TEST_RESULTS.md` complete |
| 6 | Extension: demand forecasting (moving average of units sold) | Only if 1–5 are done |
| 7 | Evaluation against objectives 1–18 | Each marked met / partly / not met with evidence |
