"""Test suite for data generation scripts."""
from __future__ import annotations

import csv
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest import TestCase

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from implementation.data_generation.generate_customers import (
    COUNTRIES,
    DEVICE_TYPES,
    generate_customers,
)
from implementation.data_generation.generate_content import (
    DURATION_RULES,
    GENRE_RATIOS,
    generate_content,
)
from implementation.data_generation.generate_plans import PLANS


class TestDataGeneration(TestCase):
    """Test data generation components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.raw_dir = self.temp_dir / "data" / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def test_customers_generation(self):
        """Test customer generation produces valid records."""
        customers = generate_customers()
        self.assertEqual(len(customers), 1000)
        for customer in customers[:10]:  # Sample check
            self.assertIn("customer_id", customer)
            self.assertIn("name", customer)
            self.assertIn("email", customer)
            self.assertIn("signup_date", customer)
            self.assertIn("device_type", customer)
            self.assertIn("country", customer)
            self.assertIn(customer["device_type"], DEVICE_TYPES)
            self.assertIn(customer["country"], COUNTRIES)
            # Validate email format
            self.assertIn("@", customer["email"])
            # Validate date format
            datetime.fromisoformat(customer["signup_date"])

    def test_customers_csv_structure(self):
        """Test customers CSV has correct columns."""
        customers = generate_customers()
        output_file = self.raw_dir / "customers.csv"
        with output_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "customer_id",
                    "name",
                    "email",
                    "signup_date",
                    "device_type",
                    "country",
                ],
            )
            writer.writeheader()
            writer.writerows(customers[:10])

        with output_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 10)
            self.assertEqual(
                set(reader.fieldnames),
                {
                    "customer_id",
                    "name",
                    "email",
                    "signup_date",
                    "device_type",
                    "country",
                },
            )

    def test_plans_generation(self):
        """Test plans generation produces correct structure."""
        self.assertEqual(len(PLANS), 3)
        plan_names = {p["name"] for p in PLANS}
        self.assertEqual(plan_names, {"Basic", "Standard", "Premium"})
        prices = {float(p["price"]) for p in PLANS}
        self.assertEqual(prices, {8.99, 13.99, 18.99})

    def test_content_generation(self):
        """Test content generation respects genre ratios and duration rules."""
        content = generate_content()
        self.assertEqual(len(content), 300)

        genre_counts = {}
        for item in content:
            genre = item["genre"]
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
            duration = int(item["duration_minutes"])
            min_dur, max_dur = DURATION_RULES[genre]
            self.assertGreaterEqual(duration, min_dur)
            self.assertLessEqual(duration, max_dur)

        # Check approximate genre ratios (allow some variance)
        total = sum(genre_counts.values())
        for genre, expected_ratio in GENRE_RATIOS.items():
            actual_ratio = genre_counts.get(genre, 0) / total
            self.assertAlmostEqual(actual_ratio, expected_ratio, delta=0.05)

    def test_content_schema(self):
        """Test content has required fields."""
        content = generate_content()
        for item in content[:10]:
            self.assertIn("content_id", item)
            self.assertIn("title", item)
            self.assertIn("genre", item)
            self.assertIn("duration_minutes", item)
            self.assertIn(item["genre"], ["movie", "music", "podcast"])
            duration = int(item["duration_minutes"])
            self.assertGreater(duration, 0)


if __name__ == "__main__":
    import unittest

    unittest.main()

