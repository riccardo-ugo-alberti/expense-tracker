# Repository Guidance

- Preserve the modular `src/` structure.
- Keep one unified app and one unified database across all banks and accounts.
- Prefer deterministic, explicit logic over implicit or heuristic-heavy behavior.
- Keep SQLite compatibility first and make PostgreSQL migration easy later.
- Do not invent bank export schemas before inspecting real sample files.
- Do not log sensitive financial data or full transaction payloads in plaintext logs.
- Avoid overengineering, ML-heavy solutions, and premature abstractions.
- Treat banks and accounts as transaction sources, not separate products.
