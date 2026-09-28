"""Demo projects and sample workflows."""
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Demo"])

DEMO_PROJECTS = {
    "nested_loop": {
        "id": "nested_loop",
        "name": "Nested Loop Optimization",
        "description": "Demonstrates O(n²) → O(n) optimization using dict/set lookup",
        "language": "python",
        "category": "Algorithmic Complexity",
        "code": '''# GreenForge AI Demo: Nested Loop Optimization
# This code demonstrates an O(n²) pattern that can be optimized

import time

def find_duplicates_slow(data):
    """O(n²) approach - checks every pair"""
    duplicates = []
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            if data[i] == data[j] and data[i] not in duplicates:
                duplicates.append(data[i])
    return duplicates

def find_common_elements_slow(list_a, list_b):
    """O(n²) approach - nested iteration"""
    common = []
    for a in list_a:
        for b in list_b:
            if a == b and a not in common:
                common.append(a)
    return common

# Test with sample data
data = list(range(500)) + list(range(250))
result = find_duplicates_slow(data[:100])

list_a = list(range(1, 300))
list_b = list(range(200, 500))
common = find_common_elements_slow(list_a[:100], list_b[:100])

print(f"Duplicates found: {len(result)}")
print(f"Common elements: {len(common)}")
''',
        "optimized_code": '''# GreenForge AI Demo: Nested Loop Optimization - OPTIMIZED
# O(n) approach using set/dict for O(1) lookups

def find_duplicates_fast(data):
    """O(n) approach - use dict to track seen items"""
    seen = {}
    duplicates = []
    for item in data:
        if item in seen:
            if seen[item] == 1:  # Only add once
                duplicates.append(item)
            seen[item] += 1
        else:
            seen[item] = 1
    return duplicates

def find_common_elements_fast(list_a, list_b):
    """O(n) approach - convert one list to set for O(1) lookups"""
    set_b = set(list_b)  # Build set once: O(m)
    return list(set(a for a in list_a if a in set_b))  # O(n) lookup

# Test with sample data
data = list(range(500)) + list(range(250))
result = find_duplicates_fast(data[:100])

list_a = list(range(1, 300))
list_b = list(range(200, 500))
common = find_common_elements_fast(list_a[:100], list_b[:100])

print(f"Duplicates found: {len(result)}")
print(f"Common elements: {len(common)}")
''',
        "expected_issues": ["Nested O(n²) loops", "List membership test inside loop"],
        "expected_optimization": "Replace nested loops with set-based lookup"
    },
    "repeated_io": {
        "id": "repeated_io",
        "name": "Repeated Database/API Calls",
        "description": "Demonstrates N+1 query pattern and batching optimization",
        "language": "python",
        "category": "Repeated I/O",
        "code": '''# GreenForge AI Demo: Repeated I/O Pattern
# Simulates N+1 database query anti-pattern

import time

class MockDB:
    """Simulates database with artificial latency"""
    def __init__(self):
        self._data = {i: {"id": i, "name": f"User_{i}", "score": i * 1.5}
                      for i in range(1, 101)}
    
    def get_user(self, user_id):
        """Single user lookup - simulates DB query"""
        time.sleep(0.001)  # Simulate 1ms DB latency
        return self._data.get(user_id)
    
    def get_users_batch(self, user_ids):
        """Batch lookup - one query for all users"""
        time.sleep(0.002)  # Slightly more but far fewer calls
        return [self._data[uid] for uid in user_ids if uid in self._data]

db = MockDB()
user_ids = list(range(1, 51))  # 50 users

# Inefficient: N+1 pattern - one query per user
results = []
for uid in user_ids:
    user = db.get_user(uid)  # Individual call per iteration
    if user:
        results.append(user)

total_score = sum(r["score"] for r in results)
print(f"Processed {len(results)} users, total score: {total_score:.1f}")
''',
        "optimized_code": '''# GreenForge AI Demo: Repeated I/O - OPTIMIZED
# Batch all database queries into a single call

import time

class MockDB:
    """Simulates database with artificial latency"""
    def __init__(self):
        self._data = {i: {"id": i, "name": f"User_{i}", "score": i * 1.5}
                      for i in range(1, 101)}
    
    def get_user(self, user_id):
        time.sleep(0.001)
        return self._data.get(user_id)
    
    def get_users_batch(self, user_ids):
        time.sleep(0.002)  # One call instead of N calls
        return [self._data[uid] for uid in user_ids if uid in self._data]

db = MockDB()
user_ids = list(range(1, 51))

# Optimized: batch all queries in one call
results = db.get_users_batch(user_ids)  # Single batch call

total_score = sum(r["score"] for r in results)
print(f"Processed {len(results)} users, total score: {total_score:.1f}")
''',
        "expected_issues": ["Function call inside loop", "Repeated I/O per iteration"],
        "expected_optimization": "Batch all queries into a single call"
    },
    "memory_heavy": {
        "id": "memory_heavy",
        "name": "Memory-Heavy Data Processing",
        "description": "Demonstrates unnecessary list materialization vs generator",
        "language": "python",
        "category": "Memory Efficiency",
        "code": '''# GreenForge AI Demo: Memory-Heavy Data Processing

def process_records_inefficient(n=50000):
    """Loads all data into memory before processing"""
    # Creates full list in memory
    all_records = list(range(n))
    
    # Multiple intermediate lists
    filtered = list(filter(lambda x: x % 2 == 0, all_records))
    squared = list(map(lambda x: x ** 2, filtered))
    result = list(filter(lambda x: x < 1000000, squared))
    
    return sum(result)

total = process_records_inefficient()
print(f"Total: {total}")
''',
        "optimized_code": '''# GreenForge AI Demo: Memory-Heavy Data Processing - OPTIMIZED

def process_records_efficient(n=50000):
    """Uses generators to process lazily without materializing"""
    # Generator pipeline - no intermediate lists
    records = range(n)
    filtered = (x for x in records if x % 2 == 0)
    squared = (x ** 2 for x in filtered)
    result = (x for x in squared if x < 1000000)
    
    return sum(result)

total = process_records_efficient()
print(f"Total: {total}")
''',
        "expected_issues": ["Unnecessary list materialization", "Excessive memory allocation"],
        "expected_optimization": "Replace intermediate lists with generators"
    },
    "ml_inference": {
        "id": "ml_inference",
        "name": "ML Inference Efficiency",
        "description": "Single-sample vs batched ML inference",
        "language": "python",
        "category": "ML Efficiency",
        "code": '''# GreenForge AI Demo: ML Inference Efficiency
# Demonstrates single-sample inference anti-pattern

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=500, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

# Inefficient: single-sample inference in loop
predictions = []
for i in range(len(X_test)):
    pred = model.predict(X_test[i:i+1])  # One sample at a time
    predictions.append(pred[0])

accuracy = sum(p == t for p, t in zip(predictions, y_test)) / len(y_test)
print(f"Accuracy: {accuracy:.4f}, Samples: {len(predictions)}")
''',
        "optimized_code": '''# GreenForge AI Demo: ML Inference - OPTIMIZED
# Batched inference: process all samples at once

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=500, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

# Optimized: batch all samples in a single predict call
predictions = model.predict(X_test)  # Single batched call

accuracy = sum(p == t for p, t in zip(predictions, y_test)) / len(y_test)
print(f"Accuracy: {accuracy:.4f}, Samples: {len(predictions)}")
''',
        "expected_issues": ["Single-sample inference in loop", "ML Efficiency"],
        "expected_optimization": "Batch all samples into a single predict call"
    },
    "string_concat": {
        "id": "string_concat",
        "name": "String Concatenation Pattern",
        "description": "Demonstrates string += in loop vs join",
        "language": "python",
        "category": "String Operations",
        "code": '''# GreenForge AI Demo: String Concatenation
# Demonstrates O(n²) string concatenation

def build_report_slow(items):
    """Inefficient: builds string with += (creates new string each time)"""
    report = ""
    for item in items:
        report += f"Item: {item}\\n"  # Creates new string object each iteration
    return report

items = [f"record_{i}" for i in range(5000)]
result = build_report_slow(items)
print(f"Report length: {len(result)} chars")
''',
        "optimized_code": '''# GreenForge AI Demo: String Concatenation - OPTIMIZED
# Use list + join for O(n) string building

def build_report_fast(items):
    """Efficient: collect parts, join once at the end"""
    parts = []
    for item in items:
        parts.append(f"Item: {item}\\n")
    return "".join(parts)  # Single join: O(n)

items = [f"record_{i}" for i in range(5000)]
result = build_report_fast(items)
print(f"Report length: {len(result)} chars")
''',
        "expected_issues": ["String concatenation in loop"],
        "expected_optimization": "Use list.append + ''.join()"
    }
}


