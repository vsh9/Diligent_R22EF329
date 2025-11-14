## Data Generation Architecture

The synthetic layer produces five CSV datasets (`customers`, `plans`, `content`, `subscriptions`, `usage_logs`) inside `data/raw/`. Each Python script is standalone yet orchestrated through shared behavioral rules and deterministic seeding. This section documents how the datasets link together and how the behavioral constraints shape the generated data.

### Components
1. **Entity Generators**
   - `generate_customers.py`, `generate_plans.py`, `generate_content.py`
   - Provide independent dimensions required by downstream relationship files.
2. **Relationship Generators**
   - `generate_subscriptions.py`, `generate_usage_logs.py`
   - Join facts across entities and inject behavioral realism (weekend boosts, plan weighting).
3. **Shared Utilities**
   - Faker locale `en_US`, common `random.Random` instance per file with fixed seed.
   - Helper functions: weighted sampling for content mix, weekend detection, completion rate math.

### Data Flow & Linkages
1. **Customers → Subscriptions**
   - Each customer record supplies `customer_id`, `signup_date`, and region/device metadata.
   - Subscriptions filter customers to those eligible for new plans (e.g., start date ≥ signup).
2. **Plans → Subscriptions**
   - Static plan catalog ensures consistent pricing and plan tiers.
   - Subscriptions randomly assign plan tiers while honoring upgrade/downgrade probabilities.
3. **Content → Usage Logs**
   - Content inventory provides duration and genre, which dictate watch duration bounds.
   - Usage logs reference `content_id` foreign keys and carry genre-derived session patterns.
4. **Subscriptions → Usage Logs**
   - Active subscriptions (end date null or in future) determine which customers can generate usage in the 60-day window.
   - Plan tier influences number of sessions and completion patterns.

### Behavioral Rules in Practice
- **Weekend Activity**: Usage generator multiplies session targets by 1.5 when sampling Saturdays/Sundays, creating clear peaks.
- **Plan-Based Weighting**: Premium subscribers receive higher target session counts, higher completion noise ceiling, and lower dropout risk; Basic gets fewer events.
- **Content Mix Enforcement**: Weighted random selection keeps the 50/30/20 split across movie/music/podcast genres, ensuring coverage for downstream analytics.
- **Duration + Completion**: For each usage row, `duration_watched` is sampled as 25–100% of content length (Premium skew ≥70%). Completion rate is computed as `(duration_watched / duration_minutes) ± noise`, clipped to [0.05, 1].
- **Temporal Guardrails**: Usage timestamps strictly fall within the prior 60 days with a recency bias (more events in last 14 days). Subscriptions respect start/end rules so lapsed users stop generating usage.

### Execution Order
1. `generate_customers.py`
2. `generate_plans.py`
3. `generate_content.py`
4. `generate_subscriptions.py`
5. `generate_usage_logs.py`

This order satisfies foreign-key dependencies and ensures each behavioral rule has upstream context (e.g., plan tier, content duration).

### Logging & Outputs
- Each script logs: total rows written, sample category distributions (e.g., plan counts, genre mix), temporal coverage stats, and target file path.
- CSVs overwrite existing files; scripts exit non-zero if dependencies are missing to prevent partial states.

### Future Integration
- Ingestion layer reads these CSVs, loads staging tables in SQLite, and triggers validation tests recorded in `implementation/validation`.
- Analytics layer will leverage the generated data to compute top content and engagement metrics, while governance checks ensure the behaviors defined here remain intact over time.

## Analytics Execution Layer

The analytics phase materializes SQL views inside `ecommerce.db` and exports curated reports for downstream stakeholders.

- **View Compilation Flow**  
  - `implementation/analytics/run_analytics.py` reads the canonical SQL definitions stored in `implementation/analytics/views/*.sql`.  
  - For each view (`top_content_view`, `engagement_view`) the script drops any existing version, executes the SQL text verbatim, and re-creates the view inside SQLite to guarantee parity with version-controlled definitions.

- **Database Interaction**  
  - The script connects to `ecommerce.db` with foreign keys enforced, ensuring views can join against the latest ingested tables (`usage_logs`, `content`, `customers`).  
  - After compilation, it immediately queries each view to verify row counts, log execution metadata, and capture preview samples.

- **Outputs & Schemas**  
  - Query results are exported to `data/processed/top_content_report.csv` (columns: `content_id`, `title`, `genre`, `total_watch_hours`, `unique_viewers`, `avg_completion_rate`) and `data/processed/engagement_report.csv` (columns: `customer_id`, `name`, `avg_watch_minutes_per_session`, `avg_completion_rate`, `total_sessions`).  
  - Execution activity, including timestamps, SQL file sources, and row counts, is recorded in `logs/analytics.log` for auditability.
