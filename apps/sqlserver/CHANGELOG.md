# CHANGELOG

## 2026-09-22

- Update the default SQL Server image target from `2022` to `2025`.
- Keep the packaged version list limited to `2025` and `2022`.
- Replace deprecated `SA_PASSWORD` wiring with `MSSQL_SA_PASSWORD` and align `.env`/Compose files with current repository policy.
- Add upstream metadata and a sqlcmd-based smoke test for deployment validation.
