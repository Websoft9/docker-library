# Issue Contracts

Issue is the story.

Update issue must include:
- app name
- current version
- target version
- upstream source
- candidate class: patch | minor | major | security
- decision target: auto-update | review-first

New app issue must include:
- app name
- official repository or docs
- official image or compose reference
- auth model
- storage needs
- network or port needs

Rules:
- one app per issue by default
- batch issues are allowed only for the same operation and the same decision, such as archiving a small set of apps together
- one issue per change topic
- owner decides whether an issue is worth doing

Archive issue must include:
- app name or app list
- archive reason
- whether Contentful metadata must be retired
