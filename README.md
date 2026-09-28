# GreenForge AI 🌿

**Agentic AI for Sustainable Software & Machine Learning**

> *"Forge more efficient code. Build greener AI."*

GreenForge AI is an AI-powered developer sustainability platform that analyzes source code and ML workloads for computational inefficiencies, estimates their resource and environmental impact, generates optimized alternatives, benchmarks before/after results, and produces a transparent sustainability score.

---

## Problem Statement

Software is typically optimized for correctness, speed, and cost — but rarely for sustainability. Inefficient algorithms, nested loops, repeated I/O, non-batched ML inference, and excessive memory use increase resource consumption invisibly. GreenForge AI makes computational efficiency visible to developers during development.

## Features

| Module | Description |
|---|---|
| 🔍 Green Code Engine | Python/JS AST-based analysis detecting 20+ inefficiency patterns |
| 🧠 Green AI Lab | ML workload benchmarking, model comparison, inference efficiency |
| ⏱ Benchmark Engine | Safe subprocess execution, before/after runtime & memory comparison |
| 🌱 Sustainability Engine | Modeled energy/carbon estimates from benchmark measurements |
| 📊 GreenForge Score | Transparent 0–100 composite score with documented methodology |
| 🤖 AI Agents | 8-agent orchestration pipeline (Code Auditor → Report Generator) |
| 📚 RAG Knowledge | TF-IDF retrieval over curated green software knowledge base |
| 💬 GF Copilot | Contextual AI chat grounded in analysis results |
| 📄 Reports | PDF + JSON sustainability reports |
| ⚙ Settings | Configurable hardware assumptions |

---

## Architecture

```
frontend/          Next.js 15 + TypeScript + Tailwind CSS
backend/
  app/
    api/           FastAPI route handlers
    agents/        Orchestration pipeline (8 agents)
    analyzers/     Python AST + complexity analysis
    benchmarking/  Safe subprocess benchmark runner
    sustainability/ Energy/carbon estimation + GreenForge scoring
    providers/     IBM Granite + local fallback AI provider
    rag/           TF-IDF RAG knowledge system
    services/      Green AI Lab + report generation
    models/        SQLAlchemy ORM models
    schemas/       Pydantic request/response schemas
    core/          Config, database
data/
  demos/           5 demo projects
  knowledge_base/  Green software knowledge
docs/              Architecture, methodology, responsible AI
```

---

## Installation

### Prerequisites
- Python 3.12+ (installed in `C:\Program Files\Python312`)
- Node.js 24+ (installed in `C:\Program Files\nodejs`)

### Backend Setup
```bash
# Create virtual environment on D drive
python -m venv D:\1m1b\greenforge-ai\backend\venv

# Install dependencies
D:\1m1b\greenforge-ai\backend\venv\Scripts\pip install -r backend/requirements.txt

# Copy environment file
cp .env.example backend/.env
```

### Frontend Setup
```bash
cd frontend
npm install
```

---

## Running the Application

