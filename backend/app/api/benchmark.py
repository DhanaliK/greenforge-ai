"""Benchmark execution endpoint."""
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import BenchmarkRequest, BenchmarkResult
from app.benchmarking.runner import run_benchmark, compute_comparison
from app.sustainability.engine import SustainabilityEngine
from app.models.models import Benchmark as BenchmarkModel
from app.core.database import AsyncSessionLocal
from app.core.config import settings

router = APIRouter(tags=["Benchmark"])
logger = logging.getLogger(__name__)


@router.post("/benchmark")
async def run_code_benchmark(request: BenchmarkRequest):
    """
    Execute code benchmark in safe subprocess.
    WARNING: Only run trusted code in controlled/local environments.
    """
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if len(request.code) > settings.MAX_CODE_SIZE_KB * 1024:
        raise HTTPException(status_code=400, detail="Code too large for benchmarking")

    runs = min(request.runs, 10)
    result = run_benchmark(request.code, runs=runs, timeout=settings.BENCHMARK_TIMEOUT)

    # Sustainability estimate
    sus = None
    if result.get("success") and result.get("mean_runtime"):
        engine = SustainabilityEngine()
        sus = engine.estimate_from_runtime(
            result["mean_runtime"],
            result.get("cpu_time"),
            label=request.label
        )

    # Persist
    bench_id = None
    try:
        async with AsyncSessionLocal() as db:
            b = BenchmarkModel(
                analysis_id=request.analysis_id,
                label=request.label,
                code_snippet=request.code[:5000],
                runs=runs,
                mean_runtime=result.get("mean_runtime"),
                min_runtime=result.get("min_runtime"),
                max_runtime=result.get("max_runtime"),
                median_runtime=result.get("median_runtime"),
                mean_memory_mb=result.get("mean_memory_mb"),
                peak_memory_mb=result.get("peak_memory_mb"),
                cpu_time=result.get("cpu_time"),
                success=result.get("success", False),
                error_message=result.get("error_message"),
                output_sample=result.get("output_sample"),
                raw_results=result.get("raw_results"),
            )
            db.add(b)
            await db.commit()
            bench_id = b.id
    except Exception as e:
        logger.warning(f"DB persist error: {e}")

    return {**result, "id": bench_id, "label": request.label, "sustainability": sus}


@router.get("/benchmarks/{benchmark_id}")
async def get_benchmark(benchmark_id: int):
    """Retrieve a benchmark result by ID."""
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            stmt = select(BenchmarkModel).where(BenchmarkModel.id == benchmark_id)
            res = await db.execute(stmt)
            b = res.scalar_one_or_none()
            if not b:
                raise HTTPException(status_code=404, detail="Benchmark not found")
            return {
                "id": b.id,
                "label": b.label,
                "success": b.success,
                "runs": b.runs,
                "mean_runtime": b.mean_runtime,
                "min_runtime": b.min_runtime,
                "max_runtime": b.max_runtime,
                "median_runtime": b.median_runtime,
                "mean_memory_mb": b.mean_memory_mb,
                "peak_memory_mb": b.peak_memory_mb,
                "cpu_time": b.cpu_time,
                "error_message": b.error_message,
                "output_sample": b.output_sample,
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
