"""ML analysis / Green AI Lab endpoints."""
import logging
from fastapi import APIRouter, HTTPException
from app.services.green_ai import MLWorkloadAnalyzer

router = APIRouter(tags=["Green AI"])
logger = logging.getLogger(__name__)
analyzer = MLWorkloadAnalyzer()


@router.get("/ml/workloads")
async def list_workloads():
    """List available demo ML workloads."""
    return {"workloads": analyzer.get_all_workloads()}


@router.post("/ml/analyze/{workload_id}")
async def analyze_ml_workload(workload_id: str):
    """Analyze a demo ML workload."""
    try:
        result = analyzer.analyze_workload(workload_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ML analysis failed: {str(e)[:200]}")


@router.post("/ml/compare")
async def compare_workloads(workload_ids: list[str]):
    """Compare multiple ML workloads."""
    if not workload_ids:
        raise HTTPException(status_code=400, detail="Provide at least one workload ID")
    try:
        result = analyzer.compare_workloads(workload_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/ml")
async def analyze_ml(request: dict):
    """Analyze ML workload (generic endpoint)."""
    workload_id = request.get("workload_id")
    if not workload_id:
        raise HTTPException(status_code=400, detail="workload_id required")
    return await analyze_ml_workload(workload_id)