### Backend
```bash
cd D:\1m1b\greenforge-ai\backend
D:\1m1b\greenforge-ai\backend\venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API available at: http://localhost:8000/api  
Swagger docs: http://localhost:8000/api/docs

### Frontend
```bash
cd D:\1m1b\greenforge-ai\frontend
npm run dev
```
App available at: http://localhost:3000

---

## Environment Variables

Copy `.env.example` to `backend/.env` and configure:

| Variable | Description | Required |
|---|---|---|
| `IBM_API_KEY` | IBM watsonx.ai API key | Optional (enables Granite) |
| `IBM_PROJECT_ID` | IBM watsonx.ai Project ID | Optional (enables Granite) |
| `IBM_SERVICE_URL` | Service URL | Optional |
| `GRANITE_MODEL_ID` | Granite model ID | Optional |
| `DATABASE_URL` | SQLite path | Optional |

**The application runs fully in Demo mode without IBM credentials.**

---

## What Works Without IBM Credentials

Everything works without IBM credentials:
- ✅ Static code analysis (Python AST, JS pattern matching)
- ✅ Complexity analysis (cyclomatic, loop depth, Big-O heuristics)
- ✅ Benchmarking (subprocess, runtime, memory)
- ✅ GreenForge Score calculation
- ✅ Sustainability estimation
- ✅ RAG knowledge base queries
- ✅ Demo projects
- ✅ Report generation (PDF + JSON)
- ✅ Copilot (local deterministic fallback)
- ✅ Green AI Lab

AI responses are labeled **"Demo / Local AI mode"** when Granite is not configured.

---

## Configuring IBM Granite

1. Create an IBM Cloud account at https://cloud.ibm.com
2. Provision a watsonx.ai instance
3. Create a project and get your Project ID
4. Generate an API key
5. Add to `backend/.env`:
   ```
   IBM_API_KEY=your_api_key_here
   IBM_PROJECT_ID=your_project_id_here
   GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
   ```
6. Restart the backend

---

## Running Tests

```bash
cd D:\1m1b\greenforge-ai\backend
D:\1m1b\greenforge-ai\backend\venv\Scripts\python -m pytest tests/ -v
```

**23 tests covering:**
- Health endpoint
- Code analysis (simple, nested loops, empty, unsupported language)
- Complexity analyzer
- Sustainability estimation
- GreenForge scoring
- Benchmark runner (success, syntax error, timeout)
- Pattern detection (string concat, list membership)
- RAG retrieval and query
- API endpoints (RAG, demo, settings, copilot)
- End-to-end workflow smoke test

---

## Demo Instructions

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the full 2–3 minute live demo sequence.

**Quick demo:**
1. Start backend + frontend
2. Open http://localhost:3000
3. Click **"Run Demo"** on Dashboard → select "Nested Loop Optimization"
4. See issues detected, GreenForge Score, benchmark comparison

---

## Green Code Engine

Detects (Python, with JS/TS partial support):
1. Nested loops (O(n²/³) heuristic)
2. Repeated function calls inside loops
3. String concatenation with += in loops
4. List membership tests inside loops (O(n) per check)
5. Repeated subscript/indexing
6. Sort/sorted() inside loops
7. Unnecessary list() wrapping
8. File I/O inside loops
9. ML: model loading inside loops
10. ML: single-sample inference in loops
11. Deep copy inside loops

## Green AI Engine

- scikit-learn demo workloads (baseline, optimized, small)
- Measures: parameters, model size, accuracy, latency, memory
- Detects: large models, high latency, non-batched inference
- Compares models with accuracy/efficiency trade-off display
- Sustainability estimates per workload

---

## GreenForge Score Methodology

| Dimension | Weight | How Scored |
|---|---|---|
| Algorithmic Efficiency | 20% | Penalizes nested loops, high complexity |
| Runtime Efficiency | 20% | Based on benchmark runtime or finding severity |
| Memory Efficiency | 15% | Based on peak memory and memory findings |
| I/O Efficiency | 10% | Penalizes repeated I/O patterns |
| ML Efficiency | 10% | Penalizes ML anti-patterns |
| Optimization Potential | 15% | Inverse of finding count/severity |
| Benchmark Improvement | 10% | Before→after improvement |

Score is a **prototype indicator**, not an industry certification.

---

## Sustainability Methodology

All sustainability estimates are **modeled estimates** based on:
- Measured benchmark runtime / CPU time
- Configurable CPU TDP (default: 95W)
- Configurable CPU utilization fraction (default: 0.5)
- Configurable PUE (default: 1.5)
- Configurable grid carbon intensity (default: 475 gCO2e/kWh — world average)

Formula: `Energy (Wh) = CPU_TDP × utilization × (cpu_time / 3600) × PUE`  
Carbon: `Energy_kWh × grid_carbon_intensity`

**These values do NOT represent validated real-world measurements.**

---

## Security

- User code runs in isolated `subprocess` with configurable timeout (default: 30s)
- No `shell=True` for user-supplied code
- Temporary working directories, cleaned after each run
- Output size limited to 256KB
- File size limit: 512KB
- File type validation on upload
- UI warns users to only run trusted code

This is a **local prototype**. Production deployment would require stronger sandboxing (Docker, gVisor, Firecracker, etc.).

---

## SDG Alignment

- **SDG 12** (Primary): Responsible Consumption and Production
- **SDG 13** (Secondary): Climate Action
- **SDG 9** (Secondary): Industry, Innovation and Infrastructure

---

## Limitations

- Complexity estimates are heuristic-based (not formal verification)
- Sustainability estimates are modeled, not measured hardware telemetry
- JavaScript/TypeScript analysis is pattern-based (no full AST)
- C/C++ not currently supported
- ML analysis limited to scikit-learn demo workloads
- No NVIDIA GPU telemetry (falls back gracefully)
- Production sandboxing not implemented

## Future Work

- RAPL/NVML real energy measurement integration
- Container-based sandbox for code execution
- VS Code extension
- CI/CD integration
- More language support (Java, Go, Rust)
- Real-time monitoring mode
- Team collaboration features

---

## Installation Summary

| Component | Location |
|---|---|
| Python 3.12 | `C:\Program Files\Python312` |
| Node.js 24 | `C:\Program Files\nodejs` |
| Python venv | `D:\1m1b\greenforge-ai\backend\venv` |
| Node modules | `D:\1m1b\greenforge-ai\frontend\node_modules` |
| SQLite DB | `D:\1m1b\greenforge-ai\backend\greenforge.db` |
| PDF Reports | `D:\1m1b\greenforge-ai\reports\` |
