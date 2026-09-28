"""
Agentic orchestration pipeline for GreenForge AI.
Coordinates Code Auditor, Complexity Analyst, Sustainability Analyst,
Optimization Agent, Benchmark Validator, and Report Generator agents.
"""
import logging
from typing import List, Dict, Any, Optional
from app.analyzers.code_analyzer import get_analyzer
from app.analyzers.complexity_analyzer import ComplexityAnalyzer
from app.sustainability.engine import SustainabilityEngine
from app.sustainability.scoring import ScoringEngine
from app.providers.ai_provider import get_ai_provider
from app.benchmarking.runner import run_benchmark, compute_comparison

logger = logging.getLogger(__name__)


class CodeAuditorAgent:
    """Inspects source code and produces structured findings."""

    def run(self, code: str, language: str) -> List[Dict]:
        analyzer = get_analyzer(language)
        issues = analyzer.analyze(code)
        return [
            {
                "issue_id": i.issue_id,
                "severity": i.severity,
                "category": i.category,
                "title": i.title,
                "explanation": i.explanation,
                "evidence": i.evidence,
                "line_start": i.line_start,
                "line_end": i.line_end,
                "estimated_complexity": i.estimated_complexity,
                "recommendation": i.recommendation,
                "confidence": i.confidence,
                "is_static": i.is_static,
            }
            for i in issues
        ]


class ComplexityAnalystAgent:
    """Analyzes code complexity and provides Big-O heuristics."""

    def run(self, code: str) -> Dict:
        analyzer = ComplexityAnalyzer()
        return analyzer.analyze(code)


class SustainabilityAnalystAgent:
    """Estimates sustainability impact from benchmark data."""

    def run(
        self,
        runtime_seconds: Optional[float],
        cpu_time: Optional[float] = None,
        label: str = "Analysis"
    ) -> Dict:
        engine = SustainabilityEngine()
        if runtime_seconds:
            return engine.estimate_from_runtime(runtime_seconds, cpu_time, label=label)
        return {
            "label": "Modeled estimate (no benchmark data)",
            "runtime_seconds": None,
            "cpu_time_seconds": None,
            "estimated_energy_wh": None,
            "estimated_carbon_gco2e": None,
            "assumptions": {
                "cpu_tdp_watts": engine.cpu_tdp_watts,
                "grid_carbon_intensity_gco2_per_kwh": engine.grid_carbon_intensity,
                "pue": engine.pue,
            },
            "methodology_note": (
                "No benchmark data available. Configure and run a benchmark to generate "
                "runtime-based sustainability estimates."
            )
        }


class OptimizationAgent:
    """
    Generates optimized code alternatives.
    Uses AI provider for reasoning + template-based fallback.
    """

    def run(self, code: str, findings: List[Dict], language: str = "python") -> Dict:
        provider = get_ai_provider()

        # Build a focused prompt
        top_issues = sorted(findings, key=lambda f: {
            "Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Informational": 4
        }.get(f.get("severity", "Informational"), 5))[:3]

        issues_text = "\n".join(
            f"- [{f['severity']}] {f['title']}: {f['explanation']}"
            for f in top_issues
        )

        prompt = (
            f"You are GreenForge AI's Optimization Agent. Your task is to produce an optimized version "
            f"of the following {language} code based on the detected issues.\n\n"
            f"DETECTED ISSUES:\n{issues_text}\n\n"
            f"ORIGINAL CODE:\n```{language}\n{code}\n```\n\n"
            f"Instructions:\n"
            f"1. Produce the complete optimized code that addresses the highest-severity issues.\n"
            f"2. Preserve the original functionality and output correctness.\n"
            f"3. Add a brief comment explaining each key optimization.\n"
            f"4. Only optimize what is clearly beneficial — do not over-engineer.\n\n"
            f"Respond with:\n"
            f"OPTIMIZED_CODE:\n<complete code here>\n\n"
            f"EXPLANATION:\n<what was changed and why>\n\n"
            f"TRADE_OFFS:\n<any trade-offs introduced>"
        )

        try:
            response = provider.generate(prompt, max_tokens=1200)
        except Exception as e:
            logger.error(f"Optimization agent error: {e}")
            return self._fallback_optimize(code, findings, language)

        # Parse structured response
        optimized_code = code
        explanation = ""
        trade_offs = ""

        if "OPTIMIZED_CODE:" in response:
            parts = response.split("OPTIMIZED_CODE:")
            rest = parts[1] if len(parts) > 1 else ""
            # Extract code block
            if "```" in rest:
                code_parts = rest.split("```")
                if len(code_parts) >= 2:
                    code_content = code_parts[1]
                    if code_content.startswith(language):
                        code_content = code_content[len(language):]
                    optimized_code = code_content.strip()
            else:
                exp_split = rest.split("EXPLANATION:")
                optimized_code = exp_split[0].strip()

            if "EXPLANATION:" in response:
                exp_parts = response.split("EXPLANATION:")
                rest2 = exp_parts[1] if len(exp_parts) > 1 else ""
                trade_split = rest2.split("TRADE_OFFS:")
                explanation = trade_split[0].strip()
                if len(trade_split) > 1:
                    trade_offs = trade_split[1].strip()

        if not optimized_code or optimized_code == code:
            return self._fallback_optimize(code, findings, language)

        return {
            "optimized_code": optimized_code,
            "explanation": explanation or "AI-generated optimization",
            "trade_offs": trade_offs or "Review carefully before deploying",
            "ai_provider": provider.name
        }

    def _fallback_optimize(self, code: str, findings: List[Dict], language: str) -> Dict:
        """Template-based optimization when AI is unavailable."""
        import ast
        import re

        optimized = code
        explanations = []

        # Pattern 1: Convert list() wrapping in for-loops
        optimized = re.sub(r'for\s+(\w+)\s+in\s+list\(', r'for \1 in (', optimized)
        if optimized != code:
            explanations.append("Removed unnecessary list() wrapping in for-loops (saves O(n) allocation).")

        # Pattern 2: Add a general optimization comment
        if not explanations:
            # Add caching hint for repeated calls
            lines = code.splitlines()
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if 'for ' in line and ':' in line:
                    # Add caching hint comment
                    indent = len(line) - len(line.lstrip())
                    pass
            optimized = "\n".join(new_lines)

        explanation = (
            "Local optimization analysis: " + " ".join(explanations) if explanations
            else (
                "Configure IBM Granite or review findings manually for AI-powered optimization. "
                "Primary recommendation: address the highest-severity finding first, "
                "then benchmark before and after to confirm improvement."
            )
        )

        return {
            "optimized_code": optimized,
            "explanation": explanation,
            "trade_offs": "Fallback optimization — configure IBM Granite for AI-powered code generation.",
            "ai_provider": "Local fallback"
        }


