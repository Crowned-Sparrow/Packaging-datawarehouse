# ML Schema for Packaging Data Warehouse

## Tables

### `training_breakdown_risk`
Daily machine-level features and breakdown prediction target labels for ML training.

**Purpose**: Feature store for predictive maintenance model to detect machines at risk of breaking down.

**Grain**: 1 row per (date, machine) combination.

**Key Columns**:
- `feature_date`: Date for which features are computed
- `machine_id`: Reference to corrugating machine (FK to corrugating.dim_machines)
- `total_runs`: Number of production runs on this day
- `total_production_minutes`: Total production time (minutes)
- `avg_run_minutes`: Average run duration (minutes)
- `breakdown_count`: Number of breakdown incidents
- `downtime_minutes`: Total downtime (minutes)
- `label_has_breakdown`: Target label (1 = breakdown occurred, 0 = no breakdown)

**Constraints**:
- Unique on (feature_date, machine_id)
- Foreign key: machine_id → corrugating.dim_machines
- All numeric columns ≥ 0
- label_has_breakdown ∈ {0, 1}

**Indexes**:
- feature_date DESC (query recent data)
- machine_id (filter by machine)
- label_has_breakdown (model training splits)
- (feature_date DESC, machine_id) composite

**Refresh Cadence**: Daily via ETL pipeline

## How to Initialize

1. Ensure database connection env vars are set:
   ```bash
   export PG_USER=...
   export PG_PASSWORD=...
   export PG_HOST=...
   export PG_PORT=5432
   export PG_DB=...
   ```

2. Run schema initialization from project root:
   ```bash
   python -m backend.etl.config.init_ml_schema
   ```

3. Verify schema was created:
   ```bash
   psql -U $PG_USER -h $PG_HOST -d $PG_DB -c "
     SELECT schemaname, tablename FROM pg_tables 
     WHERE schemaname = 'ml';
   "
   ```

## ETL Integration

Daily ETL pipeline loads features into this table:

```bash
python -m backend.etl.pipelines.daily_batch
```

Or set environment variable to load to Postgres:

```bash
export ETL_LOAD_TO_POSTGRES=true
python -m backend.etl.pipelines.daily_batch
```

Output file: `backend/etl/output/training_breakdown_risk.parquet`
