import pytest
from fastapi.testclient import TestClient
from backend.app.models.document import Document
from backend.app.models.user import User

def test_revocation_immediately_before_llm_context_assembly(
    client: TestClient,
    acme_manager_token: str,
    db_session
):
    """
    STANDOUT TEST:
    Manager begins an authorized query for 'quarterly_financials_q3.pdf'.
    Access to this document is revoked right before LLM context assembly
    (simulating mid-flight revocation or race condition).
    The secondary security checkpoint must detect the revocation, drop the chunk,
    and prevent any revoked text or citation from reaching the LLM!
    """
    # 1. Identify the target document ID
    doc = db_session.query(Document).filter(
        Document.document_name == "quarterly_financials_q3.pdf",
        Document.tenant_id == "acme-corp"
    ).first()
    assert doc is not None

    # 2. Execute RAG query with simulated mid-flight revocation of this document
    response = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {acme_manager_token}"},
        json={
            "query": "What is the confidential dividend allocation for Q3?",
            "simulate_mid_flight_revocation_doc_id": doc.document_id
        }
    )
    assert response.status_code == 200
    data = response.json()

    # 3. Assert revoked content never reached LLM or final response
    assert data["insufficient_evidence"] is True
    assert "0.65" not in data["answer"]
    assert "special dividend" not in data["answer"].lower()
    assert len(data["citations"]) == 0
    assert data["retrieval_trace"]["authorized_chunks_count"] == 0

def test_dynamic_permission_revocation_via_api(
    client: TestClient,
    acme_admin_token: str,
    acme_manager_token: str,
    db_session
):
    """
    1. Manager queries and accesses Project Titan specs.
    2. Admin dynamically updates Project Titan permissions to remove Manager.
    3. Manager queries again: immediate denial, zero results.
    """
    query = "autonomous drone delivery navigation LIDAR"

    # Step 1: Initial query works
    res1 = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {acme_manager_token}"},
        json={"query": query}
    )
    assert res1.status_code == 200
    assert res1.json()["insufficient_evidence"] is False

    # Step 2: Admin revokes access for Manager
    doc = db_session.query(Document).filter(
        Document.document_name == "project_titan_specs.md",
        Document.tenant_id == "acme-corp"
    ).first()

    update_res = client.patch(
        f"/api/v1/documents/{doc.document_id}/permissions",
        headers={"Authorization": f"Bearer {acme_admin_token}"},
        json={
            "allowed_roles": ["Tenant Admin"],  # Removed Manager and Employee
            "allowed_groups": ["command_only"]
        }
    )
    assert update_res.status_code == 200

    # Step 3: Manager queries again -> now denied
    res2 = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {acme_manager_token}"},
        json={"query": query}
    )
    assert res2.status_code == 200
    assert res2.json()["insufficient_evidence"] is True
    assert len(res2.json()["citations"]) == 0
