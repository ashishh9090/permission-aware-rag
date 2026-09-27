import pytest
from fastapi.testclient import TestClient

def test_guest_cannot_access_internal_or_confidential(client: TestClient, acme_guest_token: str):
    """
    Guest has clearance 'Public' and role 'Guest'.
    Guest must NOT be able to retrieve Internal or Confidential documents.
    Only Public handbook should be returned.
    """
    res = client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {acme_guest_token}"},
        json={"query": "working hours drone specifications revenue", "top_k": 5}
    )
    assert res.status_code == 200
    data = res.json()
    for result in data["results"]:
        assert result["classification"] == "Public"
        assert "handbook" in result["document_name"].lower()
        assert "quarterly_financials" not in result["document_name"].lower()
        assert "project_titan" not in result["document_name"].lower()

def test_employee_cannot_access_confidential_financials(client: TestClient, acme_employee_token: str):
    """
    Acme Employee has clearance 'Internal', role 'Employee', group 'engineering'.
    Must NOT be able to retrieve Confidential financials (requires 'Confidential' clearance and 'finance' group or Manager/Admin role).
    """
    res = client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {acme_employee_token}"},
        json={"query": "quarterly revenue dividend allocation profit margin", "top_k": 5}
    )
    assert res.status_code == 200
    data = res.json()
    # Ensure no financial report chunk was authorized
    for result in data["results"]:
        assert "quarterly_financials" not in result["document_name"].lower()
        assert "$42.8" not in result["chunk_text"]

def test_manager_can_access_confidential_financials(client: TestClient, acme_manager_token: str):
    """
    Acme Manager has clearance 'Confidential', role 'Manager', group 'finance'.
    Authorized to retrieve Confidential financials.
    """
    res = client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {acme_manager_token}"},
        json={"query": "quarterly revenue dividend allocation profit margin", "top_k": 5}
    )
    assert res.status_code == 200
    data = res.json()
    doc_names = [r["document_name"] for r in data["results"]]
    assert "quarterly_financials_q3.pdf" in doc_names

def test_rag_query_hides_inaccessible_document_existence(client: TestClient, acme_employee_token: str):
    """
    When an unauthorized user asks about confidential data, the response must NOT reveal
    whether the document exists. It must state insufficient accessible information.
    """
    res = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {acme_employee_token}"},
        json={"query": "What is the confidential dividend allocation and quarterly profit margin for Q3?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["insufficient_evidence"] is True
    assert "I do not have sufficient information in the accessible documents" in data["answer"]
    assert len(data["citations"]) == 0
