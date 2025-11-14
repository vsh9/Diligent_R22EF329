"""Generate synthetic usage logs with behavioral rules."""
from __future__ import annotations

import csv
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
CUSTOMERS_FILE = RAW_DIR / "customers.csv"
CONTENT_FILE = RAW_DIR / "content.csv"
PLANS_FILE = RAW_DIR / "plans.csv"
SUBSCRIPTIONS_FILE = RAW_DIR / "subscriptions.csv"
OUTPUT_FILE = RAW_DIR / "usage_logs.csv"

NUM_LOGS = 20000
SEED = 46
LOOKBACK_DAYS = 60
WEEKEND_BIAS = 0.45  # > 2/7 to reflect higher activity
PLAN_ACTIVITY_WEIGHTS = {"Basic": 1.0, "Standard": 1.2, "Premium": 1.5}
PLAN_COMPLETION_BOUNDS = {
    "Basic": (0.25, 0.8),
    "Standard": (0.35, 0.9),
    "Premium": (0.5, 1.0),
}
CONTENT_WEIGHTS = {"movie": 0.5, "music": 0.3, "podcast": 0.2}


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required file missing: {path}")
    with path.open("r", newline="", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


def group_content_by_genre(content_rows: list[dict[str, str]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in content_rows:
        grouped[row["genre"]].append(
            {
                "content_id": row["content_id"],
                "genre": row["genre"],
                "duration_minutes": int(row["duration_minutes"]),
                "title": row["title"],
            }
        )
    return grouped


def derive_active_plans(sub_rows: list[dict[str, str]], plan_lookup: dict[str, str]) -> dict[str, str]:
    """Return latest active plan per customer."""
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=LOOKBACK_DAYS)
    latest_by_customer: dict[str, tuple[datetime.date, str]] = {}
    for row in sub_rows:
        start = datetime.fromisoformat(row["start_date"]).date()
        end_str = row["end_date"]
        end_date = datetime.fromisoformat(end_str).date() if end_str else None
        if end_date and end_date < cutoff:
            continue
        if start > datetime.now(timezone.utc).date():
            continue
        cust_id = row["customer_id"]
        existing = latest_by_customer.get(cust_id)
        if existing is None or start > existing[0]:
            latest_by_customer[cust_id] = (start, plan_lookup[row["plan_id"]])
    return {cust_id: plan_name for cust_id, (_, plan_name) in latest_by_customer.items()}


def prepare_customer_pool(plan_by_customer: dict[str, str]) -> tuple[list[str], list[float]]:
    customers = list(plan_by_customer.keys())
    weights = [PLAN_ACTIVITY_WEIGHTS.get(plan_by_customer[cid], 1.0) for cid in customers]
    return customers, weights


def biased_timestamp() -> datetime:
    now = datetime.now(timezone.utc)
    attempt_weekend = random.random() < WEEKEND_BIAS
    for _ in range(5):
        days_back = random.randint(0, LOOKBACK_DAYS - 1)
        candidate = now - timedelta(days=days_back)
        if attempt_weekend and candidate.weekday() < 5:
            continue
        if not attempt_weekend and candidate.weekday() >= 5:
            continue
        break
    else:
        candidate = now - timedelta(days=random.randint(0, LOOKBACK_DAYS - 1))
    hour = random.randint(6, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return candidate.replace(hour=hour, minute=minute, second=second, microsecond=0)


def choose_content(grouped_content: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    genres = list(CONTENT_WEIGHTS.keys())
    weights = [CONTENT_WEIGHTS[g] for g in genres]
    for _ in range(5):
        genre = random.choices(genres, weights=weights, k=1)[0]
        if grouped_content.get(genre):
            return random.choice(grouped_content[genre])
    genre = random.choice(list(grouped_content.keys()))
    return random.choice(grouped_content[genre])


def compute_duration(plan: str, content_duration: int, is_weekend: bool) -> tuple[int, float]:
    low, high = PLAN_COMPLETION_BOUNDS[plan]
    ratio = random.uniform(low, high)
    if is_weekend:
        ratio = min(1.0, ratio * 1.1)
    watched = max(1, int(content_duration * ratio))
    watched = min(watched, content_duration)
    completion = watched / content_duration
    noise = random.uniform(-0.05, 0.05)
    completion = max(0.05, min(1.0, completion + noise))
    return watched, round(completion, 2)


def generate_usage_logs() -> list[dict[str, Any]]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    random.seed(SEED)

    plans = load_csv(PLANS_FILE)
    plan_lookup = {row["plan_id"]: row["name"] for row in plans}
    subscriptions = load_csv(SUBSCRIPTIONS_FILE)
    plan_by_customer = derive_active_plans(subscriptions, plan_lookup)
    if not plan_by_customer:
        raise RuntimeError("No active subscriptions found for usage generation.")

    content_rows = load_csv(CONTENT_FILE)
    grouped_content = group_content_by_genre(content_rows)

    customer_ids, customer_weights = prepare_customer_pool(plan_by_customer)
    logs: list[dict[str, Any]] = []

    for usage_id in range(1, NUM_LOGS + 1):
        customer_id = random.choices(customer_ids, weights=customer_weights, k=1)[0]
        plan_name = plan_by_customer[customer_id]
        content = choose_content(grouped_content)
        timestamp = biased_timestamp()
        is_weekend = timestamp.weekday() >= 5
        duration_watched, completion = compute_duration(plan_name, content["duration_minutes"], is_weekend)
        logs.append(
            {
                "usage_id": str(usage_id),
                "customer_id": customer_id,
                "content_id": content["content_id"],
                "timestamp": timestamp.isoformat(),
                "duration_watched": str(duration_watched),
                "completion_rate": f"{completion:.2f}",
            }
        )
    return logs, plan_by_customer


def write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "usage_id",
        "customer_id",
        "content_id",
        "timestamp",
        "duration_watched",
        "completion_rate",
    ]
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_stats(rows: list[dict[str, Any]], plan_by_customer: dict[str, str]) -> None:
    weekend_count = sum(1 for row in rows if datetime.fromisoformat(row["timestamp"]).weekday() >= 5)
    avg_completion = sum(float(row["completion_rate"]) for row in rows) / len(rows)
    plan_freq: dict[str, int] = defaultdict(int)
    for plan in plan_by_customer.values():
        plan_freq[plan] += 1
    print(f"Generated {len(rows)} usage logs -> {OUTPUT_FILE}")
    print(f"Weekend events: {weekend_count} ({(weekend_count/len(rows))*100:.1f}%)")
    print(f"Average completion rate: {avg_completion:.2f}")
    for plan, count in plan_freq.items():
        print(f"Customers with {plan}: {count}")


def main() -> None:
    rows, plan_by_customer = generate_usage_logs()
    write_csv(rows)
    print_stats(rows, plan_by_customer)


if __name__ == "__main__":
    main()
