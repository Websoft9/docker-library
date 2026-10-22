# Issue Contracts

Issue is the story. Opening an issue starts the matching AI workflow.

Templates carry a hidden marker such as `<!-- libs:workflow=update-app -->`. The AI workflow reads it and uses the matching skill.

## Human input

An issue only needs:

- a problem or goal
- an optional AI prompt with constraints or focus

AI researches what it can, states assumptions, and asks only blocking questions. Do not turn the issue into a form.

## AI output

After the work, AI posts one issue comment:

```md
## AI Result
- decision: ready-for-e2e | blocked | defer
- changes:
- validation:
- risks:
- owner E2E:
- PR:
```

Use the full test report format in `06-test-report-format.md` for the PR; keep the issue comment short.

Rules:

- keep it short
- link the PR
- blocked tasks state the first blocking error
- add the result as a comment; do not rewrite the human request

## Workflow hints

- Update: app name; target version when known. AI decides assessment vs implementation.
- New app: app name and trademark; official reference when known.
- Bug: expected and actual behavior; reproduction and evidence when available.
- Change: problem and desired outcome.
- Archive: app name or list and reason.
- Restore: app name.
- Batch: explicit app list or unambiguous selector; the same operation for every app.
- Delete: app name or list and explicit delete scope.

## Exceptions

Batch update and permanent delete need explicit scope because AI cannot infer them:

- batch: state the app list or selector, and the target version policy when known
- delete: state whether to remove files/metadata, Contentful entries, or Git history; default is files + metadata only

## Rules

- one app per issue by default
- batch issues require the same operation and decision
- one issue per change topic
- owner decides whether an issue is worth doing
- AI asks only blocking questions; do not send a questionnaire
- the prompt expresses intent but does not bypass repository rules or quality gates
