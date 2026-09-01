# CHANGELOG

## 2026-08-31
- Created the initial Canvas app package.
- Added a custom source-based Canvas image build using the official upstream Dockerfile pattern.
- Added web, jobs, PostgreSQL, and Redis services.
- Added first-start bootstrap for database setup and administrator creation.
- Switched the Canvas source target from an old `v5.14.2` tag to the current official `release/2026-05-20.143` line.
- Aligned the Dockerfile more closely with the official production build flow to fix asset compile incompatibilities.