class BenchmarkValidatorAgent:
    """Validates optimization by running benchmarks on both versions."""

    def run(self, original_code: str, optimized_code: str, runs: int = 5) -> Dict:
        from app.core.config import settings
        timeout = settings.BENCHMARK_TIMEOUT

        logger.info("Benchmarking original code...")
        before = run_benchmark(original_code, runs=runs, timeout=timeout)

        logger.info("Benchmarking optimized code...")
        after = run_benchmark(optimized_code, runs=runs, timeout=timeout)

        comparison = compute_comparison(before, after)

        # Reject optimization if it's slower
        accept = True
        if (before.get("mean_runtime") and after.get("mean_runtime")
                and after["mean_runtime"] > before["mean_runtime"] * 1.1):
            accept = False
            comparison["improvement_label"] = (
                f"Optimized version is slower ({after['mean_runtime']:.3f}s vs {before['mean_runtime']:.3f}s). "
                "Optimization not recommended."
            )

        return {
            "before": before,
            "after": after,
            "comparison": comparison,
            "accepted": accept
        }


class GreenAIAgent:
    """Analyzes ML workloads and generates efficiency recommendations."""

    def analyze(self, metrics: Dict, code: Optional[str] = None) -> Dict:
        provider = get_ai_provider()
        findings = []
        recommendations = []

        # Rule-based ML analysis
        if metrics.get("num_parameters", 0) > 10_000_000:
            findings.append({
                "category": "ML Model Size",
                "title": "Large model parameter count",
                "severity": "Medium",
                "explanation": (
                    f"The model has {metrics['num_parameters']:,} parameters. "
                    "Large models increase inference latency, memory usage, and energy consumption."
                ),
                "recommendation": "Consider model distillation, pruning, or using a smaller architecture."
            })
            recommendations.append("Explore model compression: quantization, pruning, or knowledge distillation.")

        if metrics.get("inference_latency_ms", 0) > 100:
            findings.append({
                "category": "Inference Latency",
                "title": "High inference latency",
                "severity": "High",
                "explanation": (
                    f"Inference latency of {metrics['inference_latency_ms']:.1f}ms is above 100ms threshold."
                ),
                "recommendation": "Optimize inference pipeline: batching, quantization, or hardware acceleration."
            })
            recommendations.append("Batch inference requests to improve throughput.")

        if metrics.get("memory_mb", 0) > 200:
            findings.append({
                "category": "Memory Usage",
                "title": "High memory consumption",
                "severity": "Medium",
                "explanation": (
                    f"Model uses {metrics['memory_mb']:.0f}MB. Large memory footprint limits deployment options "
                    "and increases infrastructure costs."
                ),
                "recommendation": "Use mixed-precision (float16) or quantized models to reduce memory footprint."
            })

        if not recommendations:
            recommendations.append("Model appears reasonably efficient for its task.")

        return {
            "findings": findings,
            "recommendations": recommendations,
            "ai_provider": provider.name
        }


