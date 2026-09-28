"""Settings management endpoints."""
from fastapi import APIRouter
from app.schemas.schemas import SettingsUpdate, SettingsResponse
from app.core.config import settings
from app.providers.ai_provider import get_ai_provider

router = APIRouter(tags=["Settings"])

# In-memory settings override (persisted to DB in production)
_overrides: dict = {}


@router.get("/settings")
async def get_settings():
    provider = get_ai_provider()
    return {
        "cpu_tdp_watts": _overrides.get("cpu_tdp_watts", settings.DEFAULT_CPU_TDP_WATTS),
        "gpu_tdp_watts": _overrides.get("gpu_tdp_watts", settings.DEFAULT_GPU_TDP_WATTS),
        "grid_carbon_intensity": _overrides.get("grid_carbon_intensity", settings.DEFAULT_GRID_CARBON_INTENSITY),
        "pue": _overrides.get("pue", settings.DEFAULT_PUE),
        "cpu_utilization": _overrides.get("cpu_utilization", settings.DEFAULT_CPU_UTILIZATION),
        "benchmark_timeout": _overrides.get("benchmark_timeout", settings.BENCHMARK_TIMEOUT),
        "benchmark_runs": _overrides.get("benchmark_runs", settings.BENCHMARK_RUNS),
        "ai_provider_status": provider.name,
        "methodology_note": (
            "These are configurable prototype assumptions. "
            "CPU TDP, PUE, and grid carbon intensity vary significantly by hardware and region. "
            "Change these values to match your hardware environment for more relevant estimates."
        )
    }


@router.post("/settings")
async def update_settings(update: SettingsUpdate):
    for field, value in update.model_dump(exclude_none=True).items():
        _overrides[field] = value
    return {"status": "updated", "settings": _overrides}
