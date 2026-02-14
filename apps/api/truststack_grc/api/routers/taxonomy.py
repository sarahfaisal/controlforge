from __future__ import annotations

from fastapi import APIRouter, HTTPException

from truststack_grc.core.taxonomy.loader import TaxonomyLoader

router = APIRouter()

@router.get("/industries")
def list_industries():
    loader = TaxonomyLoader.from_env()
    return {"industries": loader.list_industries()}

@router.get("/industries/{industry_id}")
def get_industry(industry_id: str):
    loader = TaxonomyLoader.from_env()
    industry = loader.get_industry(industry_id)
    if not industry:
        raise HTTPException(status_code=404, detail="Industry not found")
    return industry

@router.get("/use-cases/{use_case_id}")
def get_use_case(use_case_id: str):
    loader = TaxonomyLoader.from_env()
    uc = loader.get_use_case(use_case_id)
    if not uc:
        raise HTTPException(status_code=404, detail="Use case not found")
    return uc
