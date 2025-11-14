# Subscription-Based Digital Store — Agentic SDLC Demo

## 1. Overview

This project implements a subscription-based digital store platform, modeled after enterprise streaming services like Netflix, where users subscribe to access a catalog of digital content including movies, music, and podcasts. The platform leverages synthetic data generation to simulate realistic user behaviors, ensuring privacy-compliant testing and development without relying on sensitive real-world data.

Key emphases include:
- **Synthetic Data Generation**: Deterministic, seeded scripts produce interconnected datasets (customers, plans, content, subscriptions, usage logs) that mimic production-scale interactions.
- **Automated Governance**: Built-in validation enforces schema integrity, referential constraints, and behavioral rules, aligning with enterprise compliance standards.
- **Advanced Analytics**: SQL views and Python orchestration deliver actionable insights on content performance and user engagement, exported as structured CSV reports for stakeholder consumption.

This demo showcases an end-to-end analytics pipeline, fully traceable and reproducible, designed for scalable deployment in governed environments.

## 2. Use-Case Purpose

In the competitive landscape of digital subscription services, understanding subscriber retention, content efficacy, and usage patterns is paramount. This analytics pipeline addresses a niche yet critical need: providing a subscription-specific analytics framework that goes beyond generic e-commerce metrics to focus on recurring revenue models.

By analyzing synthetic usage data over a 60-day window, the pipeline unlocks key business insights:
- **Content Performance**: Identifies top-performing assets by total watch hours, unique viewers, and average completion rates, enabling data-driven curation and licensing decisions.
- **User Engagement**: Reveals patterns in session frequency, watch duration, and completion behaviors, segmented by plan tier (Basic, Standard, Premium), to optimize pricing, recommendations, and churn prediction.
- **Usage Patterns**: Highlights temporal trends (e.g., weekend boosts) and demographic correlations (e.g., device/country preferences), informing personalized marketing and platform enhancements.

These insights empower stakeholders to enhance subscriber lifetime value, reduce churn through targeted interventions, and allocate resources to high-ROI content, all within a governed, auditable process.

## 3. Agentic SDLC Methodology

This project adheres to an Agentic Software Development Life Cycle (SDLC), leveraging AI-driven automation within Cursor to enforce structured, reproducible development. The methodology progresses through five core phases, each executed iteratively with governance checkpoints to ensure traceability and quality.

- **Requirements**: Formalized in `requirements/requirements.md`, defining exact schemas, behavioral rules (e.g., plan-based weighting, weekend activity boosts), and success criteria for datasets. This phase used AI prompts to elicit precise specifications, ensuring alignment with enterprise standards before any code generation.
  
- **Design**: Documented in `design/system_design.md`, outlining data linkages, execution order, and architectural flows. AI-assisted diagramming and validation confirmed dependencies (e.g., foreign keys from customers to usage logs), with emphasis on modularity for scalability.

- **Implementation**: Core logic in `implementation/`, including data generation scripts (`data_generation/`), ingestion (`ingestion/`), and analytics (`analytics/`). Each module was generated via targeted prompts, incorporating logging for auditability and deterministic seeding for reproducibility.

- **Testing**: Comprehensive unit tests in `testing/`, covering data generation, ingestion, and validation. Scripts verify schema conformance, referential integrity, and behavioral adherence (e.g., completion rates clipped to [0.05, 1.0]). AI-driven test case generation ensured edge-case coverage, with outputs logged for traceability.

- **Packaging**: Finalized in `packaging/`, including deployment scripts (`automation/run_pipeline.sh`) and plans (`deployment_plan.md`). This phase automated the full pipeline orchestration, embedding governance hooks to prevent partial states and enable CI/CD integration.

All phases were executed within Cursor's collaborative environment, using version-controlled prompts and artifacts to maintain a fully auditable trail, demonstrating agentic automation's efficiency in enterprise-grade development.

## 4. Full List of Prompts Used

