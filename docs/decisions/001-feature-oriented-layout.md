# ADR-001: Use a Feature-Oriented Source Layout

## Status

Accepted

## Date

2026-08-15

## Context

The 2.x application grew from a layer-oriented layout where pages, table
models, workers, and dialogs were separated by technical type. Adding an
independent page required edits across several top-level packages, making the
ownership of a feature difficult to see.

## Decision

Organize presentation code by feature under `src/features/<feature>/`.

- A feature page owns its `page.py`, feature-specific dialogs, Qt models,
  workers, and generated UI files.
- `src/shared/` owns reusable application, configuration, persistence, domain,
  runtime, VPK, UI, and widget code. It must not import a feature.
- `src/shell/main_window.py` composes feature pages and owns navigation only.
- Add `service.py` or `worker.py` only when a feature actually needs those
  responsibilities.

## Alternatives Considered

### Keep the type-oriented layout

This keeps files familiar but spreads a single page across `views`, `models`,
and `services`, which makes isolated changes harder to make safely.

### Put all code under a single `pages` package

This improves page discovery but does not establish ownership for feature-local
models, workers, dialogs, and generated UI modules.

## Consequences

New standalone pages can be added as one feature package, while shared code
remains reusable without coupling it to a page. Imports change, but runtime
behavior and existing database migration behavior are preserved.
