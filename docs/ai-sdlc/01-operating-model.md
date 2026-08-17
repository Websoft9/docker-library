# Operating Model

Roles:
- Owner: defines demand, decides priority, runs final E2E, decides merge and release.
- AI Worker: researches upstream docs, edits files, runs automated checks, writes the report.
- CI: runs repeatable gates and stores artifacts.

Boundary:
- Human does not do routine implementation.
- Human does not do routine test execution.
- Human only does demand judgment and final E2E judgment.

Required inputs:
- Issue
- app name
- target version or target app
- upstream reference

Required outputs:
- code change
- automated test result
- risk summary
- owner E2E decision
