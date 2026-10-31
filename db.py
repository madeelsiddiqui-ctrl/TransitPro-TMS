"""
Database connectivity layer.

The web application talks to the database ONLY through this module.
It supports MySQL (via PyMySQL) and SQLite (built into Python) with the
same SQL, so the project can be demonstrated with MySQL Workbench or run
anywhere without installing a database server.
"""
import os
import re
import sqlite3

import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")

try:
    import pymysql
    import pymysql.cursors
    MYSQL_ERRORS = (pymysql.err.IntegrityError, pymysql.err.OperationalError,
                    pymysql.err.DataError, pymysql.err.InternalError)
    MYSQL_INTEGRITY = (pymysql.err.IntegrityError,)
except ImportError:  # PyMySQL not installed -> SQLite only
    pymysql = None
    MYSQL_ERRORS = ()
    MYSQL_INTEGRITY = ()

# Errors raised when a constraint (PK, FK, UNIQUE, CHECK, NOT NULL) is violated
DB_ERRORS = (sqlite3.IntegrityError, sqlite3.OperationalError) + MYSQL_ERRORS

ACTIVE_ENGINE = config.DB_ENGINE.lower()


# ---------------------------------------------------------------------------
# connections
# ---------------------------------------------------------------------------
def _mysql_connect(with_db=True):
    return pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE if with_db else None,
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        autocommit=False,
    )


def _sqlite_connect():
    conn = sqlite3.connect(config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")      # enforce FOREIGN KEYs
    return conn


def connect():
    if ACTIVE_ENGINE == "mysql":
        return _mysql_connect()
    return _sqlite_connect()


def sql(statement):
    """MySQL uses %s placeholders, SQLite uses ?  -> convert when needed."""
    return statement if ACTIVE_ENGINE == "mysql" else statement.replace("%s", "?")


def _rows(cursor):
    rows = cursor.fetchall()
    if ACTIVE_ENGINE == "mysql":
        return list(rows)
    return [dict(r) for r in rows]


def query(conn, statement, params=()):
    """Run a SELECT and return a list of dict rows."""
    cur = conn.cursor()
    cur.execute(sql(statement), params)
    rows = _rows(cur)
    cur.close()
    return rows


def query_one(conn, statement, params=()):
    rows = query(conn, statement, params)
    return rows[0] if rows else None


def execute(conn, statement, params=()):
    """Run INSERT / UPDATE / DELETE inside a transaction (COMMIT or ROLLBACK)."""
    cur = conn.cursor()
    try:
        cur.execute(sql(statement), params)
        conn.commit()
        return cur.lastrowid, cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def column_names(cursor_description):
    return [d[0] for d in cursor_description]


def raw_select(conn, statement):
    """Used by the read-only SQL console: returns (columns, rows)."""
    cur = conn.cursor()
    cur.execute(statement)
    cols = column_names(cur.description) if cur.description else []
    rows = _rows(cur)
    cur.close()
    return cols, rows


# ---------------------------------------------------------------------------
# database creation
# ---------------------------------------------------------------------------
def _split_sql(text):
    """Strip comments / USE lines and split a .sql file into statements."""
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("--") or s.upper().startswith("USE ") or s.upper().startswith("PRAGMA"):
            continue
        lines.append(line)
    return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


def _read(name):
    with open(os.path.join(DB_DIR, name), encoding="utf-8") as f:
        return f.read()


def init_sqlite(force=False):
    if os.path.exists(config.SQLITE_PATH):
        if not force:
            return False
        os.remove(config.SQLITE_PATH)
    conn = _sqlite_connect()
    conn.executescript(_read("schema_sqlite.sql"))
    for st in _split_sql(_read("02_seed_data.sql")):
        conn.execute(st)
    conn.commit()
    conn.close()
    return True


def init_mysql():
    """Create transport_db on MySQL from the same .sql files used in Workbench."""
    conn = _mysql_connect(with_db=False)
    cur = conn.cursor()
    for st in _split_sql(_read("01_schema_mysql.sql")):
        cur.execute(st)
        if st.upper().startswith("CREATE DATABASE"):
            cur.execute("USE " + config.MYSQL_DATABASE)
    for st in _split_sql(_read("02_seed_data.sql")):
        cur.execute(st)
    conn.commit()
    conn.close()


def choose_engine():
    """Try MySQL first (if configured). If the server is unreachable fall back
    to SQLite so the application still runs, and say so clearly."""
    global ACTIVE_ENGINE
    ACTIVE_ENGINE = config.DB_ENGINE.lower()
    if ACTIVE_ENGINE == "mysql":
        if pymysql is None:
            print("[TMS] PyMySQL not installed -> using SQLite.  (pip install pymysql)")
            ACTIVE_ENGINE = "sqlite"
        else:
            try:
                try:
                    c = _mysql_connect()
                except pymysql.err.OperationalError as e:
                    if e.args and e.args[0] == 1049:          # Unknown database -> build it
                        print("[TMS] Database 'transport_db' not found in MySQL - creating it now...")
                        init_mysql()
                        print("[TMS] Done: 7 tables + sample data created in MySQL.")
                        c = _mysql_connect()
                    else:
                        raise
                c.close()
                print("")
                print("  ============================================================")
                print("   SUCCESS: connected to MySQL database 'transport_db'")
                print("   Open MySQL Workbench > Schemas > refresh to see the tables")
                print("  ============================================================")
                return ACTIVE_ENGINE
            except Exception as e:  # noqa: BLE001
                code = e.args[0] if getattr(e, "args", None) else None
                print("")
                print("  ------------------------------------------------------------")
                if code == 1045:
                    print("   MySQL said: WRONG PASSWORD for user 'root'.")
                    print("   Close this window and run START_HERE again with the")
                    print("   correct password (the one you use in MySQL Workbench).")
                elif code == 2003:
                    print("   MySQL server is NOT RUNNING on this computer.")
                    print("   Start it: Windows key > type 'Services' > MySQL80 > Start")
                else:
                    print("   Could not connect to MySQL:", e)
                print("   For now the app will run with the built-in SQLite database")
                print("   (same tables, same data) so you can still use it.")
                print("  ------------------------------------------------------------")
                ACTIVE_ENGINE = "sqlite"
    if init_sqlite():
        print("[TMS] SQLite database created with sample data.")
    print("[TMS] Using SQLite:", config.SQLITE_PATH)
    return ACTIVE_ENGINE


def friendly_error(err):
    """Turn a raw DB error into a readable explanation of which constraint failed."""
    msg = str(err.args[1] if ACTIVE_ENGINE == "mysql" and len(getattr(err, "args", ())) > 1 else err)
    low = msg.lower()
    if "foreign key" in low:
        if "delete" in low or "parent" in low or "cannot delete" in low:
            return "FOREIGN KEY constraint: this record is referenced by other records (ON DELETE RESTRICT)."
        return "FOREIGN KEY constraint failed: " + msg
    if "unique" in low or "duplicate" in low:
        return "UNIQUE constraint: a record with this value already exists. (" + msg + ")"
    if "check" in low or "chk_" in low:
        m = re.search(r"(chk_\w+)", msg)
        return "CHECK constraint violated" + (f" ({m.group(1)})" if m else "") + ": " + msg
    if "not null" in low or "cannot be null" in low:
        return "NOT NULL constraint: a required field is empty. (" + msg + ")"
    return msg
