"""
GreenForge Score calculation engine.
Produces a transparent 0-100 score based on analysis results.
"""
from typing import Dict, Any, List, Optional


SCORE_WEIGHTS = {
    "algorithmic_efficiency": 0.20,
    "runtime_efficiency": 0.20,
    "memory_efficiency": 0.15,
    "io_efficiency": 0.10,
    "ml_efficiency": 0.10,
    "optimization_potential": 0.15,
    "benchmark_improvement": 0.10,
}

METHODOLOGY_NOTE = """
GreenForge Score (0–100) is a prototype indicator computed from weighted sub-scores:

• Algorithmic Efficiency (20%): Penalizes nested loops, high cyclomatic complexity,
  and polynomial-complexity heuristics detected via static analysis.
• Runtime Efficiency (20%): Based on benchmark runtime relative to baseline.
  If no benchmark is available, estimated from complexity findings.
• Memory Efficiency (15%): Based on measured memory usage and memory-related findings.
• I/O Efficiency (10%): Penalizes repeated file/network/database I/O patterns.
• ML Efficiency (10%): Penalizes model loading in loops, non-batched inference, etc.
• Optimization Potential (15%): Inverse of the number and severity of findings.
• Benchmark Improvement (10%): Score improvement from before→after optimization.

Each dimension is normalized 0–100. The final score is a weighted average.
A higher score indicates fewer detected efficiency concerns at analysis time.

This score is a prototype indicator, not an industry certification or scientifically
validated sustainability metric. It is intended to guide developer attention.
"""


class ScoringEngine:

    def calculate(
        self,
        findings: List[Dict],
        complexity_report: Optional[Dict] = None,
        benchmark_before: Optional[Dict] = None,
        benchmark_after: Optional[Dict] = None,
        is_ml: bool = False
    ) -> Dict[str, Any]:
        """Calculate GreenForge Score from analysis results."""

        algo = self._algorithmic_score(findings, complexity_report)
        runtime = self._runtime_score(benchmark_before, findings)
        memory = self._memory_score(benchmark_before, findings)
        io = self._io_score(findings)
        ml = self._ml_score(findings) if is_ml else 80.0
        opt_potential = self._optimization_potential_score(findings)
        bench_improvement = self._benchmark_improvement_score(benchmark_before, benchmark_after)

        total = (
            algo * SCORE_WEIGHTS["algorithmic_efficiency"]
            + runtime * SCORE_WEIGHTS["runtime_efficiency"]
            + memory * SCORE_WEIGHTS["memory_efficiency"]
            + io * SCORE_WEIGHTS["io_efficiency"]
            + ml * SCORE_WEIGHTS["ml_efficiency"]
            + opt_potential * SCORE_WEIGHTS["optimization_potential"]
            + bench_improvement * SCORE_WEIGHTS["benchmark_improvement"]
        )

        return {
            "total": round(total, 1),
            "algorithmic_efficiency": round(algo, 1),
            "runtime_efficiency": round(runtime, 1),
            "memory_efficiency": round(memory, 1),
            "io_efficiency": round(io, 1),
            "ml_efficiency": round(ml, 1),
            "optimization_potential": round(opt_potential, 1),
            "benchmark_improvement": round(bench_improvement, 1),
            "methodology_note": METHODOLOGY_NOTE.strip(),
        }

    def _algorithmic_score(self, findings: List[Dict], complexity: Optional[Dict]) -> float:
        score = 100.0
        # Penalize per severity
        severity_penalty = {"Critical": 20, "High": 10, "Medium": 5, "Low": 2, "Informational": 0}
        algo_cats = {"Algorithmic Complexity", "Repeated Computation"}
        for f in findings:
            if f.get("category") in algo_cats:
                score -= severity_penalty.get(f.get("severity", "Low"), 0)

        # Complexity-based penalty
        if complexity:
            max_depth = complexity.get("max_loop_depth", 0)
            if max_depth >= 3:
                score -= 20
            elif max_depth == 2:
                score -= 10
            elif max_depth == 1:
                score -= 0  # no penalty for simple loops

        return max(0.0, min(100.0, score))

    def _runtime_score(self, benchmark: Optional[Dict], findings: List[Dict]) -> float:
        if benchmark and benchmark.get("mean_runtime") is not None:
            rt = benchmark["mean_runtime"]
            # Score inversely related to runtime (prototype heuristic)
            if rt < 0.1:
                return 95.0
            elif rt < 0.5:
                return 85.0
            elif rt < 1.0:
                return 75.0
            elif rt < 5.0:
                return 60.0
            elif rt < 10.0:
                return 45.0
            else:
                return 30.0
        # Estimate from findings if no benchmark
        score = 80.0
        severity_penalty = {"Critical": 15, "High": 8, "Medium": 3, "Low": 1}
        for f in findings:
            score -= severity_penalty.get(f.get("severity", "Low"), 0)
        return max(0.0, min(100.0, score))

    def _memory_score(self, benchmark: Optional[Dict], findings: List[Dict]) -> float:
        score = 85.0
        if benchmark and benchmark.get("peak_memory_mb") is not None:
            mem = benchmark["peak_memory_mb"]
            if mem < 10:
                score = 95.0
            elif mem < 50:
                score = 85.0
            elif mem < 200:
                score = 70.0
            elif mem < 500:
                score = 55.0
            else:
                score = 35.0

        mem_cats = {"Unnecessary Memory Allocation", "Excessive Memory Allocation"}
        for f in findings:
            if f.get("category") in mem_cats:
                score -= 5 if f.get("severity") in ("High", "Critical") else 2
        return max(0.0, min(100.0, score))

    def _io_score(self, findings: List[Dict]) -> float:
        score = 90.0
        io_cats = {"Repeated I/O"}
        for f in findings:
            if f.get("category") in io_cats:
                sev = f.get("severity", "Low")
                score -= 15 if sev == "Critical" else 10 if sev == "High" else 5
        return max(0.0, min(100.0, score))

    def _ml_score(self, findings: List[Dict]) -> float:
        score = 85.0
        for f in findings:
            if f.get("category") == "ML Efficiency":
                sev = f.get("severity", "Low")
                score -= 20 if sev == "Critical" else 12 if sev == "High" else 5
        return max(0.0, min(100.0, score))

    def _optimization_potential_score(self, findings: List[Dict]) -> float:
        """Score representing optimization potential: fewer high-severity findings = higher score."""
        score = 100.0
        for f in findings:
            sev = f.get("severity", "Informational")
            score -= {"Critical": 15, "High": 8, "Medium": 4, "Low": 1, "Informational": 0}.get(sev, 0)
        return max(0.0, min(100.0, score))

    def _benchmark_improvement_score(self, before: Optional[Dict], after: Optional[Dict]) -> float:
        """Score based on benchmark improvement."""
        if not before or not after:
            return 70.0  # neutral if no benchmark comparison
        rt_before = before.get("mean_runtime")
        rt_after = after.get("mean_runtime")
        if rt_before and rt_after and rt_before > 0:
            reduction = (rt_before - rt_after) / rt_before
            if reduction > 0.5:
                return 95.0
            elif reduction > 0.3:
                return 85.0
            elif reduction > 0.1:
                return 75.0
            elif reduction > 0:
                return 65.0
            else:
                return 50.0
        return 70.0
