"""Report generation endpoints."""
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.schemas import ReportRequest
from app.services.report_service import generate_pdf_report
from app.models.models import Report
from app.core.database import AsyncSessionLocal
from app.agents.orchestrator import ReportGeneratorAgent
from datetime import datetime

router = APIRouter(tags=["Reports"])
logger = logging.getLogger(__name__)


@router.post("/reports/generate")
async def generate_report(request: ReportRequest):
    """Generate a complete sustainability report."""
    # Build report data from DB if analysis_id provided
    analysis_data = {"language": "Python", "timestamp": datetime.utcnow().isoformat()}
    benchmark_data = {}
    ml_data = {}

    if request.analysis_id:
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select
                from app.models.models import Analysis, CodeFinding, Benchmark as BenchmarkModel, OptimizationRun

                stmt = select(Analysis).where(Analysis.id == request.analysis_id)
                res = await db.execute(stmt)
                analysis = res.scalar_one_or_none()

                if analysis:
                    stmt2 = select(CodeFinding).where(CodeFinding.analysis_id == request.analysis_id)
                    res2 = await db.execute(stmt2)
                    findings = res2.scalars().all()

                    analysis_data = {
                        "language": analysis.language,
                        "lines_of_code": len(analysis.code_snippet.splitlines()),
                        "timestamp": analysis.created_at.isoformat() if analysis.created_at else "",
                        "findings": [
                            {
                                "issue_id": f.issue_id,
                                "severity": f.severity,
                                "category": f.category,
                                "title": f.title,
                                "explanation": f.explanation,
                                "recommendation": f.recommendation,
                            }
                            for f in findings
                        ],
                        "score": analysis.score_breakdown or {},
                    }

                    # Get latest benchmark
                    stmt3 = select(BenchmarkModel).where(
                        BenchmarkModel.analysis_id == request.analysis_id
                    ).order_by(BenchmarkModel.id.desc())
                    res3 = await db.execute(stmt3)
                    benchmarks = res3.scalars().all()

                    if benchmarks:
                        b = benchmarks[0]
                        benchmark_data["before"] = {
                            "mean_runtime": b.mean_runtime,
                            "peak_memory_mb": b.peak_memory_mb,
                        }
                        if len(benchmarks) > 1:
                            b2 = benchmarks[1]
                            benchmark_data["after"] = {
                                "mean_runtime": b2.mean_runtime,
                                "peak_memory_mb": b2.peak_memory_mb,
                            }
                            if b.mean_runtime and b2.mean_runtime and b.mean_runtime > 0:
                                pct = ((b.mean_runtime - b2.mean_runtime) / b.mean_runtime) * 100
                                benchmark_data["comparison"] = {
                                    "runtime_reduction_pct": round(pct, 1)
                                }

        except Exception as e:
            logger.warning(f"Could not load analysis {request.analysis_id}: {e}")

    # Generate report
    agent = ReportGeneratorAgent()
    report_content = agent.generate(analysis_data, benchmark_data, ml_data)
    report_content["title"] = request.title

    # Persist
    report_id = 1
    try:
        async with AsyncSessionLocal() as db:
            r = Report(
                analysis_id=request.analysis_id,
                title=request.title,
                content_json=report_content,
            )
            db.add(r)
            await db.commit()
            report_id = r.id
    except Exception as e:
        logger.warning(f"Could not save report: {e}")

    # Generate PDF
    pdf_path = generate_pdf_report(report_content, report_id)

    if pdf_path:
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import select, update
                stmt = update(Report).where(Report.id == report_id).values(pdf_path=pdf_path)
                await db.execute(stmt)
                await db.commit()
        except Exception:
            pass

    return {
        "report_id": report_id,
        "title": request.title,
        "content": report_content,
        "pdf_available": pdf_path is not None,
        "pdf_path": pdf_path,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.get("/reports/{report_id}/pdf")
async def download_pdf(report_id: int):
    """Download the PDF report."""
    import os
    pdf_path = f"reports/greenforge_report_{report_id}.pdf"
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found. Generate the report first.")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"greenforge_report_{report_id}.pdf"
    )


@router.get("/reports/{report_id}/json")
async def download_json(report_id: int):
    """Download the JSON report."""
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            stmt = select(Report).where(Report.id == report_id)
            res = await db.execute(stmt)
            r = res.scalar_one_or_none()
            if not r:
                raise HTTPException(status_code=404, detail="Report not found")
            return r.content_json
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
