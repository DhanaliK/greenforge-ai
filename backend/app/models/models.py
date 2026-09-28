"""SQLAlchemy ORM models for GreenForge AI."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    code_snippet = Column(Text, nullable=False)
    language = Column(String(50), default="python")
    status = Column(String(50), default="pending")
    greenforge_score = Column(Float, nullable=True)
    score_breakdown = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("Project", back_populates="analyses")
    findings = relationship("CodeFinding", back_populates="analysis", cascade="all, delete-orphan")
    benchmarks = relationship("Benchmark", back_populates="analysis", cascade="all, delete-orphan")
    optimization_runs = relationship("OptimizationRun", back_populates="analysis", cascade="all, delete-orphan")


class CodeFinding(Base):
    __tablename__ = "code_findings"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    issue_id = Column(String(100))
    severity = Column(String(50))
    category = Column(String(100))
    title = Column(String(255))
    explanation = Column(Text)
    evidence = Column(Text)
    line_start = Column(Integer, nullable=True)
    line_end = Column(Integer, nullable=True)
    estimated_complexity = Column(String(100), nullable=True)
    recommendation = Column(Text)
    confidence = Column(String(50))
    is_static = Column(Boolean, default=True)
    analysis = relationship("Analysis", back_populates="findings")


class Benchmark(Base):
    __tablename__ = "benchmarks"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    label = Column(String(100), default="original")
    code_snippet = Column(Text)
    runs = Column(Integer, default=5)
    mean_runtime = Column(Float, nullable=True)
    min_runtime = Column(Float, nullable=True)
    max_runtime = Column(Float, nullable=True)
    median_runtime = Column(Float, nullable=True)
    mean_memory_mb = Column(Float, nullable=True)
    peak_memory_mb = Column(Float, nullable=True)
    cpu_time = Column(Float, nullable=True)
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    output_sample = Column(Text, nullable=True)
    raw_results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis = relationship("Analysis", back_populates="benchmarks")


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    original_code = Column(Text)
    optimized_code = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    trade_offs = Column(Text, nullable=True)
    validation_passed = Column(Boolean, nullable=True)
    validation_message = Column(Text, nullable=True)
    before_benchmark_id = Column(Integer, ForeignKey("benchmarks.id"), nullable=True)
    after_benchmark_id = Column(Integer, ForeignKey("benchmarks.id"), nullable=True)
    status = Column(String(50), default="pending")
    ai_provider = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis = relationship("Analysis", back_populates="optimization_runs")


class MLAnalysis(Base):
    __tablename__ = "ml_analyses"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255))
    framework = Column(String(100), nullable=True)
    num_parameters = Column(Integer, nullable=True)
    model_size_mb = Column(Float, nullable=True)
    inference_latency_ms = Column(Float, nullable=True)
    memory_mb = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    batch_size = Column(Integer, nullable=True)
    findings = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    greenforge_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RAGDocument(Base):
    __tablename__ = "rag_documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    source = Column(String(500), nullable=True)
    content = Column(Text)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    chunks = relationship("RAGChunk", back_populates="document", cascade="all, delete-orphan")


class RAGChunk(Base):
    __tablename__ = "rag_chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("rag_documents.id"))
    chunk_text = Column(Text)
    chunk_index = Column(Integer)
    embedding = Column(Text, nullable=True)  # JSON-encoded vector
    document = relationship("RAGDocument", back_populates="chunks")


class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)
    title = Column(String(255))
    content_json = Column(JSON)
    pdf_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AppSettings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
