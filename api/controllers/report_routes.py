from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from visual.report_generator import generate_report_pdf
from api.global_simulation import get as get_simulation

router = APIRouter()

@router.get("/reports/reports/pdf")
def get_pdf_report():
    sim = get_simulation()
    if sim is None:
        raise HTTPException(status_code=400, detail="No hay simulación activa. Genera una en el dashboard primero.")

    filename = generate_report_pdf(sim)
    return FileResponse(path=filename, filename=filename, media_type="application/pdf")
