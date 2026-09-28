"""Code analysis endpoint."""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional

from app.schemas.schemas import CodeAnalysisRequest, CodeAnalysisResponse
from app.agents.orchestrator import GreenForgeOrchestrator
from app.models.models import Analysis, CodeFinding
from app.core.database import AsyncSessionLocal
from app.core.config import settings

router = APIRouter(tags=["Analysis"])
logger = logging.getLogger(__name__)
orchestrator = GreenForgeOrchestrator()


def _validate_code(code: str):
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    if len(code) > settings.MAX_CODE_SIZE_KB * 1024:
        raise HTTPException(status_code=400, detail=f"Code exceeds {settings.MAX_CODE_SIZE_KB}KB limit")


@router.post("/analyze/code", response_model=None)
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze source code for computational inefficiencies."""
    _validate_code(request.code)

    supported = ["python", "javascript", "typescript", "js", "ts", "py"]
    if request.language.lower() not in supported:
        raise HTTPException(status_code=400, detail=f"Language '{request.language}' not supported. Supported: {supported}")

    try:
        result = orchestrator.analyze_code(request.code, request.language)
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Analysis failed. Check backend logs.")

    # Persist to DB
    analysis_id = None
    try:
        async with AsyncSessionLocal() as db:
            analysis = Analysis(
                code_snippet=request.code[:5000],
                language=request.language,
                status="complete",
                greenforge_score=result["score"]["total"],
                score_breakdown=result["score"],
            )
            db.add(analysis)
            await db.flush()
            for f in result["findings"]:
                db.add(CodeFinding(
                    analysis_id=analysis.id,
                    issue_id=f["issue_id"],
                    severity=f["severity"],
                    category=f["category"],
                    title=f["title"],
                    explanation=f["explanation"],
                    evidence=f.get("evidence", ""),
                    line_start=f.get("line_start"),
                    line_end=f.get("line_end"),
                    estimated_complexity=f.get("estimated_complexity"),
                    recommendation=f["recommendation"],
                    confidence=f["confidence"],
                    is_static=f.get("is_static", True),
                ))
            await db.commit()
            analysis_id = analysis.id
    except Exception as e:
        logger.warning(f"DB persist error (non-fatal): {e}")

    from app.providers.ai_provider import get_ai_provider
    provider = get_ai_provider()

    return {
        "analysis_id": analysis_id,
        "language": result["language"],
        "findings": result["findings"],
        "complexity": result["complexity"],
        "greenforge_score": result["score"],
        "sustainability_estimate": result["sustainability"],
        "ai_provider": provider.name,
        "status": "complete",
    }


@router.post("/analyze/upload")
async def analyze_upload(
    file: UploadFile = File(...),
    language: Optional[str] = Form(default="python")
):
    """Upload a source code file for analysis."""
    allowed_extensions = {".py", ".js", ".ts", ".txt"}
    filename = file.filename or "upload.py"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ".py"
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported")

    content = await file.read()
    if len(content) > settings.MAX_CODE_SIZE_KB * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.MAX_CODE_SIZE_KB}KB limit")

    try:
        code = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")

    # Detect language from extension
    lang_map = {".py": "python", ".js": "javascript", ".ts": "typescript"}
    detected_language = lang_map.get(ext, language or "python")

    request = CodeAnalysisRequest(code=code, language=detected_language, filename=filename)
    return await analyze_code(request)
