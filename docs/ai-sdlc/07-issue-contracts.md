# Issue Contracts

Issue is the story. Opening an issue starts the matching AI workflow.

Templates carry a hidden marker such as `<!-- libs:workflow=update-app -->`. The AI workflow reads it and uses the matching skill.

## Update

- app name
- target version when known
- upstream source
- risk hints or owner E2E focus

AI determines the candidate class (`patch | minor | major | security`) and decision (`auto-update | review-first | defer | skip`).

## New app

- app name
- trademark
- at least one official repository, image, or deployment reference
- known constraints

AI researches the auth model, storage needs, network and port needs.

## Batch update

- app names or initials
- target version policy when known
- confirmation that all apps share the same operation

## Bug

- app name and version
- expected and actual behavior
- reproduction steps and evidence

## Change request

- problem
- desired outcome
- acceptance notes or constraints

## Archive

- app name or list
- archive reason

The archive skill handles the Contentful retirement handoff.

## Restore

- app name
- optional cadence and update policy

## Rules

- one app per issue by default
- batch issues require the same operation and decision
- one issue per change topic
- owner decides whether an issue is worth doing
- AI reports missing information instead of guessing
