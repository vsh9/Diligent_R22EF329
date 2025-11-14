"""Test suite for data validation logic."""
from __future__ import annotations

import csv
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest import TestCase

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validation.validate_data import (
    SCHEMA_CONFIG,
    load_and_validate_schema,
    parse_date,
    parse_float,
    parse_int,
    validate_subscriptions_logic,
    validate_usage_rules,
)


class TestValidation(TestCase):
    """Test validation components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.raw_dir = self.temp_dir / "data" / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def test_parse_int(self):
        """Test integer parsing."""
        self.assertEqual(parse_int("123"), 123)
        self.assertEqual(parse_int("0"), 0)
        with self.assertRaises(ValueError):
            parse_int("abc")

    def test_parse_float(self):
        """Test float parsing."""
        self.assertEqual(parse_float("123.45"), 123.45)
        self.assertEqual(parse_float("0.5"), 0.5)
        with self.assertRaises(ValueError):
            parse_float("abc")

    def test_parse_date(self):
        """Test date parsing."""
        result = parse_date("2024-01-15")
        self.assertIsInstance(result, date)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)

    def test_schema_validation_customers(self):
        """Test customers schema validation."""
        # Create valid customers CSV
        csv_file = self.raw_dir / "customers.csv"
        with csv_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["customer_id", "name", "email", "signup_date", "device_type", "country"],
            )
            writer.writeheader()
            writer.writerow({
                "customer_id": "1",
                "name": "Test User",
                "email": "test@example.com",
                "signup_date": "2024-01-01",
                "device_type": "mobile",
                "country": "United States",
            })

        # Temporarily override the path in SCHEMA_CONFIG
        original_path = SCHEMA_CONFIG["customers"]["path"]
        SCHEMA_CONFIG["customers"]["path"] = csv_file
        try:
            valid_rows, invalid_count = load_and_validate_schema("customers")
            self.assertEqual(len(valid_rows), 1)
            self.assertEqual(invalid_count, 0)
        finally:
            SCHEMA_CONFIG["customers"]["path"] = original_path

    def test_schema_validation_missing_column(self):
        """Test schema validation catches missing columns."""
        csv_file = self.raw_dir / "customers_bad.csv"
        with csv_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["customer_id", "name"])  # Missing columns
            writer.writeheader()
            writer.writerow({"customer_id": "1", "name": "Test"})

        # Temporarily override the path in SCHEMA_CONFIG
        original_path = SCHEMA_CONFIG["customers"]["path"]
        SCHEMA_CONFIG["customers"]["path"] = csv_file
        try:
            with self.assertRaises(ValueError):  # Should fail due to missing columns
                load_and_validate_schema("customers")
        finally:
            SCHEMA_CONFIG["customers"]["path"] = original_path

    def test_schema_validation_invalid_type(self):
        """Test schema validation catches type errors."""
        csv_file = self.raw_dir / "customers_bad2.csv"
        with csv_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["customer_id", "name", "email", "signup_date", "device_type", "country"],
            )
            writer.writeheader()
            writer.writerow({
                "customer_id": "not_an_int",  # Invalid type
                "name": "Test",
                "email": "test@example.com",
                "signup_date": "2024-01-01",
                "device_type": "mobile",
                "country": "United States",
            })

        # Temporarily override the path in SCHEMA_CONFIG
        original_path = SCHEMA_CONFIG["customers"]["path"]
        SCHEMA_CONFIG["customers"]["path"] = csv_file
        try:
            _, invalid_count = load_and_validate_schema("customers")
            self.assertEqual(invalid_count, 1)  # Should fail due to invalid customer_id
        finally:
            SCHEMA_CONFIG["customers"]["path"] = original_path

    def test_referential_integrity(self):
        """Test referential integrity validation."""
        # Create customers CSV
        customers_file = self.raw_dir / "customers.csv"
        with customers_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["customer_id", "name", "email", "signup_date", "device_type", "country"],
            )
            writer.writeheader()
            writer.writerow({
                "customer_id": "1",
                "name": "Test User",
                "email": "test@example.com",
                "signup_date": "2024-01-01",
                "device_type": "mobile",
                "country": "United States",
            })

        # Create usage_logs CSV with valid and invalid customer_id
        usage_file = self.raw_dir / "usage_logs.csv"
        with usage_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["usage_id", "customer_id", "content_id", "timestamp", "duration_watched", "completion_rate"],
            )
            writer.writeheader()
            writer.writerow({
                "usage_id": "1",
                "customer_id": "1",  # Valid
                "content_id": "1",
                "timestamp": "2024-01-01T10:00:00",
                "duration_watched": "30",
                "completion_rate": "0.5",
            })
            writer.writerow({
                "usage_id": "2",
                "customer_id": "999",  # Invalid - doesn't exist
                "content_id": "1",
                "timestamp": "2024-01-01T10:00:00",
                "duration_watched": "30",
                "completion_rate": "0.5",
            })

        # Load customers
        with customers_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            customers = list(reader)
        customer_ids = {row["customer_id"] for row in customers}

        # Load and validate usage logs schema first
        original_path = SCHEMA_CONFIG["usage_logs"]["path"]
        SCHEMA_CONFIG["usage_logs"]["path"] = usage_file
        try:
            usage_rows, _ = load_and_validate_schema("usage_logs")
            # Now check referential integrity manually
            valid_rows = []
            invalid_count = 0
            for row in usage_rows:
                if str(row["customer_id"]) in customer_ids:
                    valid_rows.append(row)
                else:
                    invalid_count += 1
            self.assertEqual(len(valid_rows), 1)  # Only first row is valid
            self.assertEqual(invalid_count, 1)  # Second row has invalid customer_id
        finally:
            SCHEMA_CONFIG["usage_logs"]["path"] = original_path

    def test_logical_validation_subscriptions(self):
        """Test logical validation for subscriptions."""
        subscriptions = [
            {
                "subscription_id": 1,
                "customer_id": 1,
                "plan_id": 1,
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 12, 31),  # Valid: end > start
                "auto_renew": True,
                "_line": 2,
            },
            {
                "subscription_id": 2,
                "customer_id": 1,
                "plan_id": 1,
                "start_date": date(2024, 12, 31),
                "end_date": date(2024, 1, 1),  # Invalid: end < start
                "auto_renew": True,
                "_line": 3,
            },
        ]

        valid_rows, invalid_count = validate_subscriptions_logic(subscriptions)
        self.assertEqual(len(valid_rows), 1)
        self.assertEqual(invalid_count, 1)

    def test_logical_validation_usage_logs(self):
        """Test logical validation for usage logs."""
        # Create content CSV for duration lookup
        content_file = self.raw_dir / "content.csv"
        with content_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["content_id", "title", "genre", "duration_minutes"])
            writer.writeheader()
            writer.writerow({
                "content_id": "1",
                "title": "Test Movie",
                "genre": "movie",
                "duration_minutes": "120",
            })

        # Load content for duration lookup
        with content_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            content = list(reader)
        content_durations = {int(row["content_id"]): int(row["duration_minutes"]) for row in content}

        usage_logs = [
            {
                "usage_id": 1,
                "customer_id": 1,
                "content_id": 1,
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "duration_watched": 60,  # Valid: 60 <= 120
                "completion_rate": 0.5,  # Valid: 0 <= 0.5 <= 1
                "_line": 2,
            },
            {
                "usage_id": 2,
                "customer_id": 1,
                "content_id": 1,
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "duration_watched": 150,  # Invalid: 150 > 120
                "completion_rate": 0.5,
                "_line": 3,
            },
            {
                "usage_id": 3,
                "customer_id": 1,
                "content_id": 1,
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "duration_watched": 60,
                "completion_rate": 1.5,  # Invalid: 1.5 > 1
                "_line": 4,
            },
        ]

        customer_ids = {1}  # Mock customer IDs for test
        valid_rows, invalid_count = validate_usage_rules(usage_logs, customer_ids, content_durations)
        self.assertEqual(len(valid_rows), 1)  # Only first row is valid
        self.assertEqual(invalid_count, 2)  # Second and third rows fail


if __name__ == "__main__":
    import unittest

    unittest.main()

