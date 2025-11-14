"""Validate generated CSV datasets for schema, referential, and logical rules."""
from __future__ import annotations

import csv
import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "validation.log"

DatasetRows = List[dict]
Parser = Callable[[str], object]


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


def parse_int(value: str) -> int:
    return int(value)


def parse_float(value: str) -> float:
    return float(value)


def parse_date(value: str) -> date:
    if not value:
        raise ValueError("expected date, received empty string")
    return datetime.fromisoformat(value).date()


def parse_optional_date(value: str) -> Optional[date]:
    return None if not value else parse_date(value)


def parse_datetime(value: str) -> datetime:
    if not value:
        raise ValueError("expected datetime, received empty string")
    return datetime.fromisoformat(value)


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"invalid boolean literal: {value}")


SCHEMA_CONFIG = {
    "customers": {
        "path": RAW_DIR / "customers.csv",
        "columns": [
            "customer_id",
            "name",
            "email",
            "signup_date",
            "device_type",
            "country",
        ],
        "parsers": {
            "customer_id": parse_int,
            "signup_date": parse_date,
        },
    },
    "plans": {
        "path": RAW_DIR / "plans.csv",
        "columns": ["plan_id", "name", "price"],
        "parsers": {
            "plan_id": parse_int,
            "price": parse_float,
        },
    },
    "content": {
        "path": RAW_DIR / "content.csv",
        "columns": ["content_id", "title", "genre", "duration_minutes"],
        "parsers": {
            "content_id": parse_int,
            "duration_minutes": parse_int,
        },
    },
    "subscriptions": {
        "path": RAW_DIR / "subscriptions.csv",
        "columns": [
            "subscription_id",
            "customer_id",
            "plan_id",
            "start_date",
            "end_date",
            "auto_renew",
        ],
        "parsers": {
            "subscription_id": parse_int,
            "customer_id": parse_int,
            "plan_id": parse_int,
            "start_date": parse_date,
            "end_date": parse_optional_date,
            "auto_renew": parse_bool,
        },
    },
    "usage_logs": {
        "path": RAW_DIR / "usage_logs.csv",
        "columns": [
            "usage_id",
            "customer_id",
            "content_id",
            "timestamp",
            "duration_watched",
            "completion_rate",
        ],
        "parsers": {
            "usage_id": parse_int,
            "customer_id": parse_int,
            "content_id": parse_int,
            "timestamp": parse_datetime,
            "duration_watched": parse_int,
            "completion_rate": parse_float,
        },
    },
}


def log_row_error(dataset: str, line_number: int, message: str) -> None:
    logging.error("%s | %s | line=%d | %s", utc_now(), dataset, line_number, message)


def load_and_validate_schema(dataset: str) -> Tuple[DatasetRows, int]:
    config = SCHEMA_CONFIG[dataset]
    path: Path = config["path"]
    if not path.exists():
        raise FileNotFoundError(f"Required dataset missing: {dataset} -> {path}")

    with path.open("r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        expected_columns = config["columns"]
        if reader.fieldnames is None:
            raise ValueError(f"{dataset} has no header row")
        if reader.fieldnames != expected_columns:
            raise ValueError(
                f"{dataset} column mismatch. expected={expected_columns} got={reader.fieldnames}"
            )

        parsers: Dict[str, Parser] = config["parsers"]
        valid_rows: DatasetRows = []
        invalid_count = 0

        for line_number, row in enumerate(reader, start=2):
            row_valid = True
            typed_row = {}
            for col in expected_columns:
                value = row[col]
                parser = parsers.get(col)
                if parser:
                    try:
                        typed_row[col] = parser(value)
                    except Exception as exc:  # pylint: disable=broad-except
                        row_valid = False
                        invalid_count += 1
                        log_row_error(dataset, line_number, f"{col}: {exc}")
                        break
                else:
                    typed_row[col] = value
            if row_valid:
                typed_row["_line"] = line_number
                valid_rows.append(typed_row)

    logging.info(
        "%s | %s | schema validation complete | valid=%d | invalid=%d",
        utc_now(),
        dataset,
        len(valid_rows),
        invalid_count,
    )
    return valid_rows, invalid_count


def validate_subscriptions_logic(rows: DatasetRows) -> Tuple[DatasetRows, int]:
    valid: DatasetRows = []
    invalid = 0
    for row in rows:
        start_date = row["start_date"]
        end_date = row["end_date"]
        if end_date and start_date > end_date:
            invalid += 1
            log_row_error(
                "subscriptions",
                row["_line"],
                f"start_date {start_date} after end_date {end_date}",
            )
            continue
        valid.append(row)
    logging.info(
        "%s | subscriptions | logical validation complete | valid=%d | invalid=%d",
        utc_now(),
        len(valid),
        invalid,
    )
    return valid, invalid


def validate_usage_rules(
    rows: DatasetRows,
    customer_ids: set[int],
    content_duration: Dict[int, int],
) -> Tuple[DatasetRows, int]:
    valid: DatasetRows = []
    invalid = 0
    for row in rows:
        errors: List[str] = []
        if row["customer_id"] not in customer_ids:
            errors.append(f"unknown customer_id {row['customer_id']}")
        duration = content_duration.get(row["content_id"])
        if duration is None:
            errors.append(f"unknown content_id {row['content_id']}")
        else:
            if row["duration_watched"] > duration:
                errors.append(
                    f"duration_watched {row['duration_watched']} exceeds content duration {duration}"
                )
        if not 0 <= row["completion_rate"] <= 1:
            errors.append(
                f"completion_rate {row['completion_rate']} outside 0-1 range"
            )

        if errors:
            invalid += 1
            for err in errors:
                log_row_error("usage_logs", row["_line"], err)
            continue
        valid.append(row)

    logging.info(
        "%s | usage_logs | referential/logical validation complete | valid=%d | invalid=%d",
        utc_now(),
        len(valid),
        invalid,
    )
    return valid, invalid


def run_validations() -> None:
    summary: Dict[str, Dict[str, int]] = {}

    customers, cust_invalid = load_and_validate_schema("customers")
    summary["customers"] = {"valid": len(customers), "invalid": cust_invalid}

    plans, plans_invalid = load_and_validate_schema("plans")
    summary["plans"] = {"valid": len(plans), "invalid": plans_invalid}

    content, content_invalid = load_and_validate_schema("content")
    summary["content"] = {"valid": len(content), "invalid": content_invalid}

    subscriptions, subs_invalid = load_and_validate_schema("subscriptions")
    subscriptions, subs_logic_invalid = validate_subscriptions_logic(subscriptions)
    summary["subscriptions"] = {
        "valid": len(subscriptions),
        "invalid": subs_invalid + subs_logic_invalid,
    }

    usage_logs, usage_invalid = load_and_validate_schema("usage_logs")

    customer_ids = {row["customer_id"] for row in customers}
    content_duration = {row["content_id"]: row["duration_minutes"] for row in content}

    usage_logs, usage_logic_invalid = validate_usage_rules(
        usage_logs, customer_ids, content_duration
    )
    summary["usage_logs"] = {
        "valid": len(usage_logs),
        "invalid": usage_invalid + usage_logic_invalid,
    }

    logging.info("%s | validation summary", utc_now())
    for dataset, stats in summary.items():
        logging.info(
            "%s | %s | valid=%d | invalid=%d",
            utc_now(),
            dataset,
            stats["valid"],
            stats["invalid"],
        )


def main() -> None:
    init_logging()
    logging.info("%s | validation run started", utc_now())
    run_validations()
    logging.info("%s | validation run completed", utc_now())


if __name__ == "__main__":
    main()

