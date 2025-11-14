"""Generate subscription plans dataset."""
from __future__ import annotations

import csv
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "plans.csv"

PLANS = [
    {"plan_id": "1", "name": "Basic", "price": "8.99"},
    {"plan_id": "2", "name": "Standard", "price": "13.99"},
    {"plan_id": "3", "name": "Premium", "price": "18.99"},
]


def write_plans() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["plan_id", "name", "price"])
        writer.writeheader()
        writer.writerows(PLANS)
    print(f"Generated {len(PLANS)} plans -> {OUTPUT_FILE}")


def main() -> None:
    write_plans()


if __name__ == "__main__":
    main()
