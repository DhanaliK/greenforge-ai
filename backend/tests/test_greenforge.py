"""
GreenForge AI — Backend Test Suite
Tests core functionality: analyzers, scoring, benchmarking, API endpoints.
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport


# ---- Fixtures ----
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.main import app
    from app.core.database import init_db
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---- Health ----
@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "ai_provider" in data


# ---- Code Analysis ----
@pytest.mark.asyncio
async def test_analyze_simple_code(client):
    code = """
def square(n):
    return n * n
result = square(5)
print(result)
"""
    res = await client.post("/api/analyze/code", json={"code": code, "language": "python"})
    assert res.status_code == 200
    data = res.json()
    assert "findings" in data
    assert "greenforge_score" in data
    assert "complexity" in data
    assert data["greenforge_score"]["total"] >= 0
    assert data["greenforge_score"]["total"] <= 100


@pytest.mark.asyncio
async def test_analyze_nested_loop(client):
    code = """
def slow_search(data):
    results = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == data[j] and i != j:
                results.append(data[i])
    return results
"""
    res = await client.post("/api/analyze/code", json={"code": code, "language": "python"})
    assert res.status_code == 200
    data = res.json()
    # Should detect nested loops
    severities = [f["severity"] for f in data["findings"]]
    assert any(s in ("Critical", "High") for s in severities), "Should flag nested loop"


@pytest.mark.asyncio
async def test_analyze_empty_code(client):
    res = await client.post("/api/analyze/code", json={"code": "", "language": "python"})
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_analyze_unsupported_language(client):
    res = await client.post("/api/analyze/code", json={"code": "x=1", "language": "cobol"})
    assert res.status_code == 400


# ---- Complexity Analyzer ----
def test_complexity_nested():
    from app.analyzers.complexity_analyzer import ComplexityAnalyzer
    code = """
def nested(data):
    for i in data:
        for j in data:
            pass
"""
    result = ComplexityAnalyzer().analyze(code)
    assert result["max_loop_depth"] >= 2
    assert result["total_functions"] >= 1
    assert any("O(n²)" in f["estimated_complexity"] for f in result["findings"])


def test_complexity_simple():
    from app.analyzers.complexity_analyzer import ComplexityAnalyzer
    code = "x = 1 + 2\nprint(x)"
    result = ComplexityAnalyzer().analyze(code)
    assert result["max_loop_depth"] == 0
    assert result["total_functions"] == 0


# ---- Sustainability Engine ----
def test_sustainability_estimate():
    from app.sustainability.engine import SustainabilityEngine
    engine = SustainabilityEngine()
    result = engine.estimate_from_runtime(10.0, cpu_time_seconds=9.5)
    assert result["label"] == "Modeled estimate"
    assert result["estimated_energy_wh"] > 0
    assert result["estimated_carbon_gco2e"] > 0
    assert "methodology_note" in result
    assert "modeled" in result["methodology_note"].lower()


def test_sustainability_zero_runtime():
    from app.sustainability.engine import SustainabilityEngine
    engine = SustainabilityEngine()
    result = engine.estimate_from_runtime(0.0)
    assert result["estimated_energy_wh"] == 0.0


# ---- Scoring ----
def test_score_clean_code():
    from app.sustainability.scoring import ScoringEngine
    score = ScoringEngine().calculate(findings=[])
    assert 0 <= score["total"] <= 100
    assert score["algorithmic_efficiency"] == 100.0


def test_score_with_findings():
    from app.sustainability.scoring import ScoringEngine
    findings = [
        {"severity": "Critical", "category": "Algorithmic Complexity", "title": "Nested loop"},
        {"severity": "High", "category": "Repeated Computation", "title": "Repeated call"},
    ]
    score = ScoringEngine().calculate(findings=findings)
    assert score["total"] < 90
    assert score["algorithmic_efficiency"] < 80


# ---- Benchmark Runner ----
def test_benchmark_simple():
    from app.benchmarking.runner import run_benchmark
    code = "x = sum(range(1000))\nprint(x)"
    result = run_benchmark(code, runs=2, timeout=15)
    assert result["success"] is True
    assert result["mean_runtime"] > 0
    assert result["peak_memory_mb"] >= 0


def test_benchmark_syntax_error():
    from app.benchmarking.runner import run_benchmark
    code = "def bad(:\n    pass"
    result = run_benchmark(code, runs=1, timeout=10)
    assert result["success"] is False
    assert result["error_message"]


def test_benchmark_timeout():
    from app.benchmarking.runner import run_benchmark
    code = "import time\ntime.sleep(60)"
    result = run_benchmark(code, runs=1, timeout=3)
    assert result["success"] is False


# ---- Code Analyzer Patterns ----
def test_detect_string_concat():
    from app.analyzers.code_analyzer import PythonAnalyzer
    code = """
