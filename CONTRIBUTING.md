# Contributing

Packs, taxonomy entries, and code contributions are welcome.

## Principles
- **Config-first**: Prefer changes that can be delivered via packs/taxonomy files, not code.
- **Deterministic**: Given the same inputs, checklist generation must produce the same output.
- **Auditable**: Changes should be trackable and explainable.

## Add a pack
1. Create a folder under `registry/packs/<domain>/<pack_id>/<version>/`
2. Add `pack.yaml`
3. Add one or more `controls/*.yaml` files
4. Run the pack linter:
   ```bash
   cd apps/api
   python -m truststack_grc.cli lint-packs --root ../../registry/packs
   ```

## Add a use case
Add a `use_case.yaml` under the taxonomy folder convention described in `docs/taxonomy-authoring.md`.
