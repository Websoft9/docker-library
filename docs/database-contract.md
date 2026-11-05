# Database Contract

The canonical contract is [应用数据库连接与声明规范](app-database-connection-spec.md).

New and migrated packages declare `database[]` in `variables.json` and use
`metadata/database-types.json`. Declarations describe facts only; they do not
select connections, mutate configuration, or manage database objects.

This file is a compatibility link, not a second specification. The obsolete
`metadata/database-defaults.json` draft has been removed; it is not a fallback or
compatibility layer. The schema accepts old `database` objects during transition
and the CLI reports a migration warning, including for restored archives. Old
objects are not expanded using a separate defaults dictionary.

`externalDB` remains user-facing compatibility help. `metadata/db-lifecycle.json`
remains the independent lifecycle source. Neither replaces connection declarations.
