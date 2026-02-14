from __future__ import annotations

from fastapi import APIRouter, HTTPException

from truststack_grc.core.packs.loader import PackRegistry

router = APIRouter()

@router.get("")
def list_packs():
    reg = PackRegistry.from_env()
    return {"packs": reg.list_packs()}

@router.get("/{domain}/{pack_id}")
def list_pack_versions(domain: str, pack_id: str):
    reg = PackRegistry.from_env()
    versions = reg.list_pack_versions(domain=domain, pack_id=pack_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Pack not found")
    return {"domain": domain, "pack_id": pack_id, "versions": versions}

@router.get("/{domain}/{pack_id}/{version}")
def get_pack(domain: str, pack_id: str, version: str):
    reg = PackRegistry.from_env()
    pack = reg.load_pack(domain=domain, pack_id=pack_id, version=version)
    if not pack:
        raise HTTPException(status_code=404, detail="Pack version not found")
    return pack.model_dump()