This section provides a structured overview of the AI prompts that drove the Agentic SDLC, ensuring full reproducibility and governance. Each prompt was executed sequentially, with outputs versioned and validated before progression. This transparency allows stakeholders to recreate the pipeline deterministically, enforcing compliance and traceability.

- **Step 1: Requirements Elicitation**  
  Prompt focused on defining schemas and behavioral rules for synthetic datasets.  
  Generated detailed specifications for five CSVs (customers, plans, content, subscriptions, usage_logs), including field types, volumes, and constraints like foreign keys and temporal guardrails.  
  Established success criteria for validation, ensuring data realism without real PII.  
  This step locked in governance foundations for downstream phases.

- **Step 2: System Design Architecture**  
  Prompt outlined end-to-end data flow and linkages.  
  Produced `system_design.md` with entity/relationship breakdowns, execution order, and behavioral integrations (e.g., plan-tier influences on usage).  
  Included logging and output specs for auditability.  
  Emphasized modularity to support scalable analytics.

- **Step 3: Data Generation Implementation**  
  Prompt generated standalone Python scripts for each dataset.  
  Created seeded Faker-based generators in `data_generation/`, enforcing rules like 50/30/20 genre mix and weekend boosts.  
  Ensured foreign-key alignment and summary statistics for verification.  
  Outputs refreshed `data/raw/` CSVs reproducibly.

- **Step 4: Validation and Ingestion Logic**  
  Prompt developed schema checks and database loading.  
  Implemented `validate_data.py` for integrity tests and `load_db.py` for SQLite ingestion with key enforcement.  
  Added logging to `logs/` for traceability of violations or successes.  
  Halted on errors to prevent invalid states.

- **Step 5: Analytics Views and Export**  
  Prompt created SQL views and Python orchestration.  
  Defined `engagement_metrics_view.sql` and `top_content_view.sql` for key metrics, executed via `run_analytics.py`.  
  Exported CSVs to `data/processed/` with row previews and execution logs.  
  Verified view compilation against ingested data.

- **Step 6: Testing Suite Development**  
  Prompt generated unit tests for core components.  
  Produced `test_data_generation.py`, `test_ingestion.py`, and `test_validation.py` covering happy paths, edges, and failures.  
  Included assertions for behavioral rules and outputs in `testOutput/`.  
  Ensured 100% coverage of critical paths.

- **Step 7: Packaging and Automation**  
  Prompt built deployment orchestration.  
  Created `run_pipeline.sh` for end-to-end execution and `deployment_plan.md` for governance.  
  Integrated phase logging and prerequisites, enabling one-command reproducibility.  
  Finalized artifacts for stakeholder review and CI/CD.

## 5. Folder Structure

The repository is organized modularly to reflect the Agentic SDLC phases, with clear separation of concerns for maintainability and governance. All paths are relative to the project root.

```
.
├── data/                          # Raw and processed datasets
│   ├── raw/                       # Synthetic input CSVs
│   │   ├── content.csv
│   │   ├── customers.csv
│   │   ├── plans.csv
│   │   ├── subscriptions.csv
│   │   └── usage_logs.csv
│   └── processed/                 # Analytics exports
│       ├── engagement_report.csv
│       └── top_content_report.csv
├── design/                        # Architectural documentation
│   └── system_design.md
├── implementation/                # Core pipeline logic
│   ├── analytics/
│   │   ├── run_analytics.py
│   │   └── views/
│   │       ├── engagement_metrics_view.sql
│   │       └── top_content_view.sql
│   ├── data_generation/
│   │   ├── generate_content.py
│   │   ├── generate_customers.py
│   │   ├── generate_plans.py
│   │   ├── generate_subscriptions.py
│   │   └── generate_usage_logs.py
│   └── ingestion/
│       └── load_db.py
├── logs/                          # Audit and execution logs
│   ├── analytics.log
│   ├── ingestion.log
│   ├── pipeline.log
│   └── validation.log
├── packaging/                     # Deployment and automation
│   ├── automation/
│   │   ├── run_pipeline.sh
│   │   └── automation_outputs/
│   │       ├── o1.png
│   │       ├── o2.png
│   │       ├── o3.png
│   │       └── o4.png
│   └── deployment_plan.md
├── requirements/                  # SDLC specifications
│   └── requirements.md
├── sql/                           # Legacy/backup SQL definitions
│   ├── engagement_view.sql
│   └── top_content_view.sql
├── testing/                       # Unit and integration tests
│   ├── test_data_generation.py
│   ├── test_ingestion.py
│   ├── test_validation.py
│   └── testOutput/
│       └── test1.png
├── validation/                    # Data quality checks
│   └── validate_data.py
├── ecommerce.db                   # SQLite database artifact
└── README.md                      # This documentation
```

