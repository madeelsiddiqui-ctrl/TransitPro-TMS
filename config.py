"""
Configuration for the Transport Management System.

DB_ENGINE = "mysql"   -> connects to MySQL Server (use with MySQL Workbench)
DB_ENGINE = "sqlite"  -> uses a local file (database/transport.db), zero setup

Every value can also be overridden with an environment variable of the same name.
"""
import os

# ----- choose the database engine -----------------------------------------
DB_ENGINE = os.getenv("DB_ENGINE", "mysql")          # "mysql" or "sqlite"

# ----- MySQL settings (same as your MySQL Workbench connection) -----------
MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT     = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER     = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")   # <-- put YOUR MySQL root password here
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "transport_db")

# ----- SQLite settings -----------------------------------------------------
SQLITE_PATH = os.getenv(
    "SQLITE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "transport.db"),
)

# ----- Flask ---------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "tms-pgd-dsai-ned-2026")

# ----- Online demo (set DEMO_MODE=1 on the hosting server) ----------------
# Shows a "Live demo" banner with a button that restores the sample data.
DEMO_MODE = os.getenv("DEMO_MODE", "0") == "1"

# ----- Project / student profile (shown in the web interface) -------------
PROJECT = {
    "title":       "Transport Management System",
    "short":       "TMS",
    "student":     "Muhammad Adeel Siddiqi",
    "program":     "PGD - DSAI, Batch XIV",
    "reg_no":      "PGD/DSAI/Apr-26/312564",
    "course":      "RDBMS - Database Management Systems",
    "instructor":  "Sajid Majeed",
    "university":  "NED University of Engineering & Technology",
}
