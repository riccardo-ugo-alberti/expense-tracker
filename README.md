# expense-tracker

Multi-account personal finance tracker for importing manual bank exports into one consolidated system.

## Overview

This project is designed as one unified application with one unified database for personal finance analysis.
Multiple bank accounts feed the same datastore, and the dashboard will analyze all transactions together rather than splitting data by bank.

Current supported sources are manual exports from:

- Cortina Banca / Inbank
- Volksbank

Additional banks and accounts can be added later as new transaction sources.

## Architecture Direction

- One SQLite database for local development today
- Easy migration path to PostgreSQL later through SQLAlchemy and `DATABASE_URL`
- Raw and cleaned transaction layers remain separate
- Banks and accounts are modeled as sources, not as separate apps or separate databases

The database layer now supports:

- `accounts` for multiple user-owned bank accounts
- `import_runs` to track manual import batches
- `transactions_raw` linked to an account
- `transactions_clean` linked to an account

The clean transaction model is also prepared for future internal transfer handling with:

- `direction`
- `internal_transfer_candidate`
- `transfer_group`
- `needs_review`

## Current Scope

- Manual bank export ingestion only
- No open banking integrations
- No scraping or bank APIs
- No bank-specific parser logic without real sample files

## Next Planned Step

The next planned step is a file upload UI with import preview, so manual exports can be reviewed before they are stored in the consolidated database.
Unified dashboard views with account-level filtering will come later.
