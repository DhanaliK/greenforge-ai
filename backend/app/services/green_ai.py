"""
Green AI Lab — ML workload analysis and efficiency benchmarking.
"""
import time
import random
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Demo ML workloads (lightweight, runnable on student laptops)
DEMO_WORKLOADS = {
    "sklearn_baseline": {
        "id": "sklearn_baseline",
        "name": "Baseline Classifier (scikit-learn)",
        "description": "RandomForestClassifier with default settings on synthetic dataset",
        "framework": "scikit-learn",
        "category": "Classification",
        "code": """
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Non-batched: load and predict one at a time (inefficient pattern)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

results = []
for i in range(len(X_test)):
    pred = model.predict(X_test[i:i+1])
    results.append(pred[0])

accuracy = sum(r == y for r, y in zip(results, y_test)) / len(y_test)
print(f"Accuracy: {accuracy:.4f}")
"""
    },
    "sklearn_optimized": {
        "id": "sklearn_optimized",
        "name": "Optimized Classifier (batched inference)",
        "description": "Same RandomForestClassifier but with batched inference",
        "framework": "scikit-learn",
        "category": "Classification",
        "code": """
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Batched: predict all at once (efficient pattern)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
results = model.predict(X_test)

accuracy = sum(r == y for r, y in zip(results, y_test)) / len(y_test)
print(f"Accuracy: {accuracy:.4f}")
"""
    },
    "sklearn_small": {
        "id": "sklearn_small",
        "name": "Lightweight Classifier (DecisionTree)",
        "description": "Smaller, faster DecisionTree model for comparison",
        "framework": "scikit-learn",
        "category": "Classification",
        "code": """
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=10, random_state=42)
model.fit(X_train, y_train)
results = model.predict(X_test)

accuracy = sum(r == y for r, y in zip(results, y_test)) / len(y_test)
print(f"Accuracy: {accuracy:.4f}")
"""
    }
}


class MLWorkloadAnalyzer:
    """Analyzes ML workloads for efficiency patterns."""

    def analyze_workload(self, workload_id: str) -> Dict:
        """Run and analyze a demo ML workload."""
        if workload_id not in DEMO_WORKLOADS:
            return {"error": f"Workload '{workload_id}' not found"}

        workload = DEMO_WORKLOADS[workload_id]
        metrics = self._benchmark_workload(workload["code"])
        model_metrics = self._estimate_model_metrics(workload_id, metrics)

        # Analyze for inefficiency patterns
        from app.analyzers.code_analyzer import get_analyzer
        analyzer = get_analyzer("python")
        issues = analyzer.analyze(workload["code"])
        findings = [
            {
                "category": i.category,
                "title": i.title,
                "severity": i.severity,
                "explanation": i.explanation,
                "recommendation": i.recommendation,
            }
            for i in issues
        ]

        # Get AI recommendations
        from app.agents.orchestrator import GreenAIAgent
        agent = GreenAIAgent()
        ai_result = agent.analyze(model_metrics, workload["code"])

        findings.extend(ai_result.get("findings", []))

        # Score
        from app.sustainability.scoring import ScoringEngine
        scorer = ScoringEngine()
        score = scorer.calculate(findings, is_ml=True)

        # Sustainability estimate
        from app.sustainability.engine import SustainabilityEngine
        sus = SustainabilityEngine()
        sustainability = sus.estimate_from_runtime(
            metrics.get("mean_runtime", 1.0),
            label=workload["name"]
        ) if metrics.get("success") else {
            "label": "Benchmark failed",
            "methodology_note": "Run benchmark to generate estimate."
        }

        return {
            "workload_id": workload_id,
            "workload_name": workload["name"],
            "framework": workload["framework"],
            "metrics": model_metrics,
            "benchmark": metrics,
            "findings": findings,
            "recommendations": ai_result.get("recommendations", []),
            "greenforge_score": score,
            "sustainability": sustainability,
            "ai_provider": ai_result.get("ai_provider", "Local fallback")
        }

    def _benchmark_workload(self, code: str) -> Dict:
        """Run benchmark on ML workload."""
        from app.benchmarking.runner import run_benchmark
        from app.core.config import settings
        return run_benchmark(code, runs=3, timeout=settings.BENCHMARK_TIMEOUT)

    def _estimate_model_metrics(self, workload_id: str, benchmark: Dict) -> Dict:
        """Estimate model metrics based on workload type and benchmark results."""
        # Baseline metrics for demo workloads
        defaults = {
            "sklearn_baseline": {
                "model_name": "RandomForestClassifier (n=100)",
                "num_parameters": 100 * 50,  # rough estimate: 100 trees, ~50 nodes each
                "model_size_mb": 2.5,
                "accuracy": 0.92,
                "batch_size": 1,  # non-batched
                "framework": "scikit-learn",
            },
            "sklearn_optimized": {
                "model_name": "RandomForestClassifier (batched)",
                "num_parameters": 100 * 50,
                "model_size_mb": 2.5,
                "accuracy": 0.92,
                "batch_size": 200,  # full batch
                "framework": "scikit-learn",
            },
            "sklearn_small": {
                "model_name": "DecisionTreeClassifier",
                "num_parameters": 50,
                "model_size_mb": 0.1,
                "accuracy": 0.88,
                "batch_size": 200,
                "framework": "scikit-learn",
            }
        }

        base = defaults.get(workload_id, {
            "model_name": workload_id,
            "num_parameters": None,
            "model_size_mb": None,
            "accuracy": None,
            "batch_size": None,
            "framework": "scikit-learn",
        })

        # Add measured metrics
        if benchmark.get("success"):
            base["inference_latency_ms"] = round(benchmark["mean_runtime"] * 1000, 1)
            base["memory_mb"] = benchmark.get("peak_memory_mb", 0)

        return base

    def compare_workloads(self, workload_ids: List[str]) -> Dict:
        """Compare multiple workloads side by side."""
        results = {}
        for wid in workload_ids:
            results[wid] = self.analyze_workload(wid)
        return results

    def get_all_workloads(self) -> List[Dict]:
        return [
            {
                "id": wid,
                "name": w["name"],
                "description": w["description"],
                "framework": w["framework"],
                "category": w["category"],
            }
            for wid, w in DEMO_WORKLOADS.items()
        ]
