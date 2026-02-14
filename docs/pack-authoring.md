# Pack authoring guide

A **pack** is a versioned folder that contains:
- `pack.yaml` — metadata (id, version, domain, source)
- `controls/*.yaml` — controls (one or many files)
- optional:
  - `mappings/` — crosswalks (e.g., EU AI Act articles ↔ canonical controls)
  - `suggestions.yaml` — patterns/tools recommended for controls
  - `templates/` — evidence templates (docs/checklists)

## Folder convention
```
registry/packs/<domain>/<pack_id>/<version>/
  pack.yaml
  controls/
    001.yaml
    002.yaml
```

## Control applicability DSL (JSONLogic-like)
Controls include an `applicability` object evaluated against a normalized `context`:

Examples:
```yaml
applicability:
  all:
    - equals: ["industry", "healthcare"]
    - any:
        - equals: ["data.phi", true]
        - equals: ["data.pii", true]
```

Supported operators (v1):
- `all` / `any` / `not`
- `equals`
- `in`
- `exists`
- `contains` (strings/arrays)
- `has_tag` (checks `context.tags`)

> Extend operators in `core/mapping/rules.py` without changing pack format.

## Validation
Run the pack linter:
```bash
cd apps/api
python -m truststack_grc.cli lint-packs --root ../../registry/packs
```
