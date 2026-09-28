"""
Safe subprocess-based benchmark execution engine for GreenForge AI.
IMPORTANT: Never execute user code inside the main process.
"""
import subprocess
import tempfile
import os
import sys
import json
import time
import statistics
import platform
from typing import Optional, List, Dict, Any
from pathlib import Path
from app.core.config import settings


BENCHMARK_WRAPPER = """
import time
import tracemalloc
import json
import sys
import os
import gc

def _run_user_code():
    # BEGIN USER CODE
{code}
    # END USER CODE

gc.collect()
tracemalloc.start()
start_wall = time.perf_counter()
start_cpu = time.process_time()

try:
    _run_user_code()
    success = True
    error = None
except Exception as e:
    success = False
    error = str(e)

end_wall = time.perf_counter()
end_cpu = time.process_time()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

result = {{
    "success": success,
    "error": error,
    "wall_time": end_wall - start_wall,
    "cpu_time": end_cpu - start_cpu,
    "memory_current_kb": current / 1024,
    "memory_peak_kb": peak / 1024,
}}
print("GREENFORGE_RESULT:" + json.dumps(result))
"""


def run_benchmark(code: str, runs: int = 5, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute code in subprocess and collect benchmarks.
    Returns structured benchmark result.
    """
    wall_times = []
    cpu_times = []
    memory_peaks_mb = []
    errors = []
    output_sample = None

    # Indent user code for wrapper
    indented_code = "\n".join("    " + line for line in code.splitlines())
    wrapper_code = BENCHMARK_WRAPPER.format(code=indented_code)

    for run_idx in range(runs):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                script_path = os.path.join(tmpdir, "bench.py")
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(wrapper_code)

                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmpdir,
                )

                stdout = result.stdout
                stderr = result.stderr

                # Extract structured result
                for line in stdout.splitlines():
                    if line.startswith("GREENFORGE_RESULT:"):
                        try:
                            data = json.loads(line[len("GREENFORGE_RESULT:"):])
                            if data.get("success"):
                                wall_times.append(data["wall_time"])
                                cpu_times.append(data["cpu_time"])
                                memory_peaks_mb.append(data["memory_peak_kb"] / 1024)
                            else:
                                errors.append(data.get("error", "Unknown error"))
                            if output_sample is None:
                                other_lines = [l for l in stdout.splitlines()
                                               if not l.startswith("GREENFORGE_RESULT:")]
                                output_sample = "\n".join(other_lines[:10])
                        except json.JSONDecodeError:
                            errors.append("Failed to parse benchmark result")
                        break
                else:
                    # No structured result found
                    if result.returncode != 0:
                        errors.append(stderr[:500] if stderr else "Non-zero exit code")
                    else:
                        errors.append("No benchmark result marker found")

        except subprocess.TimeoutExpired:
            errors.append(f"Execution timed out after {timeout}s")
            break
        except Exception as e:
            errors.append(f"Execution error: {str(e)}")
            break

    if not wall_times:
        return {
            "success": False,
            "runs": runs,
            "mean_runtime": None,
            "min_runtime": None,
            "max_runtime": None,
            "median_runtime": None,
            "mean_memory_mb": None,
            "peak_memory_mb": None,
            "cpu_time": None,
            "output_sample": None,
            "error_message": "; ".join(set(errors))[:1000],
            "raw_results": []
        }

    return {
        "success": True,
        "runs": len(wall_times),
        "mean_runtime": round(statistics.mean(wall_times), 4),
        "min_runtime": round(min(wall_times), 4),
        "max_runtime": round(max(wall_times), 4),
        "median_runtime": round(statistics.median(wall_times), 4),
        "mean_memory_mb": round(statistics.mean(memory_peaks_mb), 2),
        "peak_memory_mb": round(max(memory_peaks_mb), 2),
        "cpu_time": round(statistics.mean(cpu_times), 4),
        "output_sample": (output_sample or "")[:2000],
        "error_message": None,
        "raw_results": [
            {"run": i + 1, "wall_time": t, "memory_mb": m}
            for i, (t, m) in enumerate(zip(wall_times, memory_peaks_mb))
        ]
    }


def compute_comparison(before: Dict, after: Dict) -> Dict:
    """Compute improvement metrics between two benchmark results."""
    result = {
        "runtime_reduction_pct": None,
        "memory_reduction_pct": None,
        "improvement_label": "No benchmark data available"
    }

    if before.get("mean_runtime") and after.get("mean_runtime"):
        rt_before = before["mean_runtime"]
        rt_after = after["mean_runtime"]
        if rt_before > 0:
            pct = ((rt_before - rt_after) / rt_before) * 100
            result["runtime_reduction_pct"] = round(pct, 1)

    if before.get("mean_memory_mb") and after.get("mean_memory_mb"):
        mem_before = before["mean_memory_mb"]
        mem_after = after["mean_memory_mb"]
        if mem_before > 0:
            pct = ((mem_before - mem_after) / mem_before) * 100
            result["memory_reduction_pct"] = round(pct, 1)

    rt_pct = result["runtime_reduction_pct"]
    mem_pct = result["memory_reduction_pct"]

    if rt_pct is not None and rt_pct > 0:
        result["improvement_label"] = f"Runtime reduced by {rt_pct:.1f}%"
        if mem_pct is not None and mem_pct > 0:
            result["improvement_label"] += f", memory reduced by {mem_pct:.1f}%"
    elif rt_pct is not None and rt_pct < 0:
        result["improvement_label"] = f"Optimized version is {abs(rt_pct):.1f}% slower — optimization not recommended"
    else:
        result["improvement_label"] = "Similar performance"

    return result
