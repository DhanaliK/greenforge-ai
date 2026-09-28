"""
Sustainability estimation engine for GreenForge AI.
Computes modeled energy and carbon estimates from benchmark measurements.
All results are MODELED ESTIMATES unless marked as measured.
"""
from typing import Optional, Dict, Any
from app.core.config import settings


class SustainabilityEngine:
    """
    Translates benchmark measurements into modeled sustainability estimates.

    IMPORTANT: These are modeled estimates based on configurable assumptions.
    They do NOT represent validated real-world carbon measurements.
    """

    def __init__(
        self,
        cpu_tdp_watts: Optional[float] = None,
        gpu_tdp_watts: Optional[float] = None,
        grid_carbon_intensity: Optional[float] = None,
        pue: Optional[float] = None,
        cpu_utilization: Optional[float] = None
    ):
        self.cpu_tdp_watts = cpu_tdp_watts or settings.DEFAULT_CPU_TDP_WATTS
        self.gpu_tdp_watts = gpu_tdp_watts or settings.DEFAULT_GPU_TDP_WATTS
        self.grid_carbon_intensity = grid_carbon_intensity or settings.DEFAULT_GRID_CARBON_INTENSITY
        self.pue = pue or settings.DEFAULT_PUE
        self.cpu_utilization = cpu_utilization or settings.DEFAULT_CPU_UTILIZATION

    def estimate_from_runtime(
        self,
        runtime_seconds: float,
        cpu_time_seconds: Optional[float] = None,
        gpu_utilization_fraction: float = 0.0,
        label: str = "Workload"
    ) -> Dict[str, Any]:
        """
        Estimate energy and carbon from runtime and configuration.
        Returns a dict with all values clearly labeled as modeled estimates.
        """
        # Use CPU time if available, otherwise approximate from wall time
        effective_cpu_time = cpu_time_seconds if cpu_time_seconds else runtime_seconds

        # CPU energy: TDP * utilization fraction * time
        cpu_energy_wh = (
            self.cpu_tdp_watts
            * self.cpu_utilization
            * (effective_cpu_time / 3600)
        )

        # GPU energy (if applicable)
        gpu_energy_wh = (
            self.gpu_tdp_watts
            * gpu_utilization_fraction
            * (runtime_seconds / 3600)
        )

        # Total IT equipment energy
        it_energy_wh = cpu_energy_wh + gpu_energy_wh

        # Datacenter overhead via PUE
        total_energy_wh = it_energy_wh * self.pue

        # Carbon equivalent
        # grid_carbon_intensity is in gCO2e/kWh
        carbon_gco2e = total_energy_wh * (self.grid_carbon_intensity / 1000)

        return {
            "label": "Modeled estimate",
            "runtime_seconds": round(runtime_seconds, 4),
            "cpu_time_seconds": round(effective_cpu_time, 4) if cpu_time_seconds else None,
            "estimated_energy_wh": round(total_energy_wh, 8),
            "estimated_carbon_gco2e": round(carbon_gco2e, 8),
            "assumptions": {
                "cpu_tdp_watts": self.cpu_tdp_watts,
                "gpu_tdp_watts": self.gpu_tdp_watts,
                "cpu_utilization_fraction": self.cpu_utilization,
                "pue": self.pue,
                "grid_carbon_intensity_gco2_per_kwh": self.grid_carbon_intensity,
                "gpu_utilization_fraction": gpu_utilization_fraction,
            },
            "methodology_note": (
                "Modeled estimate — computed from benchmark runtime and configurable assumptions "
                "about CPU TDP, utilization, PUE, and grid carbon intensity. "
                "These values do NOT represent validated real-world energy or carbon measurements. "
                "Source-level analysis alone cannot precisely predict real-world environmental impact."
            )
        }

    def compare_estimates(self, before: Dict, after: Dict) -> Dict:
        """Compare two sustainability estimates and compute reduction."""
        e_before = before.get("estimated_energy_wh", 0) or 0
        e_after = after.get("estimated_energy_wh", 0) or 0
        c_before = before.get("estimated_carbon_gco2e", 0) or 0
        c_after = after.get("estimated_carbon_gco2e", 0) or 0

        energy_reduction_pct = None
        carbon_reduction_pct = None

        if e_before > 0:
            energy_reduction_pct = round(((e_before - e_after) / e_before) * 100, 1)
        if c_before > 0:
            carbon_reduction_pct = round(((c_before - c_after) / c_before) * 100, 1)

        return {
            "energy_before_wh": e_before,
            "energy_after_wh": e_after,
            "carbon_before_gco2e": c_before,
            "carbon_after_gco2e": c_after,
            "energy_reduction_pct": energy_reduction_pct,
            "carbon_reduction_pct": carbon_reduction_pct,
            "label": "Modeled sustainability impact comparison",
            "note": (
                "These are modeled estimates based on benchmark runtimes and configured hardware assumptions. "
                "Do not treat as validated carbon reduction claims."
            )
        }
