## Deployment Plan

### Automated Agentic SDLC Pipeline

The `packaging/automation/run_pipeline.sh` script orchestrates the complete lifecycle end-to-end. Each phase emits console updates and appends structured logs to `logs/pipeline.log` for governance.

**Execution Requirements:**
- Bash shell (Git Bash, WSL, or Linux/macOS)
- Python 3.x with required packages (faker, sqlite3)
- Script is executable: `chmod +x packaging/automation/run_pipeline.sh`
- Run from project root: `./packaging/automation/run_pipeline.sh` or `bash packaging/automation/run_pipeline.sh`

1. **Phase 1 – Data Generation**  
   - Runs all generators under `implementation/data_generation/`.  
   - Outputs refreshed CSVs in `data/raw/`.  
   - Individual scripts also write their own statistics to stdout.

2. **Phase 2 – Validation**  
   - Executes `validation/validate_data.py`.  
   - Confirms schema, referential integrity, and logical rules against the raw CSVs.  
   - Findings recorded in `logs/validation.log`; pipeline halts if violations occur.

3. **Phase 3 – Ingestion**  
   - Calls `implementation/ingestion/load_db.py`.  
   - Rebuilds `ecommerce.db`, enforcing primary/foreign keys and logging to `logs/ingestion.log`.

4. **Phase 4 – Analytics**  
   - Runs `implementation/analytics/run_analytics.py`.  
   - Compiles the SQL views, exports `data/processed/top_content_report.csv` and `data/processed/engagement_report.csv`, and records execution in `logs/analytics.log`.

### Governance & Traceability

- `logs/pipeline.log` captures high-level phase timestamps and outcomes.  
- Phase-specific logs (validation, ingestion, analytics) contain row counts, SQL execution status, and error traces for auditing.  
- Processed outputs provide artifacts for downstream review or publishing.  
- A single entry point simplifies reruns and reproducibility for CI/CD or GitHub automation.

