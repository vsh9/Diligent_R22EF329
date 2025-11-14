#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
PIPELINE_LOG="$LOG_DIR/pipeline.log"
DATA_RAW="$ROOT_DIR/data/raw"
DATA_PROCESSED="$ROOT_DIR/data/processed"

mkdir -p "$LOG_DIR" "$DATA_RAW" "$DATA_PROCESSED"
touch "$PIPELINE_LOG"

log() {
  local level="$1"
  shift
  local message="$*"
  local timestamp
  timestamp="$(date -Iseconds)"
  echo "${timestamp} | ${level} | ${message}" | tee -a "$PIPELINE_LOG"
}

log_info() {
  log "INFO" "$*"
}

log_error() {
  log "ERROR" "$*"
}

run_cmd() {
  local description="$1"
  shift
  log_info "$description"
  if ! "$@"; then
    log_error "$description failed"
    echo "Pipeline failed: $description"
    exit 1
  fi
}

log_info "==============================================="
log_info "Starting Agentic SDLC pipeline run"

echo ""
echo "==============================================="
echo "[PHASE 1] DATA GENERATION"
echo "Generating synthetic datasets..."
echo "==============================================="
DATA_GENERATORS=(
  "implementation/data_generation/generate_customers.py"
  "implementation/data_generation/generate_plans.py"
  "implementation/data_generation/generate_content.py"
  "implementation/data_generation/generate_subscriptions.py"
  "implementation/data_generation/generate_usage_logs.py"
)

for script in "${DATA_GENERATORS[@]}"; do
  run_cmd "Running ${script}" python "$ROOT_DIR/$script"
done
log_info "Phase 1 complete: All datasets generated in data/raw/"

echo ""
echo "==============================================="
echo "[PHASE 2] VALIDATION"
echo "Validating schema, referential integrity, and logical rules..."
echo "==============================================="
run_cmd "Validating generated data" python "$ROOT_DIR/validation/validate_data.py"
log_info "Phase 2 complete: Data validation passed"

echo ""
echo "==============================================="
echo "[PHASE 3] INGESTION"
echo "Loading data into SQLite database..."
echo "==============================================="
run_cmd "Ingesting data into SQLite" python "$ROOT_DIR/implementation/ingestion/load_db.py"
log_info "Phase 3 complete: Database ecommerce.db created/updated"

echo ""
echo "==============================================="
echo "[PHASE 4] ANALYTICS"
echo "Compiling SQL views and generating reports..."
echo "==============================================="
run_cmd "Running analytics views and exports" python "$ROOT_DIR/implementation/analytics/run_analytics.py"
log_info "Phase 4 complete: Analytics reports exported"

log_info "Pipeline completed successfully"
echo ""
echo "==============================================="
echo "✓ All phases completed successfully!"
echo ""
echo "Generated outputs:"
echo "  - Raw data: data/raw/*.csv"
echo "  - Database: ecommerce.db"
echo "  - Reports: data/processed/*.csv"
echo ""
echo "Logs available in:"
echo "  - logs/pipeline.log (orchestration log)"
echo "  - logs/validation.log (data validation)"
echo "  - logs/ingestion.log (database operations)"
echo "  - logs/analytics.log (view compilation)"
echo "==============================================="

