"""Opens connections to SQL Server using the settings in config.ini.

Only the data layer (and setup_db.py) uses this module: the logic and the
screens never know where data is stored.
"""
import configparser
from pathlib import Path

import pyodbc

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_FOLDER / "config.ini"
EXAMPLE_CONFIG_FILE = PROJECT_FOLDER / "config.example.ini"

# Give up after this many seconds if the server doesn't answer, so a stopped
# SQL Server produces a message quickly instead of a long freeze.
LOGIN_TIMEOUT_SECONDS = 5


def load_settings(path=CONFIG_FILE) -> dict:
    """The [database] section of config.ini as a plain dictionary."""
    parser = configparser.ConfigParser()
    if not parser.read(path, encoding="utf-8"):
        raise FileNotFoundError(f"{Path(path).name} not found. Run 'python setup_db.py' "
                                "first: it creates the file and the database.")
    return dict(parser["database"])


def _is_yes(value):
    return str(value).strip().lower() in ("yes", "true", "1")


def connection_string(settings, database=None) -> str:
    """Build the ODBC connection string. `database` overrides the one in settings."""
    parts = [
        f"DRIVER={{{settings['driver']}}}",
        f"SERVER={settings['server']}",
        f"DATABASE={database or settings['database']}",
    ]
    if _is_yes(settings.get("trusted_connection", "yes")):
        parts.append("Trusted_Connection=yes")
    else:
        parts.append(f"UID={settings['username']}")
        parts.append(f"PWD={settings['password']}")
    if _is_yes(settings.get("trust_server_certificate", "no")):
        parts.append("TrustServerCertificate=yes")
    return ";".join(parts)


def connect(settings, database=None, autocommit=False):
    """Open a connection. With autocommit off, changes need connection.commit()."""
    return pyodbc.connect(connection_string(settings, database), autocommit=autocommit,
                          timeout=LOGIN_TIMEOUT_SECONDS)
