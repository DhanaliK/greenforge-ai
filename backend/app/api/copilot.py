"""GreenForge Copilot chat endpoint."""
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import CopilotRequest
from app.providers.ai_provider import get_ai_provider
from app.rag.rag_system import get_rag_system

router = APIRouter(tags=["Copilot"])
logger = logging.getLogger(__name__)


@router.post("/copilot/chat")
async def copilot_chat(request: CopilotRequest):
    """GreenForge Copilot — contextual AI chat assistant."""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    provider = get_ai_provider()
    rag = get_rag_system()

    # Retrieve relevant knowledge
    rag_chunks = rag.retriever.retrieve(request.message, top_k=3)
    rag_context = "\n".join(c["chunk_text"] for c in rag_chunks[:2]) if rag_chunks else ""

    # Build context from analysis
    analysis_ctx = request.analysis_context or {}
    findings_summary = ""
    if analysis_ctx.get("findings"):
        top = analysis_ctx["findings"][:3]
        findings_summary = "\n".join(
            f"- [{f.get('severity')}] {f.get('title')}: {f.get('explanation', '')[:100]}"
            for f in top
        )

    score = analysis_ctx.get("score", {})
    benchmark = analysis_ctx.get("benchmark", {})

    context_parts = []
    if findings_summary:
        context_parts.append(f"Current analysis findings:\n{findings_summary}")
    if score.get("total"):
        context_parts.append(f"GreenForge Score: {score['total']:.1f}/100")
    if benchmark.get("before", {}).get("mean_runtime"):
        context_parts.append(
            f"Benchmark: before={benchmark['before']['mean_runtime']:.3f}s, "
            f"after={benchmark.get('after', {}).get('mean_runtime', 'N/A')}"
        )
    if rag_context:
        context_parts.append(f"Relevant knowledge:\n{rag_context}")

    context_text = "\n\n".join(context_parts)

    # Build history
    history_text = ""
    for msg in request.history[-6:]:
        role = "User" if msg.role == "user" else "Assistant"
        history_text += f"{role}: {msg.content}\n"

    prompt = (
        f"You are GreenForge Copilot, an AI assistant specializing in software sustainability, "
        f"computational efficiency, and green AI practices.\n\n"
        f"{'Context from current analysis:' + chr(10) + context_text + chr(10) + chr(10) if context_text else ''}"
        f"{'Conversation history:' + chr(10) + history_text + chr(10) if history_text else ''}"
        f"User: {request.message}\n\n"
        f"Provide a helpful, accurate, technically precise response. "
        f"Be honest about uncertainty. Do not fabricate analysis results. "
        f"If asked about sustainability estimates, clarify they are modeled estimates."
    )

    try:
        reply = provider.generate(prompt, max_tokens=500)
    except Exception as e:
        logger.error(f"Copilot error: {e}")
        reply = (
            "I'm unable to generate a response right now. "
            "Please check that IBM Granite credentials are configured, "
            "or review the analysis findings directly."
        )

    return {
        "reply": reply,
        "ai_provider": provider.name,
        "context_used": bool(context_text),
    }
