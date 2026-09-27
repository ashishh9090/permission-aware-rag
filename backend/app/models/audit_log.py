from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from datetime import datetime, timezone
from backend.app.db.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    event_id = Column(String(64), primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    request_id = Column(String(64), index=True, nullable=False)
    tenant_id = Column(String(64), index=True, nullable=False)
    user_id = Column(String(64), index=True, nullable=False)
    action = Column(String(64), nullable=False, index=True)  # retrieval, rag_query, ingestion, permission_update, access_denied
    
    authorization_policy_version = Column(Integer, default=1, nullable=False)
    query_text = Column(String(512), nullable=True)
    
    retrieved_chunk_ids = Column(JSON, default=list, nullable=False)
    authorized_chunk_ids = Column(JSON, default=list, nullable=False)
    denied_candidate_count = Column(Integer, default=0, nullable=False)
    document_ids_sent_to_llm = Column(JSON, default=list, nullable=False)
    
    access_decision = Column(String(32), nullable=False)  # PERMIT, DENY, PARTIAL_PERMIT
    outcome = Column(String(64), nullable=False)  # SUCCESS, FORBIDDEN, ZERO_MATCH, BLOCKED_INJECTION, etc.
    latency_ms = Column(Float, default=0.0, nullable=False)
    
    # Sanitized metadata details (strictly zero unauthorized text)
    details_json = Column(JSON, default=dict)