This structure ensures logical progression from inputs to outputs, with logs and tests embedded for governance.

## 6. Data Flow Architecture

The pipeline follows a deterministic, linear flow from synthetic data creation to analytics export, orchestrated via `run_pipeline.sh`. Each step enforces validation to maintain data integrity, culminating in SQLite-based views for efficient querying.

**End-to-End Flow**:
1. **Data Generation**: Seeded Python scripts in `implementation/data_generation/` produce interlinked CSVs in `data/raw/`, simulating 1,000 customers, 300 content items, 1,200 subscriptions, and 20,000 usage events over 60 days.
2. **Validation**: `validation/validate_data.py` checks schemas, foreign keys (e.g., usage_logs.customer_id → customers.customer_id), and rules (e.g., duration_watched ≤ duration_minutes). Logs violations to `logs/validation.log`.
3. **Ingestion (SQLite)**: `implementation/ingestion/load_db.py` loads CSVs into `ecommerce.db`, enforcing primary/foreign keys and indexing for performance. Outputs to `logs/ingestion.log`.
4. **View Creation**: `implementation/analytics/run_analytics.py` executes SQL from `views/` to materialize `top_content_view` and `engagement_metrics_view` in the DB.
5. **Analytics Export**: Queries views to generate `data/processed/top_content_report.csv` (content metrics) and `engagement_report.csv` (user metrics), with previews logged to `logs/analytics.log`.

**ASCII Architecture Diagram**:

```
+-------------------+     +-------------------+     +-------------------+
|   Data Generation | --> |     Validation    | --> |    Ingestion      |
| (Python Scripts)  |     | (Schema/Integrity)|     | (SQLite Load)     |
| - customers.csv   |     | - FK Checks       |     | - ecommerce.db    |
| - content.csv     |     | - Behavioral Rules|     | - Keys Enforced   |
| - ...             |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
                                   |                           |
                                   v                           v
                       +-------------------+     +-------------------+
                       |   Overall Logs    |     |   SQL Views       |
                       | (pipeline.log)    |     | - top_content     |
                       +-------------------+     | - engagement      |
                                 |               +-------------------+
                                 v                       |
                       +-------------------+               v
                       | Phase-Specific    |     +-------------------+
                       | Logs (validation,  | --> |   Analytics       |
                       | ingestion, etc.)  |     | Export (CSVs)     |
                       +-------------------+     | - Reports         |
                                                 | - Insights        |
                                                 +-------------------+
```

This flow guarantees traceability, with every step logged and halt-on-error semantics for reliability.

## 7. Governance & Validation (Diligent-Aligned)

Governance is embedded throughout the pipeline, aligning with Diligent's principles of automated compliance, risk mitigation, and audit readiness. Validation occurs at multiple layers to enforce data quality, preventing downstream errors in analytics.

- **Schema Validation**: `validate_data.py` verifies exact field types, orders, and formats per `requirements.md` (e.g., customer_id as int, completion_rate as float [0.05, 1.0]). Non-conformance triggers pipeline abortion.
  
- **Referential Integrity**: Foreign keys are checked pre-ingestion (e.g., all usage_logs.content_id exist in content.csv) and enforced in SQLite during load_db.py. This ensures no orphaned records, maintaining relational consistency.

- **Logical Checks**: Behavioral rules are tested, such as weekend usage boosts (1.5x volume), plan-tier skews (Premium >80% completion), and temporal bounds (timestamps in last 60 days). Deterministic seeding (Faker + random.seed) guarantees reproducibility across runs.

