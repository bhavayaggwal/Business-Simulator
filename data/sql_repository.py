"""SQL Server repository.

It has the same methods, with the same return types, as MemoryRepository
(PRD §3), so SimulatorService works with either one unchanged.

Every query uses ? parameters: the values travel separately from the SQL text,
so nothing a user types can ever be run as SQL (no SQL injection).
"""
import copy
from contextlib import contextmanager
from dataclasses import fields
from decimal import Decimal

import pyodbc

from data.connection import connect
from logic.errors import StorageError
from logic.models import Business, GlossaryTerm, Industry, MonthResult, UserProfile

# SQLSTATE codes (the first item of a pyodbc error) that mean the server
# couldn't be reached or the connection was lost.
CONNECTION_STATES = {"08001", "08S01", "08004", "HYT00", "HYT01"}

# Column names in the same order as each dataclass's fields, so a row from the
# database can be turned straight into an object: Business(*row).
INDUSTRY_FIELDS = [f.name for f in fields(Industry)]
BUSINESS_FIELDS = [f.name for f in fields(Business)]
RESULT_FIELDS = [f.name for f in fields(MonthResult)]


def _columns(names):
    return ", ".join(names)


def _placeholders(count):
    return ", ".join(["?"] * count)


def describe(error, settings):
    """Turn a pyodbc error into a message a student can act on."""
    state = error.args[0] if error.args else ""
    detail = str(error)
    if state in CONNECTION_STATES:
        return (f"Can't reach SQL Server ({settings['server']}). Check that it is running, "
                "then try again.")
    # A missing database is reported as a failed sign-in (28000) too, so this
    # more specific check has to come first.
    if "Cannot open database" in detail:
        return (f"The database {settings['database']} doesn't exist yet. "
                "Run 'python setup_db.py' first.")
    if state == "28000":
        return "SQL Server refused the sign-in. Check the settings in config.ini."
    if state == "42S02":
        return "The database tables are missing. Run 'python setup_db.py' first."
    if state == "23000":
        return ("That couldn't be saved because it breaks a database rule "
                "(for example, a name that is already used).")
    return f"The database couldn't load or save your data (error {state})."


