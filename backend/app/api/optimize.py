"""Code optimization endpoint."""
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import OptimizationRequest
from app.agents.orchestrator import OptimizationAgent, BenchmarkValidatorAgent
from app.sustainability.engine import SustainabilityEngine
from app.models.models import OptimizationRun
from app.core.database import AsyncSessionLocal
from app.core.config import settings

router = APIRouter(tags=["Optimize"])
logger = logging.getLogger(__name__)


@router.post("/optimize")
async def optimize_code(request: OptimizationRequest):
    """Generate and benchmark an optimized version of the provided code."""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    findings = request.findings or []
    if isinstance(findings, list) and findings and hasattr(findings[0], 'dict'):
        findings = [f.dict() for f in findings]
    elif isinstance(findings, list) and findings and hasattr(findings[0], 'model_dump'):
        findings = [f.model_dump() for f in findings]

    # Step 1: Generate optimization
    opt_agent = OptimizationAgent()
    opt_result = opt_agent.run(request.code, findings, request.language)

    optimized_code = opt_result.get("optimized_code", request.code)
    explanation = opt_result.get("explanation", "")
    trade_offs = opt_result.get("trade_offs", "")
    ai_provider = opt_result.get("ai_provider", "Unknown")

    # Step 2: Validate syntax
    validation_passed = True
    validation_message = "Syntax validation passed"
    if request.language == "python":
        import ast
        try:
            ast.parse(optimized_code)
        except SyntaxError as e:
            validation_passed = False
            validation_message = f"Optimized code has syntax error: {e}"
            optimized_code = request.code  # revert

    # Step 3: Benchmark if requested
    before_bench = None
    after_bench = None
    comparison = None

    if request.run_benchmark and validation_passed:
        try:
            validator = BenchmarkValidatorAgent()
            bench_result = validator.run(
                request.code,
                optimized_code,
                runs=min(settings.BENCHMARK_RUNS, 5)
            )
            before_bench = bench_result["before"]
            after_bench = bench_result["after"]
            comparison = bench_result["comparison"]

            # Add sustainability estimates
            sus_engine = SustainabilityEngine()
            if before_bench.get("mean_runtime"):
                before_bench["sustainability"] = sus_engine.estimate_from_runtime(
                    before_bench["mean_runtime"], before_bench.get("cpu_time"), label="Before"
                )
            if after_bench.get("mean_runtime"):
                after_bench["sustainability"] = sus_engine.estimate_from_runtime(
                    after_bench["mean_runtime"], after_bench.get("cpu_time"), label="After"
                )
        except Exception as e:
            logger.error(f"Benchmark error: {e}", exc_info=True)
            comparison = {"improvement_label": f"Benchmark failed: {str(e)[:100]}"}

    # Persist
    opt_id = None
    try:
        async with AsyncSessionLocal() as db:
            opt = OptimizationRun(
                analysis_id=request.analysis_id,
                original_code=request.code[:5000],
                optimized_code=(optimized_code or "")[:5000],
                explanation=explanation[:2000],
                trade_offs=trade_offs[:1000],
                validation_passed=validation_passed,
                validation_message=validation_message,
                status="complete",
                ai_provider=ai_provider,
            )
            db.add(opt)
            await db.commit()
            opt_id = opt.id
    except Exception as e:
        logger.warning(f"DB persist error: {e}")

    return {
        "optimization_id": opt_id,
        "original_code": request.code,
        "optimized_code": optimized_code,
        "explanation": explanation,
        "trade_offs": trade_offs,
        "validation_passed": validation_passed,
        "validation_message": validation_message,
        "before_benchmark": before_bench,
        "after_benchmark": after_bench,
        "comparison": comparison,
        "status": "complete",
        "ai_provider": ai_provider,
    }