class ReportGeneratorAgent:
    """Generates comprehensive sustainability reports."""

    def generate(
        self,
        analysis_data: Dict,
        benchmark_data: Optional[Dict] = None,
        ml_data: Optional[Dict] = None
    ) -> Dict:
        provider = get_ai_provider()

        findings = analysis_data.get("findings", [])
        score = analysis_data.get("score", {})
        sustainability = analysis_data.get("sustainability", {})

        # Generate executive summary
        critical_count = sum(1 for f in findings if f.get("severity") == "Critical")
        high_count = sum(1 for f in findings if f.get("severity") == "High")

        prompt = (
            f"Generate a professional executive summary for a GreenForge AI sustainability analysis report.\n\n"
            f"Analysis summary:\n"
            f"- Total issues detected: {len(findings)}\n"
            f"- Critical: {critical_count}, High: {high_count}\n"
            f"- GreenForge Score: {score.get('total', 'N/A')}/100\n"
            f"- Language: {analysis_data.get('language', 'Python')}\n\n"
            f"Write a 3-4 sentence professional executive summary suitable for a technical report. "
            f"Be factual and avoid overclaiming. Mention that sustainability estimates are modeled."
        )

        try:
            executive_summary = provider.generate(prompt, max_tokens=300)
        except Exception:
            s = score.get("total", 0)
            executive_summary = (
                f"GreenForge AI analysis identified {len(findings)} computational efficiency issues "
                f"({critical_count} critical, {high_count} high severity) in the analyzed code. "
                f"The GreenForge Score is {s:.0f}/100, reflecting the current efficiency profile. "
                f"Sustainability impact estimates are modeled from benchmark measurements and "
                f"configurable hardware assumptions — not validated environmental measurements."
            )

        report = {
            "title": "GreenForge AI Sustainability Report",
            "executive_summary": executive_summary,
            "project_overview": {
                "language": analysis_data.get("language", "Python"),
                "lines_of_code": analysis_data.get("lines_of_code", 0),
                "analysis_timestamp": analysis_data.get("timestamp", ""),
            },
            "code_findings": {
                "total": len(findings),
                "by_severity": {
                    "Critical": critical_count,
                    "High": high_count,
                    "Medium": sum(1 for f in findings if f.get("severity") == "Medium"),
                    "Low": sum(1 for f in findings if f.get("severity") == "Low"),
                },
                "findings": findings
            },
            "complexity": analysis_data.get("complexity", {}),
            "greenforge_score": score,
            "benchmark": benchmark_data or {},
            "sustainability": sustainability,
            "ml_analysis": ml_data or {},
            "responsible_ai_note": (
                "All sustainability estimates in this report are modeled from benchmark measurements "
                "and configurable hardware/grid assumptions. They are indicative estimates, not validated "
                "environmental measurements. GreenForge AI does not claim exact carbon reduction. "
                "The GreenForge Score is a prototype indicator, not an industry certification."
            ),
            "sdg_alignment": {
                "primary": "SDG 12 — Responsible Consumption and Production",
                "secondary": ["SDG 13 — Climate Action", "SDG 9 — Industry, Innovation and Infrastructure"]
            },
            "ai_provider": provider.name
        }

        return report


class GreenForgeOrchestrator:
    """
    Main orchestration pipeline for GreenForge AI.
    Coordinates all agents in sequence.
    """

    def __init__(self):
        self.auditor = CodeAuditorAgent()
        self.complexity_analyst = ComplexityAnalystAgent()
        self.sustainability_analyst = SustainabilityAnalystAgent()
        self.scoring_engine = ScoringEngine()
        self.optimization_agent = OptimizationAgent()
        self.benchmark_validator = BenchmarkValidatorAgent()
        self.report_generator = ReportGeneratorAgent()

    def analyze_code(self, code: str, language: str = "python") -> Dict:
        """Run full analysis pipeline."""
        import datetime

        logger.info(f"Starting GreenForge analysis for {language} code ({len(code)} chars)")

        # Step 1: Code Audit
        findings = self.auditor.run(code, language)

        # Step 2: Complexity Analysis
        complexity = self.complexity_analyst.run(code)

        # Step 3: Sustainability estimate (no benchmark yet)
        sustainability = self.sustainability_analyst.run(None)

        # Step 4: Score
        score = self.scoring_engine.calculate(findings, complexity)

        return {
            "language": language,
            "lines_of_code": len(code.splitlines()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "findings": findings,
            "complexity": complexity,
            "sustainability": sustainability,
            "score": score
        }
