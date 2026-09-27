from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.core.security import get_current_user
from backend.app.schemas.retrieval import RetrievalQuery, RetrievalResponse
from backend.app.services.retrieval_service import retrieval_service

router = APIRouter()

@router.post("/search", response_model=RetrievalResponse)
def search_documents(
    payload: RetrievalQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results, trace = retrieval_service.retrieve(
        db=db,
        user=current_user,
        query=payload.query,
        top_k=payload.top_k,
        simulation_delay_ms=payload.simulation_delay_ms
    )
    return RetrievalResponse(
        query=payload.query,
        results=results,
        total_candidates=trace["total_candidates"],
        authorized_count=trace["authorized_count"],
        denied_count=trace["denied_count"],
        latency_ms=trace["total_latency_ms"],
        request_id=trace["request_id"],
        policy_version_applied=trace["policy_version"]
    )
