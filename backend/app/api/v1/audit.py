from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLog
from backend.app.core.security import get_current_user
from backend.app.schemas.audit import AuditLogResponse, AuditSummary
from backend.app.services.audit_service import audit_service

router = APIRouter()

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns audit records strictly scoped to the authenticated user's tenant.
    Super Admins can see all logs.
    """
    user_roles = set(current_user.roles or [])
    if "Super Admin" in user_roles:
        logs = audit_service.get_all_audit_logs_super_admin(db=db, limit=limit, offset=offset)
    else:
        logs = audit_service.get_tenant_audit_logs(
            db=db,
            tenant_id=current_user.tenant_id,
            limit=limit,
            offset=offset,
            action_filter=action
        )
    return logs

@router.get("/summary", response_model=AuditSummary)
def get_audit_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    user_roles = set(current_user.roles or [])
    if "Super Admin" not in user_roles:
        query = query.filter(AuditLog.tenant_id == current_user.tenant_id)

    logs = query.all()
    total = len(logs)
    permits = sum(1 for l in logs if l.access_decision == "PERMIT")
    denies = sum(1 for l in logs if l.access_decision == "DENY")
    tampers = sum(1 for l in logs if "TAMPER" in (l.outcome or ""))
    avg_lat = sum(l.latency_ms for l in logs) / total if total > 0 else 0.0

    return AuditSummary(
        total_events=total,
        permit_count=permits,
        deny_count=denies,
        tamper_attempts=tampers,
        average_latency_ms=round(avg_lat, 2)
    )
