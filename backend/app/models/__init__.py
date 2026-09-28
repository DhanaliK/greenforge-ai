from app.models.models import (
    Project, Analysis, CodeFinding, Benchmark,
    OptimizationRun, MLAnalysis, RAGDocument, RAGChunk, Report, AppSettings
)

all_models = [Project, Analysis, CodeFinding, Benchmark, OptimizationRun,
              MLAnalysis, RAGDocument, RAGChunk, Report, AppSettings]
