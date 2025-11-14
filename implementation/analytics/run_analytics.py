"""Compile analytics views and export aggregated reports."""
from __future__ import annotations

import csv
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "ecommerce.db"
VIEWS_DIR = Path(__file__).resolve().parent / "views"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "analytics.log"

VIEW_CONFIG = [
    {
        "name": "top_content_view",
        "sql_file": VIEWS_DIR / "top_content_view.sql",
        "output": PROCESSED_DIR / "top_content_report.csv",
    },
    {
        "name": "engagement_view",
        "sql_file": VIEWS_DIR / "engagement_metrics_view.sql",
        "output": PROCESSED_DIR / "engagement_report.csv",
    },
]


def utc_now() -> str:
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


def read_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL definition missing: {path}")
    return path.read_text(encoding="utf-8")


def compile_view(conn: sqlite3.Connection, view_name: str, sql_text: str) -> None:
    logging.info("%s | compiling view=%s", utc_now(), view_name)
    conn.execute(f"DROP VIEW IF EXISTS {view_name}")
    conn.executescript(sql_text)
    logging.info("%s | compiled view=%s successfully", utc_now(), view_name)


def query_view(conn: sqlite3.Connection, view_name: str) -> tuple[List[str], List[sqlite3.Row]]:
    cursor = conn.execute(f"SELECT * FROM {view_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return columns, rows


def export_csv(columns: Sequence[str], rows: Iterable[sqlite3.Row], output_path: Path) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[col] for col in columns])


def print_preview(view_name: str, columns: Sequence[str], rows: List[sqlite3.Row]) -> None:
    print(f"{view_name}: {len(rows)} rows")
    preview = rows[:5]
    for idx, row in enumerate(preview, start=1):
        sample = ", ".join(f"{col}={row[col]}" for col in columns)
        print(f"  {idx}. {sample}")
    if not preview:
        print("  (no rows)")
    print()


def run() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    init_logging()
    logging.info("%s | analytics run started | db=%s", utc_now(), DB_PATH.name)

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        for view in VIEW_CONFIG:
            try:
                sql_text = read_sql(view["sql_file"])
                compile_view(conn, view["name"], sql_text)
                columns, rows = query_view(conn, view["name"])
                export_csv(columns, rows, view["output"])
                logging.info(
                    "%s | view=%s | rows=%d | output=%s",
                    utc_now(),
                    view["name"],
                    len(rows),
                    view["output"].relative_to(PROJECT_ROOT),
                )
                print_preview(view["name"], columns, rows)
            except Exception as exc:  # pylint: disable=broad-except
                logging.error(
                    "%s | view=%s | error=%s",
                    utc_now(),
                    view["name"],
                    exc,
                )
                raise

    logging.info("%s | analytics run completed", utc_now())
    print("Analytics execution complete. Reports saved to data/processed/")


if __name__ == "__main__":
    run()

