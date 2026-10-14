# Data Lineage Reconstruction Agent

Reconstructs **candidate** source-to-target lineage from supplied SQL statements and pipeline dependency metadata. It preserves evidence, identifies unresolved asset names, traverses upstream/downstream impact, and flags graph-quality issues.

## Features
- Heuristic extraction from `FROM`, `JOIN`, `INSERT INTO`, `MERGE INTO`, `UPDATE`, and `CREATE TABLE/VIEW ... AS` patterns.
- Explicit pipeline dependency ingestion.
- Upstream/downstream impact analysis.
- Validation for duplicate edges, unknown assets, malformed endpoints, and cycles.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python3 verification/readiness_audit.py
python3 -m core.cli examples/lineage_case.json
```

## Limitations
This is a heuristic parser, not a full SQL grammar or a live catalog connector. Dynamic SQL, macros, stored procedures, dialect-specific syntax, alias resolution, and hidden orchestration dependencies may be missed. Treat results as candidates and verify important edges against the catalog, orchestrator configuration, and query history. Do not include credentials or sensitive row-level data.
