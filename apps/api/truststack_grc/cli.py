from __future__ import annotations

import argparse
import sys
from pathlib import Path

from truststack_grc.core.packs.loader import PackRegistry
from truststack_grc.core.taxonomy.loader import TaxonomyLoader

def cmd_list_packs(_args: argparse.Namespace) -> int:
    reg = PackRegistry.from_env()
    packs = reg.list_packs()
    for p in packs:
        versions = ", ".join(p["versions"])
        print(f'{p["domain"]}/{p["pack_id"]}: {versions}')
    return 0

def cmd_list_taxonomy(_args: argparse.Namespace) -> int:
    tax = TaxonomyLoader.from_env()
    for ind in tax.list_industries():
        print(f'{ind["id"]}: {ind.get("name")}')
        for seg in ind.get("segments", []):
            print(f'  - {seg["id"]}: {seg.get("name")}')
            for uc in seg.get("use_cases", []):
                print(f'      * {uc["id"]}: {uc.get("name")}')
    return 0

def cmd_lint_packs(args: argparse.Namespace) -> int:
    # Uses the same loader/validators as runtime
    reg = PackRegistry.from_env()
    root = Path(args.root).resolve()
    ok = True
    for domain_dir in sorted([d for d in root.iterdir() if d.is_dir()], key=lambda p: p.name):
        for pack_dir in sorted([d for d in domain_dir.iterdir() if d.is_dir()], key=lambda p: p.name):
            for ver_dir in sorted([d for d in pack_dir.iterdir() if d.is_dir()], key=lambda p: p.name):
                domain, pack_id, version = domain_dir.name, pack_dir.name, ver_dir.name
                try:
                    pack = reg.load_pack(domain=domain, pack_id=pack_id, version=version)
                    if not pack:
                        raise RuntimeError("Missing pack.yaml?")
                    print(f"OK  {domain}/{pack_id}/{version}  controls={len(pack.controls)}  hash={pack.hash[:10]}…")
                except Exception as e:
                    ok = False
                    print(f"ERR {domain}/{pack_id}/{version}: {e}", file=sys.stderr)
    return 0 if ok else 2

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="truststack-grc", description="TrustStack AI GRC Workbench CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list-packs", help="List discovered packs")
    sp.set_defaults(func=cmd_list_packs)

    st = sub.add_parser("list-taxonomy", help="List discovered industries/segments/use cases")
    st.set_defaults(func=cmd_list_taxonomy)

    sl = sub.add_parser("lint-packs", help="Validate pack manifests and control files")
    sl.add_argument("--root", default="../../registry/packs", help="Packs root folder")
    sl.set_defaults(func=cmd_lint_packs)
    return p

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
