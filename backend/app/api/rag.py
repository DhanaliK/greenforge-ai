"""RAG knowledge query endpoint."""
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import RAGQueryRequest
from app.rag.rag_system import get_rag_system

router = APIRouter(tags=["RAG"])


@router.post("/rag/query")
async def rag_query(request: RAGQueryRequest):
    """Query the GreenForge knowledge base with RAG."""
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    rag = get_rag_system()
    result = rag.query(request.query, top_k=request.top_k, context=request.context)
    return result


@router.get("/rag/documents")
async def list_documents():
    """List knowledge base documents."""
    from app.rag.rag_system import KNOWLEDGE_BASE
    return [
        {"title": d["title"], "source": d.get("source"), "category": d.get("category")}
        for d in KNOWLEDGE_BASE
    ]
