# Prompt Fragments

## Writing Rule

Prefer short, concrete product language. Describe what the app is, what it is used for, and why a self-hosted user would choose it.

Field length limits:

- `summary`: at most 8 words; prefer 5 words or fewer.
- `overview`: at most 30 words; prefer 20 words or fewer.
- `description`: no hard limit; keep it factual and concise.

Count the words before writing, and prefer the shorter target unless it would drop essential meaning.

## Category Rule

Use the smallest correct set of category bindings. Do not add broad categories just because they are loosely related.

## Validation Rule

`.venv/bin/libs catalog-push --app <app> --json` is the preview gate for this skill. The file is not ready until the preview succeeds.
