"""Create or upgrade the SQL Server database.

Run from the project folder:

    python setup_db.py

1. The first time, copies config.example.ini to config.ini (check the server name).
2. Creates the database if it doesn't exist yet.
3. Runs every script in database/ that hasn't run before, in file-name order,
   and records each one in the SchemaVersion table so it never runs twice.

Running it again is safe: with nothing new to do, it changes nothing.
"""
import re
import shutil
import sys
from pathlib import Path

import pyodbc

from data.connection import CONFIG_FILE, EXAMPLE_CONFIG_FILE, connect, load_settings

SCRIPTS_FOLDER = Path(__file__).resolve().parent / "database"

# "GO" is not SQL: it is an instruction to SSMS to send the text so far as one
# batch. pyodbc doesn't understand it, so each script is split on GO lines here.
GO_LINE = re.compile(r"^\s*GO\s*$", re.IGNORECASE | re.MULTILINE)

# A database name can't be passed as a ? parameter, so it is checked instead.
SAFE_NAME = re.compile(r"^[A-Za-z0-9_]{1,100}$")


class ScriptFailed(Exception):
    """A numbered script could not run. Nothing from that script was kept."""


def create_database(settings) -> bool:
    """Create the database if it is missing. Returns True if it was created."""
    name = settings["database"]
    if not SAFE_NAME.fullmatch(name):
        raise ValueError(f"Database name {name!r} may only use letters, numbers and _.")
    # CREATE DATABASE can't run inside a transaction, hence autocommit.
    connection = connect(settings, database="master", autocommit=True)
    try:
        exists = connection.execute("SELECT DB_ID(?)", name).fetchone()[0] is not None
        if not exists:
            connection.execute(f"CREATE DATABASE [{name}]")
        return not exists
    finally:
        connection.close()


def split_batches(sql_text):
    """The batches of a script: the text between GO lines, without empty ones."""
    batches = []
    for batch in GO_LINE.split(sql_text):
        if batch.strip():
            batches.append(batch.strip())
    return batches


def pending_scripts(already_run):
    """Numbered scripts not yet recorded in SchemaVersion, in file-name order.

    sorted() is fine here: this is setup tooling, not one of the program's
    sort features (those use logic/algorithms.py).
    """
    scripts = sorted(SCRIPTS_FOLDER.glob("[0-9][0-9][0-9]_*.sql"))
    return [script for script in scripts if script.name not in already_run]


def apply_scripts(settings) -> list:
    """Run each pending script in its own transaction. Returns the names that ran."""
    connection = connect(settings)
    try:
        connection.execute(
            "IF OBJECT_ID('SchemaVersion') IS NULL "
            "CREATE TABLE SchemaVersion ("
            "  script_name NVARCHAR(100) NOT NULL PRIMARY KEY,"
            "  applied_at  DATETIME2 NOT NULL DEFAULT SYSDATETIME())")
        connection.commit()
        already_run = {row[0] for row in connection.execute("SELECT script_name FROM SchemaVersion")}

        ran = []
        for script in pending_scripts(already_run):
            try:
                for batch in split_batches(script.read_text(encoding="utf-8-sig")):
                    connection.execute(batch)
                connection.execute("INSERT INTO SchemaVersion (script_name) VALUES (?)",
                                   script.name)
                connection.commit()
            except pyodbc.Error as error:
                # SQL Server can undo CREATE TABLE too, so a failed script leaves nothing.
                connection.rollback()
                raise ScriptFailed(f"{script.name} failed: {error}") from error
            ran.append(script.name)
        return ran
    finally:
        connection.close()


def main():
    if not CONFIG_FILE.exists():
        shutil.copy(EXAMPLE_CONFIG_FILE, CONFIG_FILE)
        print(f"Created {CONFIG_FILE.name} from {EXAMPLE_CONFIG_FILE.name}. "
              "If setup fails, check the server name in it.")
    settings = load_settings()
    if len(sys.argv) > 1:
        settings["database"] = sys.argv[1]      # e.g. a separate test database

    print(f"Server {settings['server']}, database {settings['database']}")
    try:
        if create_database(settings):
            print(f"  created database {settings['database']}")
        ran = apply_scripts(settings)
    except pyodbc.Error as error:
        print("Could not connect to SQL Server. Check it is running and that the server "
              f"name in {CONFIG_FILE.name} is right.\n  {error}")
        return 1
    except ScriptFailed as error:
        print(f"Stopped: {error}")
        return 1

    for name in ran:
        print(f"  ran {name}")
    print("Up to date." if not ran else f"Done: {len(ran)} script(s) run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
