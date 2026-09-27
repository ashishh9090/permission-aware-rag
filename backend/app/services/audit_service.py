import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.audit_log import AuditLog

class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        request_id: str,
        tenant_id: str,
        user_id: str,
        action: str,
        policy_version: int,
        query_text: Optional[str],
        retrieved_chunk_ids: List[str],
        authorized_chunk_ids: List[str],
        denied_count: int,
        doc_ids_sent: List[str],
        decision: str,
        outcome: str,
        latency_ms: float,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Creates an append-only audit record.
        Strictly sanitizes details to ensure raw unauthorized text is NEVER logged.
        """
        clean_details = (details or {}).copy()
        
        # Ensure no document content keys leak into audit logs
        forbidden_keys = ["raw_text", "chunk_text", "document_content", "unauthorized_text", "content"]
        for k in forbidden_keys:
            if k in clean_details:
                del clean_details[k]

        event = AuditLog(
            event_id=f"evt_{uuid.uuid4().hex[:14]}",
            timestamp=datetime.now(timezone.utc),
            request_id=request_id,
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            authorization_policy_version=policy_version,
            query_text=query_text[:500] if query_text else None,
            retrieved_chunk_ids=retrieved_chunk_ids,
            authorized_chunk_ids=authorized_chunk_ids,
            denied_candidate_count=denied_count,
            document_ids_sent_to_llm=doc_ids_sent,
            access_decision=decision,
            outcome=outcome,
            latency_ms=round(latency_ms, 2),
            details_json=clean_details
        )
        db.add(event)
        try:
            db.commit()
            db.refresh(event)
        except Exception:
            db.rollback()
            raise
        return event

    @staticmethod
    def get_tenant_audit_logs(
        db: Session,
        tenant_id: str,
        limit: int = 50,
        offset: int = 0,
        action_filter: Optional[str] = None
    ) -> List[AuditLog]:
        query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
        if action_filter:
            query = query.filter(AuditLog.action == action_filter)
        return query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_all_audit_logs_super_admin(
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

audit_service = AuditService()
