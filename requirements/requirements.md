## Requirements Overview

We are building a subscription-based digital store analytics pipeline (Netflix-style). The Agentic SDLC mandates explicit dataset specifications before implementation. This document formalizes the exact schemas, behavioral rules, and success metrics for the synthetic generators that feed the downstream ingestion, validation, analytics, and governance layers.

## Dataset Specifications

General rules shared across datasets:
- All scripts write CSV outputs into `data/raw/`.
- Faker + Python `random` are the only generators; both must be seeded for reproducibility.
- Each script runs standalone and prints summary statistics (row counts, distribution hints).

### customers.csv
| Field | Type | Notes |
| --- | --- | --- |
| `customer_id` | int | Sequential primary key starting at 1 |
| `name` | string | Faker full name |
| `email` | string | Unique Faker email |
| `signup_date` | date | ISO format, within past 24 months |
| `device_type` | enum | {mobile, tablet, desktop, smart_tv} |
| `country` | enum | {United States, Canada, United Kingdom, Australia, India} |

Target volume: 1,000 rows.

### plans.csv
| Field | Type | Notes |
| --- | --- | --- |
| `plan_id` | int | 1..3 |
| `name` | enum | {Basic, Standard, Premium} |
| `price` | decimal | {8.99, 13.99, 18.99} USD |

Volume fixed at 3 (one per plan).

### content.csv
| Field | Type | Notes |
| --- | --- | --- |
| `content_id` | int | Sequential primary key |
| `title` | string | Faker sentence (strip trailing period) |
| `genre` | enum | {movie, music, podcast} with 50/30/20 mix |
| `duration_minutes` | int | Range depends on genre (movies 80–160, music 3–8, podcasts 15–90) |

Target volume: 300 rows.

### subscriptions.csv
| Field | Type | Notes |
| --- | --- | --- |
| `subscription_id` | int | Sequential primary key |
| `customer_id` | int | FK referencing `customers.customer_id` |
| `plan_id` | int | FK referencing `plans.plan_id` |
| `start_date` | date | ≥ `signup_date`, within last 18 months |
| `end_date` | date or empty | ≥ `start_date`; 40% of subscriptions end within 12 months, remainder active (empty end_date) |
| `auto_renew` | bool | 70% True |

Target volume: 1,200 rows with multiple subscriptions per customer to mimic upgrades/downgrades.

### usage_logs.csv
| Field | Type | Notes |
| --- | --- | --- |
| `usage_id` | int | Sequential primary key |
| `customer_id` | int | FK referencing `customers.customer_id` |
| `content_id` | int | FK referencing `content.content_id` |
| `timestamp` | datetime | Within last 60 days, ISO 8601 |
| `duration_watched` | int | 25–100% of `content.duration_minutes`, never exceeding it |
| `completion_rate` | float | `duration_watched / duration_minutes` plus noise, clipped to [0.05, 1.0] |

Target volume: 20,000 rows, driven by behavioral rules below.

## Behavioral Rules
- **Weekend boost**: Saturday/Sunday usage volume increased 1.5×.
- **Plan influence**: Premium > Standard > Basic for number of sessions and completion rate.
- **Duration guardrail**: `duration_watched ≤ duration_minutes`, skewed higher for Premium viewers.
- **Completion realism**: Derived from duration ratio with ±10% noise, clipped between 0.05 and 1.0.
- **Content mix**: Samples maintain ~50% movies, 30% music, 20% podcasts to ensure coverage.
- **Recent activity**: All usage timestamps fall inside the past 60 days; customer with no subscription activity can have zero usage rows.

## Constraints & Assumptions
- Deterministic seeds per script (documented inside each generator).
- CSVs overwrite previous runs to keep the working directory clean.
- Scripts fail fast if dependencies (upstream CSVs) are missing.

## Success Criteria
- CSVs conform exactly to the schemas above (field names, order, data types).
- Foreign keys always align with existing records.
- Console statistics confirm behavioral rules (weekend share, plan-based usage, etc.).
- Outputs remain ready for ingestion + validation steps in the Agentic SDLC pipeline.
