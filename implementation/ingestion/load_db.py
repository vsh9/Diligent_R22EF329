"""Create SQLite database and ingest raw CSV datasets."""
from __future__ import annotations

import csv
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "ecommerce.db"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "ingestion.log"


def utc_now() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def init_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cursor.fetchone() is not None


def create_tables(conn: sqlite3.Connection) -> None:
    """Create tables with required schema constraints."""
    schema_statements = [
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            signup_date TEXT NOT NULL,
            device_type TEXT NOT NULL,
            country TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS plans (
            plan_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS content (
            content_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            auto_renew INTEGER NOT NULL CHECK (auto_renew IN (0, 1)),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS usage_logs (
            usage_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            content_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            duration_watched INTEGER NOT NULL,
            completion_rate REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (content_id) REFERENCES content(content_id)
        );
        """,
    ]
    for statement in schema_statements:
        conn.execute(statement)


def read_csv_rows(path: Path) -> Iterable[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required source CSV missing: {path}")
    with path.open("r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row


def transform_rows(
    rows: Iterable[dict[str, str]], transformer: Callable[[dict[str, str]], Tuple]
) -> List[Tuple]:
    return [transformer(row) for row in rows]


def ingest_table(
    conn: sqlite3.Connection,
    table: str,
    csv_path: Path,
    columns: Sequence[str],
    transformer: Callable[[dict[str, str]], Tuple],
) -> None:
    existed = table_exists(conn, table)
    if not existed:
        logging.info("%s | %s | table created (schema applied)", utc_now(), table)
    else:
        conn.execute(f"DELETE FROM {table}")
    rows = transform_rows(read_csv_rows(csv_path), transformer)
    if rows:
        placeholders = ", ".join(["?"] * len(columns))
        conn.executemany(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", rows
        )
    conn.commit()
    action = "replaced" if existed else "created"
    logging.info(
        "%s | %s | %s | rows=%d | source=%s",
        utc_now(),
        table,
        action,
        len(rows),
        csv_path.name,
    )


def load_all_tables(conn: sqlite3.Connection) -> None:
    configs = [
        {
            "table": "customers",
            "csv": RAW_DIR / "customers.csv",
            "columns": [
                "customer_id",
                "name",
                "email",
                "signup_date",
                "device_type",
                "country",
            ],
            "transformer": lambda r: (
                int(r["customer_id"]),
                r["name"],
                r["email"],
                r["signup_date"],
                r["device_type"],
                r["country"],
            ),
        },
        {
            "table": "plans",
            "csv": RAW_DIR / "plans.csv",
            "columns": ["plan_id", "name", "price"],
            "transformer": lambda r: (
                int(r["plan_id"]),
                r["name"],
                float(r["price"]),
            ),
        },
        {
            "table": "content",
            "csv": RAW_DIR / "content.csv",
            "columns": ["content_id", "title", "genre", "duration_minutes"],
            "transformer": lambda r: (
                int(r["content_id"]),
                r["title"],
                r["genre"],
                int(r["duration_minutes"]),
            ),
        },
        {
            "table": "subscriptions",
            "csv": RAW_DIR / "subscriptions.csv",
            "columns": [
                "subscription_id",
                "customer_id",
                "plan_id",
                "start_date",
                "end_date",
                "auto_renew",
            ],
            "transformer": lambda r: (
                int(r["subscription_id"]),
                int(r["customer_id"]),
                int(r["plan_id"]),
                r["start_date"],
                r["end_date"] or None,
                1 if r["auto_renew"].lower() in {"true", "1"} else 0,
            ),
        },
        {
            "table": "usage_logs",
            "csv": RAW_DIR / "usage_logs.csv",
            "columns": [
                "usage_id",
                "customer_id",
                "content_id",
                "timestamp",
                "duration_watched",
                "completion_rate",
            ],
            "transformer": lambda r: (
                int(r["usage_id"]),
                int(r["customer_id"]),
                int(r["content_id"]),
                r["timestamp"],
                int(r["duration_watched"]),
                float(r["completion_rate"]),
            ),
        },
    ]

    for config in configs:
        ingest_table(
            conn=conn,
            table=config["table"],
            csv_path=config["csv"],
            columns=config["columns"],
            transformer=config["transformer"],
        )


def main() -> None:
    init_logging()
    logging.info("%s | ingestion started | db=%s", utc_now(), DB_PATH.name)
    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        create_tables(conn)
        load_all_tables(conn)
        logging.info("%s | ingestion completed successfully", utc_now())
    finally:
        conn.close()


if __name__ == "__main__":
    main()

