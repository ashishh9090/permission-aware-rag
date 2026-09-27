from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.core.security import get_current_user
from backend.app.schemas.rag import RAGQueryRequest, RAGResponse
from backend.app.services.rag_service import rag_service

router = APIRouter()

@router.post("/query", response_model=RAGResponse)
def answer_rag_query(
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    response = rag_service.answer_query(
        db=db,
        user=current_user,
        query=request.query,
        top_k=request.top_k,
        conversation_history=request.conversation_history,
        simulate_mid_flight_revocation_doc_id=request.simulate_mid_flight_revocation_doc_id
    )
    return response
