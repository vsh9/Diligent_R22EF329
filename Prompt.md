# Prompts Used in Agentic SDLC for Subscription-Based Digital Store

This document showcases the sequence of AI prompts used to build the project through the Agentic SDLC methodology. Each prompt is presented with its title, full text (reconstructed for reproducibility), and a summary of the generated output. This transparency enables stakeholders to recreate the development process, ensuring governance, traceability, and educational value for demonstrating AI-assisted engineering.

The prompts follow the SDLC phases: Requirements, Design, Implementation, Testing, and Packaging. They were executed in Cursor, with outputs versioned in the repository.

*The prompts were improved and curated using cursor to ensure a detailed execution of the project before generating code.*

## Step 1: Requirements Elicitation and System Design Architecture

**Prompt Title**: Define Synthetic Data Schemas, Behavioral Rules for Subscription Analytics Pipeline along with Architect Data Flow and Linkages for Synthetic Pipeline

**Full Prompt**:
"You are an AI engineering agent following the Agentic SDLC.

Context:
We are building a subscription-based digital store (similar to Netflix) analytics pipeline.

High-level requirements:
- Generate synthetic datasets for: customers, plans, content, subscriptions, usage logs.
- Ingest all files into SQLite with audit logging and validation.
- Create analytical SQL views for: top content, engagement metrics.
- Add governance+data validation layer.
- Automate entire pipeline with a shell script.
- Push final project to GitHub.

Your task:
1. Create a complete folder structure for this project.
2. Prepare empty file stubs for every script, SQL, and validation.
3. Follow Agentic SDLC: requirements->design->implementation->testing->packaging.

Deliver:
- Folder structure
- Empty files created
- Next recommended implementation step
"

## Step 2: Data Generation Implementation

**Prompt Title**: Implement Data Generation Scripts

**Full Prompt**:
"Update the project according to the Agentic SDLC next step.

Task:
Populate the following files under implementation/data_generation/ with full working code:
- generate_customers.py
- generate_plans.py
- generate_content.py
- generate_subscriptions.py
- generate_usage_logs.py

Before coding:
1. Update requirements/requirements.md with the exact dataset specifications.
2. Update design/system_design.md with the data generation architecture and flow:
   - How each dataset links (FK relationships)
   - How behavioral rules influence synthetic data

Dataset Specifications to include+implement:

1. customers.csv
   Fields:
   - customer_id (int)
   - name
   - email
   - signup_date
   - device_type (mobile/desktop/tablet/TV)
   - country

2. plans.csv
   Fields:
   - plan_id (int)
   - name (Basic/Standard/Premium)
   - price

3. content.csv
   Fields:
   - content_id (int)
   - title
   - genre
   - duration_minutes

4. subscriptions.csv
   Fields:
   - subscription_id
   - customer_id (FK)
   - plan_id (FK)
   - start_date
   - end_date
   - auto_renew (True/False)

5. usage_logs.csv
   Fields:
   - usage_id
   - customer_id (FK)
   - content_id (FK)
   - timestamp
   - duration_watched
   - completion_rate

Behavioral Rules:
- Weekends have higher watch activity
- Premium users consume more content
- Duration watched must never exceed content.duration_minutes
- Completion rate must be realistic (duration_watched / duration_minutes)
- Timestamp should be within last 60 days
- Content mix includes: movies, music, podcasts

Implementation Requirements:
- Use Faker + random
- Write all generated CSVs into data/raw/
- Ensure reproducibility
- Each Python generator file must be a standalone script
- Print generation statistics to console

Deliver:
Fully implemented generation scripts+updated requirements.md+updated system_design.md.
After generating all data, recommend the next SDLC step."


## Step 3: Validation Logic and Code generation

**Prompt Title**: Build Data Validation

**Full Prompt**:
"Implement validate_data.py inside /validation/.

Validation requirements:
1. Schema validation:
   - correct columns exist
   - correct datatypes for numeric/date/time fields

2. Referential integrity:
   - usage_logs.customer_id exists in customers.csv
   - usage_logs.content_id exists in content.csv

3. Logical rules:
   - duration_watched <= content.duration_minutes
   - completion_rate between 0 and 1
   - subscription start_date <= end_date

4. Log results:
   - Write detailed validation logs to /logs/validation.log
   - Any row failing validation should be logged and skipped

Deliver:
A working validate_data.py with robust logging and row-level reporting.
"

## Step 4: SQL Ingestion Logic and Code Generation

**Prompt Title**: Build SQLite Ingestion

