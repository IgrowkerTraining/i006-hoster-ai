from app.db.models.schemas import ReportRequest, ReportResponse
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date
from app.db.models.report_model import Report
from sqlalchemy import select
from fastapi import HTTPException

from app.api.dependencies import get_main_db, get_ai_db, get_ai_service
from app.services.ai_service import AIService

router = APIRouter(prefix="/reports", tags=["reports"])

#Get All
@router.get("/", response_model=list[ReportResponse])
async def get_reports(
    limit: int = 10,
    offset: int = 0,
    ai_db: AsyncSession = Depends(get_ai_db)
):

    result = await ai_db.execute(
        select(Report)
        .order_by(Report.report_date.desc())
        .limit(limit)
        .offset(offset)
    )

    reports = result.scalars().all()

    return reports
    
    
#Get By Id
@router.get("/{report_id}", response_model=ReportResponse)
async def get_report_by_id(
    report_id: int,
    ai_db: AsyncSession = Depends(get_ai_db)
):

    result = await ai_db.execute(
        select(Report).where(Report.id == report_id)
    )

    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.post("/generate")
async def generate_report(
    data: ReportRequest,
    main_db: AsyncSession = Depends(get_main_db),
    ai_db: AsyncSession = Depends(get_ai_db),
    ai_service: AIService = Depends(get_ai_service)
):
    month = data.month
    year = data.year

    result = await main_db.execute(
        text("""
        SELECT 
            COUNT(*) as total_reservations,
            MIN("createdAt") as first_reservation,
            MAX("createdAt") as last_reservation
        FROM reserves
        WHERE EXTRACT(MONTH FROM "createdAt") = :month
        AND EXTRACT(YEAR FROM "createdAt") = :year
        """),
        {"month": month, "year": year}
    )

    stats = result.mappings().first()

    analysis_prompt = f"""
    Analiza las reservas del sistema.

    Mes analizado: {month}
    Año analizado: {year}

    Total de reservas: {stats['total_reservations']}
    Primera reserva del período: {stats['first_reservation']}
    Última reserva del período: {stats['last_reservation']}

    Genera un análisis del comportamiento de reservas.
    """

    ai_response = await ai_service.chat_completion({
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "user", "content": analysis_prompt}
        ]
    })

    # Guardar reporte en AI DB
    await ai_db.execute(
    text("""
        INSERT INTO reports (report_date, analyzed_period, description)
        VALUES (:report_date, :analyzed_period, :description)
    """),
    {
        "report_date": date.today(),
        "analyzed_period": f"Mes:{month} Año:{year}",
        "description": ai_response,
    }
)
    
    await ai_db.commit()

    return {"status": "report generated"}


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    ai_db: AsyncSession = Depends(get_ai_db)
):

    result = await ai_db.execute(
        select(Report).where(Report.id == report_id)
    )

    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    await ai_db.delete(report)
    await ai_db.commit()

    return {"message": "Report deleted"}