class SqlRepository:
    def __init__(self, settings):
        self.settings = settings
        self._connection = None

    @contextmanager
    def _transaction(self):
        """A cursor for one unit of work.

        Everything done with it is committed together when the with-block ends,
        or all undone if anything inside the block fails. Database errors come
        out as StorageError with a readable message.
        """
        try:
            if self._connection is None:
                self._connection = connect(self.settings)
            cursor = self._connection.cursor()
        except pyodbc.Error as error:
            self._connection = None
            raise StorageError(describe(error, self.settings)) from error
        try:
            yield cursor
            self._connection.commit()
        except pyodbc.Error as error:
            self._undo()
            raise StorageError(describe(error, self.settings)) from error
        except Exception:
            self._undo()
            raise
        finally:
            try:
                cursor.close()
            except pyodbc.Error:
                pass                # the connection has already gone

    def _undo(self):
        """Roll back. If the connection itself has died, forget it, so the next
        call opens a fresh one (for example once SQL Server is restarted)."""
        try:
            self._connection.rollback()
        except pyodbc.Error:
            self.close()

    def close(self):
        if self._connection is not None:
            try:
                self._connection.close()
            except pyodbc.Error:
                pass
            self._connection = None

    def check_connection(self):
        """Raise StorageError now if the database can't be used, rather than
        part-way through the first screen."""
        with self._transaction() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Industry").fetchone()

    # ---- profiles -------------------------------------------------------
    def get_profiles(self):
        with self._transaction() as cursor:
            rows = cursor.execute(
                "SELECT user_id, username FROM UserProfile ORDER BY user_id").fetchall()
        return [UserProfile(*row) for row in rows]

    def add_profile(self, username):
        with self._transaction() as cursor:
            new_id = cursor.execute(
                "INSERT INTO UserProfile (username) OUTPUT INSERTED.user_id VALUES (?)",
                username).fetchone()[0]
        return UserProfile(new_id, username)

    # ---- industries -----------------------------------------------------
    def get_industries(self):
        with self._transaction() as cursor:
            rows = cursor.execute(f"SELECT {_columns(INDUSTRY_FIELDS)} FROM Industry "
                                  "ORDER BY industry_id").fetchall()
        return [Industry(*row) for row in rows]

    def get_industry(self, industry_id):
        with self._transaction() as cursor:
            row = cursor.execute(f"SELECT {_columns(INDUSTRY_FIELDS)} FROM Industry "
                                 "WHERE industry_id = ?", industry_id).fetchone()
        return Industry(*row) if row else None

    # ---- businesses -----------------------------------------------------
    def add_business(self, business: Business):
        # Every column except the id, which SQL Server numbers itself (IDENTITY).
        names = BUSINESS_FIELDS[1:]
        values = [getattr(business, name) for name in names]
        with self._transaction() as cursor:
            new_id = cursor.execute(
                f"INSERT INTO Business ({_columns(names)}) OUTPUT INSERTED.business_id "
                f"VALUES ({_placeholders(len(names))})", *values).fetchone()[0]
        stored = copy.copy(business)
        stored.business_id = new_id
        return stored

    def get_business(self, business_id):
        with self._transaction() as cursor:
            row = cursor.execute(f"SELECT {_columns(BUSINESS_FIELDS)} FROM Business "
                                 "WHERE business_id = ?", business_id).fetchone()
        return Business(*row) if row else None

    def get_businesses_for_user(self, user_id):
        with self._transaction() as cursor:
            rows = cursor.execute(f"SELECT {_columns(BUSINESS_FIELDS)} FROM Business "
                                  "WHERE user_id = ? ORDER BY business_id", user_id).fetchall()
        return [Business(*row) for row in rows]

    def update_business(self, business: Business):
        with self._transaction() as cursor:
            self._update_business(cursor, business)

    def _update_business(self, cursor, business):
        # Only the figures that change month by month; the set-up values never do.
        cursor.execute(
            "UPDATE Business SET price = ?, marketing_budget = ?, current_month = ?, "
            "cash = ?, stock = ? WHERE business_id = ?",
            business.price, business.marketing_budget, business.current_month,
            business.cash, business.stock, business.business_id)

    # ---- monthly results ------------------------------------------------
    def add_result(self, result: MonthResult):
        with self._transaction() as cursor:
            self._insert_result(cursor, result)

    def _insert_result(self, cursor, result):
        values = [getattr(result, name) for name in RESULT_FIELDS]
        # market_factor is a float in Python but DECIMAL(4,3) in the table.
        values[RESULT_FIELDS.index("market_factor")] = Decimal(str(round(result.market_factor, 3)))
        cursor.execute(f"INSERT INTO MonthlyResult ({_columns(RESULT_FIELDS)}) "
                       f"VALUES ({_placeholders(len(RESULT_FIELDS))})", *values)

    def get_results(self, business_id):
        """Results for one business, in month order."""
        with self._transaction() as cursor:
            rows = cursor.execute(f"SELECT {_columns(RESULT_FIELDS)} FROM MonthlyResult "
                                  "WHERE business_id = ? ORDER BY month_no",
                                  business_id).fetchall()
        results = []
        for row in rows:
            result = MonthResult(*row)
            result.market_factor = float(result.market_factor)
            results.append(result)
        return results

    def save_month(self, result: MonthResult, business: Business):
        """Store the month and move the business on in ONE transaction: both
        happen, or (if either fails) neither does."""
        with self._transaction() as cursor:
            self._insert_result(cursor, result)
            self._update_business(cursor, business)

    # ---- glossary -------------------------------------------------------
    def get_glossary(self):
        with self._transaction() as cursor:
            rows = cursor.execute("SELECT term, definition, ISNULL(example, N'') "
                                  "FROM GlossaryTerm ORDER BY term_id").fetchall()
        return [GlossaryTerm(*row) for row in rows]
