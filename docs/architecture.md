# Architecture (v1) — Config-first, file-based, auditable

This repository is intentionally **folder-driven** and **metadata-driven**:
- Add a new use case by adding a new YAML file in the taxonomy tree.
- Add a new standard/framework by dropping a new pack folder under `registry/packs/...`.
- No database is required for v1: projects are stored as **folders** under `workspaces/`.

## Core runtime flow
1. **Discover taxonomy** from `registry/taxonomy/industries/**/use_case.yaml`
2. **Render scoping questions** (from use-case config) and collect answers
3. **Normalize context** into a stable JSON object
4. **Discover packs** from `registry/packs/<domain>/<pack_id>/<version>/`
5. **Validate pack schemas** (JSON Schema)
6. **Evaluate applicability rules** per control against context (JSONLogic-like DSL)
7. **Generate checklist** (dedupe via optional `canonical_id`)
8. **Persist project state** as files
9. **Track work + evidence** with an append-only audit log and evidence hashes
10. **Export reports** (HTML/JSON/CSV; PDF scaffold)

## Separation of concerns
- `core/taxonomy/` loads taxonomy + questions (no workflow logic)
- `core/packs/` loads/validates packs (no mapping logic)
- `core/mapping/` applies rule evaluation + dedup + reasons (no persistence)
- `core/storage/` persists to filesystem + audit log + evidence hashes (no UI/business rules)
- `core/reporting/` renders exports from stored state (no mutation)

## Why file-based storage?
- Enables “GitOps for assurance”: packs + taxonomy + workspaces can be versioned.
- Deterministic regeneration is easy: same inputs → same output.
- Low operational overhead for v1 while remaining enterprise-auditable.

> When you outgrow filesystem storage, keep the same `Storage` interface and add a Postgres/ORM implementation.
