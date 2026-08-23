from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.services.report_service import generate_beam_pdf_report
from app.services.wellness_service import calculate_wellness_metrics
from app.services.store_service import get_journals

router = APIRouter(prefix="/reports", tags=["reports"])

class ReportGenerateRequest(BaseModel):
    title: str | None = "Longitudinal Emotional Intelligence & Behavioral Report"
    time_range: str | None = "weekly"

@router.post("/generate")
def create_report_meta(payload: ReportGenerateRequest) -> dict[str, Any]:
    return {
        "status": "success",
        "report_id": "REP-2026-AUG",
        "title": payload.title,
        "format": "PDF (ReportLab 5.0)",
        "download_url": "/api/v1/reports/download"
    }

@router.get("/download")
def download_pdf_report():
    journals = get_journals()
    wellness = calculate_wellness_metrics(journals)
    
    pdf_bytes = generate_beam_pdf_report(
        user_name="BEAM Researcher",
        wellness_data=wellness,
        recent_journals=journals
    )
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=BEAM_AI_Affective_Report.pdf"
        }
    )
