"""Generate synthetic subscriptions data."""
from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
CUSTOMERS_FILE = RAW_DIR / "customers.csv"
PLANS_FILE = RAW_DIR / "plans.csv"
OUTPUT_FILE = RAW_DIR / "subscriptions.csv"
NUM_SUBSCRIPTIONS = 1200
SEED = 45
MAX_LOOKBACK_DAYS = 548  # ~18 months
PLAN_WEIGHTS = {"1": 0.4, "2": 0.35, "3": 0.25}


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required file missing: {path}")
    with path.open("r", newline="", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


def choose_plan_id() -> str:
    plan_ids = list(PLAN_WEIGHTS.keys())
    weights = [PLAN_WEIGHTS[pid] for pid in plan_ids]
    return random.choices(plan_ids, weights=weights, k=1)[0]


def random_start(signup_date: datetime.date) -> datetime.date:
    today = datetime.now(timezone.utc).date()
    earliest = max(signup_date, today - timedelta(days=MAX_LOOKBACK_DAYS))
    if earliest >= today:
        return today
    delta_days = (today - earliest).days
    offset = random.randint(0, delta_days)
    return earliest + timedelta(days=offset)


def determine_end_date(start_date: datetime.date) -> str:
    today = datetime.now(timezone.utc).date()
    if random.random() < 0.3:
        return ""
    duration_days = random.randint(30, 365)
    end_date = start_date + timedelta(days=duration_days)
    if end_date > today:
        return ""
    return end_date.isoformat()


def generate_subscriptions() -> list[dict[str, Any]]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    random.seed(SEED)

    customers = load_csv(CUSTOMERS_FILE)
    for customer in customers:
        customer["signup_date"] = datetime.fromisoformat(customer["signup_date"]).date()
    loads_plans = load_csv(PLANS_FILE)
    plan_lookup = {plan["plan_id"]: plan["name"] for plan in loads_plans}

    subscriptions: list[dict[str, Any]] = []
    today = datetime.now(timezone.utc).date()
    for sub_id in range(1, NUM_SUBSCRIPTIONS + 1):
        customer = random.choice(customers)
        plan_id = choose_plan_id()
        start_date = random_start(customer["signup_date"])
        if start_date > today:
            start_date = today
        end_date = determine_end_date(start_date)
        subscriptions.append(
            {
                "subscription_id": str(sub_id),
                "customer_id": customer["customer_id"],
                "plan_id": plan_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date,
                "auto_renew": str(random.random() < 0.7),
            }
        )
    return subscriptions, plan_lookup


def write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "subscription_id",
        "customer_id",
        "plan_id",
        "start_date",
        "end_date",
        "auto_renew",
    ]
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_stats(rows: list[dict[str, Any]], plan_lookup: dict[str, str]) -> None:
    plan_counts: dict[str, int] = {pid: 0 for pid in plan_lookup}
    active = 0
    for row in rows:
        plan_counts[row["plan_id"]] += 1
        if row["end_date"] == "":
            active += 1
    print(f"Generated {len(rows)} subscriptions -> {OUTPUT_FILE}")
    for pid, count in plan_counts.items():
        pct = (count / len(rows)) * 100
        print(f"  {plan_lookup[pid]}: {count} ({pct:.1f}%)")
    print(f"Active subscriptions (no end_date): {active}")


def main() -> None:
    rows, plan_lookup = generate_subscriptions()
    write_csv(rows)
    print_stats(rows, plan_lookup)


if __name__ == "__main__":
    main()
