from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from truststack_grc.api.routers import packs, projects, taxonomy, reports
from truststack_grc.config import get_settings

settings = get_settings()

app = FastAPI(
    title="TrustStack AI GRC Workbench API",
    version=settings.generator_version,
    description="Config-driven packs → controls → evidence → audit-ready.",
)

# In production, tighten CORS and add auth. This is a dev-friendly default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(taxonomy.router, prefix="/api/taxonomy", tags=["taxonomy"])
app.include_router(packs.router, prefix="/api/packs", tags=["packs"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "truststack-grc", "config_root": str(settings.config_root)}
