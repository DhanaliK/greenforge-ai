"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---- Code Analysis ----

class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Source code to analyze")
    language: str = Field(default="python", description="Programming language")
    filename: Optional[str] = None

class CodeFindingSchema(BaseModel):
    issue_id: str
    severity: str  # Critical, High, Medium, Low, Informational
    category: str
    title: str
    explanation: str
    evidence: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    estimated_complexity: Optional[str] = None
    recommendation: str
    confidence: str
    is_static: bool = True

class ComplexityFinding(BaseModel):
    function_name: str
    estimated_complexity: str
    confidence: str
    reason: str
    cyclomatic_complexity: Optional[int] = None
    line_start: Optional[int] = None

class ComplexityReport(BaseModel):
    total_functions: int
    total_classes: int
    max_loop_depth: int
    findings: List[ComplexityFinding]
    summary: str

class SustainabilityEstimate(BaseModel):
    label: str = "Modeled estimate"
    runtime_seconds: Optional[float] = None
    cpu_time_seconds: Optional[float] = None
    estimated_energy_wh: Optional[float] = None
    estimated_carbon_gco2e: Optional[float] = None
    assumptions: Dict[str, Any] = {}
    methodology_note: str = "Modeled estimate — depends on configured hardware and grid assumptions."

class GreenForgeScore(BaseModel):
    total: float
    algorithmic_efficiency: float
    runtime_efficiency: float
    memory_efficiency: float
    io_efficiency: float
    ml_efficiency: float
    optimization_potential: float
    benchmark_improvement: float
    methodology_note: str

class CodeAnalysisResponse(BaseModel):
    analysis_id: int
    language: str
    findings: List[CodeFindingSchema]
    complexity: ComplexityReport
    greenforge_score: GreenForgeScore
    sustainability_estimate: SustainabilityEstimate
    ai_provider: str
    status: str

# ---- Benchmark ----

class BenchmarkRequest(BaseModel):
    code: str
    label: str = "original"
    analysis_id: Optional[int] = None
    runs: int = Field(default=5, ge=1, le=10)

class BenchmarkResult(BaseModel):
    id: Optional[int] = None
    label: str
    success: bool
    runs: int
    mean_runtime: Optional[float] = None
    min_runtime: Optional[float] = None
    max_runtime: Optional[float] = None
    median_runtime: Optional[float] = None
    mean_memory_mb: Optional[float] = None
    peak_memory_mb: Optional[float] = None
    cpu_time: Optional[float] = None
    output_sample: Optional[str] = None
    error_message: Optional[str] = None
    raw_results: Optional[List[Dict]] = None

class BenchmarkComparisonResponse(BaseModel):
    before: BenchmarkResult
    after: BenchmarkResult
    runtime_reduction_pct: Optional[float] = None
    memory_reduction_pct: Optional[float] = None
    sustainability_before: Optional[SustainabilityEstimate] = None
    sustainability_after: Optional[SustainabilityEstimate] = None
    improvement_label: str

# ---- Optimization ----

class OptimizationRequest(BaseModel):
    code: str
    language: str = "python"
    findings: Optional[List[CodeFindingSchema]] = None
    analysis_id: Optional[int] = None
    run_benchmark: bool = True

class OptimizationResponse(BaseModel):
    optimization_id: Optional[int] = None
    original_code: str
    optimized_code: Optional[str] = None
    explanation: str
    trade_offs: str
    validation_passed: Optional[bool] = None
    validation_message: Optional[str] = None
    before_benchmark: Optional[BenchmarkResult] = None
    after_benchmark: Optional[BenchmarkResult] = None
    comparison: Optional[BenchmarkComparisonResponse] = None
    status: str
    ai_provider: str

# ---- RAG ----

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    context: Optional[Dict[str, Any]] = None

class RAGChunkResult(BaseModel):
    chunk_text: str
    document_title: str
    document_source: Optional[str] = None
    score: float
    chunk_index: int

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    source_chunks: List[RAGChunkResult]
    is_grounded: bool
    ai_provider: str

# ---- Copilot ----

class CopilotMessage(BaseModel):
    role: str  # user / assistant
    content: str

class CopilotRequest(BaseModel):
    message: str
    history: List[CopilotMessage] = []
    analysis_context: Optional[Dict[str, Any]] = None

class CopilotResponse(BaseModel):
    reply: str
    ai_provider: str
    context_used: bool

# ---- ML Analysis ----

class MLAnalysisRequest(BaseModel):
    workload_id: Optional[str] = None
    code: Optional[str] = None
    model_name: Optional[str] = None

class MLFinding(BaseModel):
    category: str
    title: str
    severity: str
    explanation: str
    recommendation: str

class MLModelMetrics(BaseModel):
    model_name: str
    num_parameters: Optional[int] = None
    model_size_mb: Optional[float] = None
    inference_latency_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    accuracy: Optional[float] = None
    batch_size: Optional[int] = None
    framework: Optional[str] = None

class MLAnalysisResponse(BaseModel):
    ml_analysis_id: Optional[int] = None
    model_name: str
    metrics: MLModelMetrics
    findings: List[MLFinding]
    recommendations: List[str]
    greenforge_score: Optional[GreenForgeScore] = None
    sustainability_estimate: Optional[SustainabilityEstimate] = None
    ai_provider: str

# ---- Report ----

class ReportRequest(BaseModel):
    analysis_id: Optional[int] = None
    ml_analysis_id: Optional[int] = None
    title: str = "GreenForge AI Sustainability Report"
    include_benchmarks: bool = True
    include_ml: bool = True

class ReportResponse(BaseModel):
    report_id: int
    title: str
    content: Dict[str, Any]
    pdf_available: bool
    created_at: str

# ---- Settings ----

class SettingsUpdate(BaseModel):
    cpu_tdp_watts: Optional[float] = None
    gpu_tdp_watts: Optional[float] = None
    grid_carbon_intensity: Optional[float] = None
    pue: Optional[float] = None
    cpu_utilization: Optional[float] = None
    benchmark_timeout: Optional[int] = None
    benchmark_runs: Optional[int] = None

class SettingsResponse(BaseModel):
    cpu_tdp_watts: float
    gpu_tdp_watts: float
    grid_carbon_intensity: float
    pue: float
    cpu_utilization: float
    benchmark_timeout: int
    benchmark_runs: int
    ai_provider_status: str
    methodology_note: str
