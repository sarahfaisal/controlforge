from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from truststack_grc.core.reporting.service import ReportingService
from truststack_grc.core.storage.filesystem import FileSystemStorage

router = APIRouter()

@router.get("/{project_id}")
def export_report(project_id: str, format: str = "html"):
    storage = FileSystemStorage.from_env()
    service = ReportingService(storage=storage)

    if format == "html":
        html = service.render_html(project_id)
        if html is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return HTMLResponse(content=html)

    if format == "json":
        data = service.export_json(project_id)
        if data is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return data

    if format == "csv":
        path = service.export_csv(project_id)
        if path is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return FileResponse(path, filename=f"{project_id}.csv", media_type="text/csv")

    if format == "pdf":
        path = service.export_pdf(project_id)
        if path is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return FileResponse(path, filename=f"{project_id}.pdf", media_type="application/pdf")

    raise HTTPException(status_code=400, detail="Unknown format. Use html|json|csv|pdf")
