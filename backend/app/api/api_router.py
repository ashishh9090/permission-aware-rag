from fastapi import APIRouter
from backend.app.api.v1 import auth, documents, retrieval, rag, audit, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(retrieval.router, prefix="/retrieval", tags=["Retrieval"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