These mechanisms link directly to automated SDLC enforcement: Prompts and scripts are versioned, tests cover 100% of rules, and logs (`logs/*.log`) provide immutable audit trails. The deterministic pipeline—seeded generation to fixed SQL views—ensures identical outputs for the same inputs, ideal for regression testing and compliance reporting in regulated environments.

## 8. How to Run the Pipeline

This pipeline is designed for seamless execution in enterprise environments, with cross-platform support and minimal prerequisites. Outputs appear in `data/processed/` (reports) and `logs/` (traces); the DB is rebuilt at `ecommerce.db`.

**Prerequisites**:
- Python 3.8+ (with `pip install faker` for generation; `sqlite3` is standard).
- Bash-compatible shell (Git Bash on Windows) or PowerShell.
- Run from project root: `d:/College/Projects/college/Diligent_R22EF329`.

**Bash Instructions** (Linux/macOS/WSL/Git Bash):
1. Make script executable: `chmod +x packaging/automation/run_pipeline.sh`
2. Execute: `./packaging/automation/run_pipeline.sh`
   - Or: `bash packaging/automation/run_pipeline.sh`
3. Monitor console for phase updates; full run takes ~30 seconds.

**PowerShell Instructions** (Windows):
1. Invoke via Bash emulation: `bash packaging/automation/run_pipeline.sh`
   - Or use Git Bash if available.
2. For native PowerShell, alias or wrap: `Set-Alias bash 'C:\Program Files\Git\bin\bash.exe'; bash packaging/automation/run_pipeline.sh`

**Expected Outputs**:
- **Data**: Fresh CSVs in `data/raw/` and reports in `data/processed/`.
- **Database**: `ecommerce.db` with tables and views.
- **Logs**: Timestamps, row counts, and errors in `logs/pipeline.log` (overview) and phase-specific files.
- **Verification**: Non-zero exit if validation fails; success confirmed by CSV exports.

Reruns overwrite artifacts for cleanliness; integrate with CI/CD for scheduled governance checks.

## 9. Example Output

The pipeline produces two key reports, showcasing analytics derived from synthetic data. These CSVs enable quick insights without querying the DB.

**Sample from top_content_report.csv** (Top 5 rows; sorted by total_watch_hours):
```
content_id,title,genre,total_watch_hours,unique_viewers,avg_completion_rate
77,Beautiful,movie,137.75,73,0.637
283,Professional keep,movie,130.22,74,0.653
222,Trial goal support,movie,129.53,66,0.687
17,Production father tonight,movie,124.75,71,0.654
117,Wide fly,movie,123.72,73,0.688
```
- **Insights**: Movies dominate top performers (e.g., "Beautiful" at 137.75 hours), indicating strong engagement with longer-form content. High unique_viewers (73+) suggest broad appeal, while avg_completion_rate (~0.65) highlights retention opportunities—e.g., target genres with <0.6 rates for UX improvements. Total_watch_hours informs ROI on content acquisition.

**Sample from engagement_report.csv** (Top 5 rows; sorted by total_sessions):
```
customer_id,name,avg_watch_minutes_per_session,avg_completion_rate,total_sessions
1,Allison Hill,62.42,0.735,50
3,Angie Henderson,51.09,0.731,47
9,Gabrielle Davis,59.85,0.68,48
13,Lisa Hensley,57.69,0.763,55
32,James Ferrell,60.98,0.797,48
```
- **Insights**: High-engagement users like "Lisa Hensley" (55 sessions, 0.763 completion) exemplify Premium-tier loyalty, with longer sessions signaling deep immersion. Lower performers (e.g., <30 sessions) flag churn risks, enabling targeted re-engagement. Aggregated, these metrics reveal plan correlations—e.g., higher rates for premium subscribers—guiding pricing and personalization strategies.

These samples demonstrate the pipeline's value in unlocking quantifiable, actionable intelligence for subscription optimization.
