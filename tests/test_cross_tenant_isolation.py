import pytest
from fastapi.testclient import TestClient

def test_cross_tenant_retrieval_returns_zero_results(client: TestClient, acme_employee_token: str):
    """
    Test 1: Acme employee attempts to search for CyberDyne-specific documents.
    Must return 0 results. Cross-tenant leakage is strictly impossible.
    """
    response = client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {acme_employee_token}"},
        json={"query": "Skynet neural net battlefield processing units cybernetic exoskeleton", "top_k": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 0
    assert data["authorized_count"] == 0

def test_cyberdyne_employee_cannot_access_acme_documents(client: TestClient, cyber_employee_token: str):
    """
    Test 2: CyberDyne employee attempts to search for Acme's Project Titan drone navigation.
    Must return only CyberDyne's Project Titan (exoskeleton), never Acme's drone navigation!
    """
    response = client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {cyber_employee_token}"},
        json={"query": "autonomous drone delivery navigation LIDAR", "top_k": 5}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Any returned chunks must strictly belong to CyberDyne
    for result in data["results"]:
        assert "cybernetic exoskeleton" in result["chunk_text"].lower() or "cheyenne mountain" in result["chunk_text"].lower()
        assert "commercial delivery drones" not in result["chunk_text"].lower()

def test_cross_tenant_header_spoofing_rejected(client: TestClient, acme_employee_token: str):
    """
    Test 3: Malicious client provides an authentic Acme token but sends an X-Tenant-ID
    header claiming to be CyberDyne.
    Must be rejected with 403 Forbidden.
    """
    response = client.post(
        "/api/v1/retrieval/search",
        headers={
            "Authorization": f"Bearer {acme_employee_token}",
            "X-Tenant-ID": "cyberdyne-sys"
        },
        json={"query": "quarterly revenue", "top_k": 5}
    )
    assert response.status_code == 403
    assert "Tenant spoofing detected" in response.json()["detail"]