result = ""
for item in items:
    result += str(item)
"""
    issues = PythonAnalyzer().analyze(code)
    assert any("concat" in i.issue_id.lower() or "string" in i.category.lower() for i in issues)


def test_detect_list_membership():
    from app.analyzers.code_analyzer import PythonAnalyzer
    code = """
my_list = [1,2,3,4,5]
for x in data:
    if x in my_list:
        print(x)
"""
    issues = PythonAnalyzer().analyze(code)
    assert any("membership" in i.issue_id.lower() or "data structure" in i.category.lower() for i in issues)


# ---- RAG ----
def test_rag_retrieval():
    from app.rag.rag_system import RAGSystem
    rag = RAGSystem()
    chunks = rag.retriever.retrieve("nested loops energy consumption", top_k=3)
    assert len(chunks) > 0
    assert all("chunk_text" in c for c in chunks)
    assert all(c["score"] > 0 for c in chunks)


def test_rag_query():
    from app.rag.rag_system import RAGSystem
    rag = RAGSystem()
    result = rag.query("What is Software Carbon Intensity?")
    assert "answer" in result
    assert len(result["answer"]) > 20
    assert "source_chunks" in result


# ---- API Endpoints ----
@pytest.mark.asyncio
async def test_rag_api(client):
    res = await client.post("/api/rag/query", json={"query": "green software energy efficiency", "top_k": 3})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "source_chunks" in data


@pytest.mark.asyncio
async def test_demo_list(client):
    res = await client.get("/api/demo/projects")
    assert res.status_code == 200
    data = res.json()
    assert "projects" in data
    assert len(data["projects"]) >= 5


@pytest.mark.asyncio
async def test_settings_get(client):
    res = await client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "cpu_tdp_watts" in data
    assert "grid_carbon_intensity" in data


@pytest.mark.asyncio
async def test_copilot(client):
    res = await client.post("/api/copilot/chat", json={
        "message": "What is a nested loop?",
        "history": []
    })
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 10


# ---- End-to-End Smoke Test ----
@pytest.mark.asyncio
async def test_e2e_workflow(client):
    """Upload demo code → analyze → benchmark → optimize → score → report"""
    code = """
def find_pairs(data):
    pairs = []
    for i in range(len(data)):
        for j in range(i+1, len(data)):
            if data[i] + data[j] == 10:
                pairs.append((data[i], data[j]))
    return pairs
result = find_pairs(list(range(50)))
print(f"Pairs: {len(result)}")
"""
    # 1. Analyze
    res = await client.post("/api/analyze/code", json={"code": code, "language": "python"})
    assert res.status_code == 200
    analysis = res.json()
    analysis_id = analysis["analysis_id"]
    assert analysis["greenforge_score"]["total"] >= 0

    # 2. Benchmark
    res = await client.post("/api/benchmark", json={"code": code, "label": "original", "runs": 2})
    assert res.status_code == 200
    bench = res.json()
    # success depends on environment, just check structure
    assert "mean_runtime" in bench or "error_message" in bench

    # 3. Generate Report
    res = await client.post("/api/reports/generate", json={
        "analysis_id": analysis_id,
        "title": "E2E Test Report"
    })
    assert res.status_code == 200
    report = res.json()
    assert "report_id" in report
    assert "content" in report
    assert report["content"]["greenforge_score"] is not None
