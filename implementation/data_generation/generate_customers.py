"""Generate synthetic customers dataset."""
from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

NUM_CUSTOMERS = 1000
DEVICE_TYPES = ["mobile", "tablet", "desktop", "smart_tv"]
COUNTRIES = ["United States", "Canada", "United Kingdom", "Australia", "India"]
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "customers.csv"
SEED = 42


def random_signup_date() -> datetime:
    """Return a signup date within the last 2 years."""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=730)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).date()


def generate_customers() -> list[dict[str, str]]:
    """Generate customer records."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    fake = Faker("en_US")
    Faker.seed(SEED)
    random.seed(SEED)

    customers: list[dict[str, str]] = []
    for idx in range(1, NUM_CUSTOMERS + 1):
        name = fake.name()
        email = f"{name.lower().replace(' ', '.')}.{idx}@example.com"
        signup = random_signup_date()
        record = {
            "customer_id": str(idx),
            "name": name,
            "email": email,
            "signup_date": signup.isoformat(),
            "device_type": random.choice(DEVICE_TYPES),
            "country": random.choice(COUNTRIES),
        }
        customers.append(record)
    return customers


def write_csv(rows: list[dict[str, str]]) -> None:
    """Write customer data to CSV."""
    fieldnames = [
        "customer_id",
        "name",
        "email",
        "signup_date",
        "device_type",
        "country",
    ]
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_stats(rows: list[dict[str, str]]) -> None:
    """Print basic statistics."""
    device_counts: dict[str, int] = {device: 0 for device in DEVICE_TYPES}
    for row in rows:
        device_counts[row["device_type"]] += 1
    print(f"Generated {len(rows)} customers -> {OUTPUT_FILE}")
    print("Device distribution:")
    for device, count in device_counts.items():
        pct = (count / len(rows)) * 100
        print(f"  {device}: {count} ({pct:.1f}%)")


def main() -> None:
    customers = generate_customers()
    write_csv(customers)
    print_stats(customers)


if __name__ == "__main__":
    main()
