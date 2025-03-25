## File Structure
🧠 This is the Xenda repo — no client-specific stuff should live here!
```plaintext
.
├── xendas/                            # Also known as ETLs or data pipelines
│   ├── xenda.py                       # (1) Primary orchestration script:
│   │   └── Traverses YAML config (stages → groups → steps)
│   │       Handles parallel/sequential logic
│   │       Implements retry & logging
│   │       Supports pre-step views via `pre_views` for joins/lookups
│
│   ├── run_xenda.py                   # (2) CLI entry point:
│   │   └── Boots Spark, loads config, runs pipeline
│   │       Saves logs to JSON and optionally writes metadata
│
│   ├── requirements.txt               # Dependencies for Xenda
│   └── Dockerfile                     # Docker build instructions (base image for clients)
│
├── invoker/                           # Centralized trigger dispatcher
│   ├── invoker.py                     # (3) Sends webhook/job triggers to Xenda agents
│   ├── requirements.txt
│   └── Dockerfile
│
├── scrolls/
│   └── config.yaml                    # (4) Client config: webhooks, tokens, scheduling
│
├── footprints/                        # (5) Execution logs
│   └── xenda_footprints.json
│       └── Step-level run info: success/failure, retries, timing
│
├── trials/                            # Unit tests (aka Trials)
│   ├── test_dq.py                     # (6) Tests for `dq_checks.py`
│   ├── test_retry.py                  # (7) Tests retry logic
│   ├── test_sql_loader.py             # (8) Tests SQL template rendering
│   ├── test_checkpoints.py            # (9) Tests step checkpoint logic
│   ├── test_batch_id.py               # (10) Tests batch ID creation logic
│   ├── test_pipeline_structure.py     # (11) Validates YAML schema
│   └── __init__.py                    # (12) Enables test discovery
│
├── utils/                             # Utility modules for pipeline execution
│   ├── sql_loader.py                  # (13) Renders SQL using Jinja2
│   ├── sql_runner.py                  # (14) Executes SQL in Spark, writes output
│   ├── dq_checks.py                   # (15) Executes DQ SQL files
│   ├── metadata_logger.py             # (16) Writes JSON logs to Delta
│   ├── datasource.py                  # (17) Manages JDBC/connection configs
│   └── __init__.py                    # (18) Makes utils importable
│
└── run_pipeline.sh                    # (19) Bash launcher for pipelines
    └── Defaults to 'main_flow'; validates config; runs Python CLI

```

### ✨ This is the Scroll repo — one scroll per client.

```plaintext
.
├── scrolls/
|   ├── main_flow.yaml                    # (1) YAML DAG definition:
|   │   └── Orchestration config: stages, steps, retries, DQ, secrets, etc.
|   │       Reconfigurable without touching code
|   │
|   spells/                               # SQL, Python, or any transform logic
|   ├── extract/                          # Bronze layer
|   │   ├── students.sql                  # (2) Raw ingestion from source systems
|   │   └── schools.sql                   # (3) Another Bronze-level raw load
|   │
|   ├── brew/                             # Silver layer (Data Vault modeling)
|   │   ├── hub_student.sql
|   │   ├── hub_school.sql
|   │   ├── link_enrollment.sql
|   │   └── sat_student_demographics.sql  # (4) Hubs, Links, Sats (MERGE INTO / INSERT logic)
|   │
|   ├── distill/                          # Gold layer (Star Schema for analytics)
|   |   ├── dim_student.sql
|   |   ├── dim_school.sql
|   |   └── fact_enrollment.sql           # (5) Facts/dimensions for dashboards
├── dq/
|   ├── extract/                          # Bronze-level checks
|   │   ├── students/
|   │   │   ├── row_count.sql
|   │   │   └── not_null_studentid.sql     # (6) Row counts, null checks
|   │   └── schools/
|   │       └── row_count.sql              # (7) Empty file guard
|   │
|   ├── brew/                             # Silver-level checks
|   │   ├── hub_student/
|   │   │   └── unique_keys.sql            # (8) Primary key uniqueness
|   │   ├── hub_school/
|   │   │   └── (possible checks)
|   │   ├── link_enrollment/
|   │   │   └── (possible checks)
|   │   └── sat_student_demographics/
|   │       └── (possible checks)          # (9) Optional: referential integrity, field validation
|   │
|   └── distill/                          # Gold-level checks
|       ├── dim_student/
|       │   └── not_null_dim_id.sql       # (10) Surrogate key must exist
|       ├── dim_school/
|       │   └── (possible checks)
|       └── fact_enrollment/
|           └── valid_dates.sql           # (11) Date logic (e.g., start_date < end_date)

```