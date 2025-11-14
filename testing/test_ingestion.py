"""Test suite for SQLite ingestion pipeline."""
from __future__ import annotations

import csv
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest import TestCase

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from implementation.ingestion.load_db import (
    create_tables,
    ingest_table,
    table_exists,
)


class TestIngestion(TestCase):
    """Test ingestion components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_ecommerce.db"
        self.raw_dir = self.temp_dir / "data" / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def test_table_creation(self):
        """Test tables are created with correct schema."""
        conn = sqlite3.connect(str(self.db_path))
        create_tables(conn)
        conn.commit()

        expected_tables = [
            "customers",
            "plans",
            "content",
            "subscriptions",
            "usage_logs",
        ]
        for table in expected_tables:
            self.assertTrue(table_exists(conn, table))

        # Check foreign key constraints are enabled
        cursor = conn.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        self.assertEqual(fk_enabled, 1)

        conn.close()

    def test_customers_table_schema(self):
        """Test customers table has correct columns."""
        conn = sqlite3.connect(str(self.db_path))
        create_tables(conn)
        conn.commit()

        cursor = conn.execute("PRAGMA table_info(customers)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        self.assertIn("customer_id", columns)
        self.assertIn("name", columns)
        self.assertIn("email", columns)
        self.assertIn("signup_date", columns)
        self.assertIn("device_type", columns)
        self.assertIn("country", columns)
        self.assertEqual(columns["customer_id"], "INTEGER")

        conn.close()

    def test_ingest_sample_data(self):
        """Test ingesting sample CSV data."""
        # Create sample customers CSV
        csv_file = self.raw_dir / "customers.csv"
        with csv_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["customer_id", "name", "email", "signup_date", "device_type", "country"])
            writer.writerow(["1", "Test User", "test@example.com", "2024-01-01", "mobile", "United States"])

        conn = sqlite3.connect(str(self.db_path))
        create_tables(conn)

        # Ingest the CSV with transformer function
        columns = ["customer_id", "name", "email", "signup_date", "device_type", "country"]
        transformer = lambda r: (
            int(r["customer_id"]),
            r["name"],
            r["email"],
            r["signup_date"],
            r["device_type"],
            r["country"],
        )
        ingest_table(conn, "customers", csv_file, columns, transformer)
        conn.commit()

        # Verify data was inserted
        cursor = conn.execute("SELECT COUNT(*) FROM customers")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)

        cursor = conn.execute("SELECT name FROM customers WHERE customer_id = 1")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Test User")

        conn.close()

    def test_foreign_key_constraints(self):
        """Test foreign key constraints are enforced."""
        conn = sqlite3.connect(str(self.db_path))
        create_tables(conn)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()

        # Try to insert subscription with invalid customer_id (should fail)
        try:
            conn.execute(
                "INSERT INTO subscriptions (subscription_id, customer_id, plan_id, start_date, auto_renew) VALUES (1, 9999, 1, '2024-01-01', 'True')"
            )
            conn.commit()
            self.fail("Foreign key constraint should have been violated")
        except sqlite3.IntegrityError:
            pass  # Expected

        conn.close()

    def test_primary_key_uniqueness(self):
        """Test primary key uniqueness is enforced."""
        conn = sqlite3.connect(str(self.db_path))
        create_tables(conn)
        conn.commit()

        # Insert first customer
        conn.execute(
            "INSERT INTO customers (customer_id, name, email, signup_date, device_type, country) VALUES (1, 'User 1', 'user1@test.com', '2024-01-01', 'mobile', 'United States')"
        )
        conn.commit()

        # Try to insert duplicate customer_id (should fail)
        try:
            conn.execute(
                "INSERT INTO customers (customer_id, name, email, signup_date, device_type, country) VALUES (1, 'User 2', 'user2@test.com', '2024-01-01', 'mobile', 'United States')"
            )
            conn.commit()
            self.fail("Primary key constraint should have been violated")
        except sqlite3.IntegrityError:
            pass  # Expected

        conn.close()


if __name__ == "__main__":
    import unittest

    unittest.main()