@router.get("/demo/projects")
async def list_demo_projects():
    """List available demo projects."""
    return {
        "projects": [
            {
                "id": k,
                "name": v["name"],
                "description": v["description"],
                "language": v["language"],
                "category": v["category"],
                "expected_issues": v["expected_issues"],
            }
            for k, v in DEMO_PROJECTS.items()
        ]
    }


@router.get("/demo/projects/{project_id}")
async def get_demo_project(project_id: str):
    """Get a specific demo project."""
    if project_id not in DEMO_PROJECTS:
        raise HTTPException(status_code=404, detail=f"Demo project '{project_id}' not found")
    return DEMO_PROJECTS[project_id]


@router.post("/demo/run/{project_id}")
async def run_demo(project_id: str, include_optimization: bool = True):
    """Run a complete demo workflow: analyze + benchmark + optimize."""
    if project_id not in DEMO_PROJECTS:
        raise HTTPException(status_code=404, detail=f"Demo project '{project_id}' not found")

    project = DEMO_PROJECTS[project_id]
    code = project["code"]
    language = project.get("language", "python")

    # Step 1: Analyze
    from app.agents.orchestrator import GreenForgeOrchestrator
    orch = GreenForgeOrchestrator()
    analysis = orch.analyze_code(code, language)

    result = {
        "project": project_id,
        "name": project["name"],
        "analysis": analysis,
        "benchmark": None,
        "optimization": None,
    }

    # Step 2: Benchmark original
    from app.benchmarking.runner import run_benchmark
    from app.core.config import settings
    bench = run_benchmark(code, runs=3, timeout=settings.BENCHMARK_TIMEOUT)
    result["benchmark"] = bench

    # Step 3: Optimize and benchmark if optimized code exists
    if include_optimization and project.get("optimized_code"):
        optimized_code = project["optimized_code"]
        from app.agents.orchestrator import BenchmarkValidatorAgent
        from app.sustainability.engine import SustainabilityEngine

        validator = BenchmarkValidatorAgent()
        bench_comparison = validator.run(code, optimized_code, runs=3)

        sus = SustainabilityEngine()
        before_sus = None
        after_sus = None
        if bench_comparison["before"].get("mean_runtime"):
            before_sus = sus.estimate_from_runtime(bench_comparison["before"]["mean_runtime"])
        if bench_comparison["after"].get("mean_runtime"):
            after_sus = sus.estimate_from_runtime(bench_comparison["after"]["mean_runtime"])

        result["optimization"] = {
            "original_code": code,
            "optimized_code": optimized_code,
            "explanation": project.get("expected_optimization", ""),
            "before_benchmark": bench_comparison["before"],
            "after_benchmark": bench_comparison["after"],
            "comparison": bench_comparison["comparison"],
            "sustainability_before": before_sus,
            "sustainability_after": after_sus,
        }

    return result
