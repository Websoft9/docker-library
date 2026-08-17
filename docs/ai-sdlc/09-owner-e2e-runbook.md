# Owner E2E Runbook

Owner only checks the final result.

Minimum checks:
1. Install succeeds.
2. Main page or main port is reachable.
3. Default login or first-run path works when the app supports it.
4. One core user action works.

Decision:
- `pass`: merge and release
- `retry`: send back to AI with a clear blocking point
- `reject`: close or defer the task

Archive decision:
- if the app should be retired, owner may choose `archive`
- archived apps move to `archive/apps/` and must also trigger Contentful metadata retirement

Owner should not repeat AI's routine checks unless the report is incomplete.
