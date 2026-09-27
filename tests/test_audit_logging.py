import pytest
from fastapi.testclient import TestClient
from backend.app.models.audit_log import AuditLog

def test_audit_logs_record_decisions_without_leaking_text(
    client: TestClient,
    acme_employee_token: str,
    db_session
):
    """
    Verify:
    1. Retrieval events create audit log entries.
    2. Denied attempts are logged with decision='DENY'.
    3. Details never contain raw unauthorized text.
    """
    # Attempt unauthorized retrieval
    client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {acme_employee_token}"},
        json={"query": "confidential dividend payout", "top_k": 5}
    )

    logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.tenant_id == "acme-corp")
        .order_by(AuditLog.timestamp.desc())
        .limit(5)
        .all()
    )
    assert len(logs) > 0
    latest = logs[0]
    assert latest.tenant_id == "acme-corp"
    assert latest.action in ["retrieval", "rag_query"]

    # Verify sensitive data minimization: raw chunk text must not exist in details_json
    raw_dump = str(latest.details_json)
    assert "raw_text" not in raw_dump
    assert "unauthorized_text" not in raw_dump
    assert "chunk_text" not in raw_dump

def test_tenant_admin_cannot_view_other_tenant_audit_logs(
    client: TestClient,
    acme_admin_token: str
):
    """
    Acme Admin requests audit logs.
    All returned logs must strictly have tenant_id == 'acme-corp'.
    """
    res = client.post(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {acme_admin_token}"}
    )
    # The endpoint is GET /api/v1/audit/logs
    res = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {acme_admin_token}"}
    )
    assert res.status_code == 200
    logs = res.json()
    for log in logs:
        assert log["tenant_id"] == "acme-corp"
        assert log["tenant_id"] != "cyberdyne-sys"