**Full Prompt**:
"Implement load_db.py.

Requirements:
- Create SQLite DB: ecommerce.db
- Load all CSVs into tables:
  customers, plans, content, subscriptions, usage_logs
- Enforce realistic schema:
  primary keys
  foreign keys
- Log ingestion audit to /logs/ingestion.log:
  - row counts
  - load timestamp
  - tables replaced or created

Deliver:
A full ingestion pipeline with schema creation + loading + logging.
"

## Step 5: Analytics Views and Export

**Prompt Title**: Develop SQL Views and Analytics Orchestration

**Full Prompt**:
"Create SQL view files in /sql/:

1. top_content_view.sql
   Query:
   - total watch hours per content
   - number of viewers
   - average completion_rate
   - order by total watch hours desc

2. engagement_view.sql
   Query:
   - average watch time per customer
   - average completion rate
   - total sessions per customer

Deliver:
Fully implemented SQL views compatible with SQLite.
"

## Step 6: Analytics Running Script

**Prompt Title**: Generate Comprehensive Analytics script

**Full Prompt**:
"Proceed to the next Agentic SDLC step.

Goal:
Integrate the newly created SQL views into a runnable analytics pipeline.

Update by creating a new script run_analytics.py

Requirements for run_analytics.py:

1. Connect to ecommerce.db.

2. Automatically execute the SQL view definitions

   Execution rules:
   - If the view already exists, replace it.
   - Apply the SQL exactly as written in the .sql files.
   - Store compiled views in the SQLite DB for downstream querying.

3. Query both views and export results as CSV into:

       top_content_report.csv
       engagement_report.csv

4. Console output:
   - Total records in each view
   - Example top 5 rows from each report

5. Logging:
   - Write a new log file under logs/analytics.log
   - Include timestamps, query execution status, row counts, and any errors.

6. Architecture documentation:
   - Update design/system_design.md with a section describing:
     "Analytics Execution Layer"
     - View compilation flow
     - How run_analytics.py interacts with ecommerce.db
     - Output paths and sample schemas

7. Final action:
   - After running analytics, print summary:
       "Analytics execution completed successfully. Reports available in data/processed/"

Deliver:
- Completed run_analytics.py
- Updated design/system_design.md with Analytics Execution Layer section
- Generated output CSVs in data/processed/
- Log file at logs/analytics.log

After this step, recommend the next SDLC action automatically.
"

## Step 7: Testing Implementation

**Prompt Title**: Implement Unit Tests for Pipeline Components

**Full Prompt**:
"Proceed to the next Agentic SDLC step: Testing.

Proceed to the Testing phase.

1. Create basic pytest tests for data generation,ingestion and validation. 
   Each test file should only check core functionality: schemas, row counts, 
   FK integrity, and that logs are created.

2. Add a simple test runner that executes all tests and writes results to logs/testing.log.

3. Update design/system_design.md describing unit tests.

After completing, recommend the next Agentic SDLC step: Packaging."

## Step 8: Automate Full Agentic SDLC Pipeline

**Prompt Title**: Orchestrate Full Pipeline Automation

**Full Prompt**:
"Proceed to the next Agentic SDLC step.

Task:
Implement a complete automation script

This script must orchestrate the full data lifecycle:
data generation->validation->ingestion->analytics.

Pipeline Requirements:

1. Make the script executable with correct

2. Logging:
   - Create /logs/pipeline.log if not present
   - Each phase should append a timestamped entry
   - If any phase fails, write an error log and exit immediately

3. Execution Phases (in order):

   **PHASE 1: DATA GENERATION**
   Call all generator scripts,Output should go to data/raw/

   **PHASE 2: VALIDATION**
   Run data validation if validation fails, pipeline stops.

   **PHASE 3: INGESTION**
   Run SQLite ingestion log operations into ingestion.log

   **PHASE 4: ANALYTICS**
   Should execute SQL views+export results to data/processed/
   Log operations into analytics.log

4. Documentation Update:
   Append a new section to packaging/deployment_plan.md:
   “Automated Agentic SDLC Pipeline”
   - Describe each phase
   - Expected outputs
   - How logs help with governance and traceability

5. Deliver:
   - Fully implemented run_pipeline.sh
   - Updated deployment_plan.md
   - All phases tested successfully
   - Final summary message printed

After completing the script, recommend the next SDLC step automatically.
"

This prompt catalog demonstrates the agentic approach: structured, iterative, and governed. To reproduce, copy-paste prompts into Cursor/AI tools, adjusting paths as needed.
