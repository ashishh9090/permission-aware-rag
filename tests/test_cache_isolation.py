import pytest
from fastapi.testclient import TestClient

def test_cache_does_not_leak_across_permission_levels(
    client: TestClient,
    acme_manager_token: str,
    acme_employee_token: str
):
    """
    1. Manager queries confidential financials. The response is cached under Manager's
       tenant + clearance + role hash.
    2. Employee executes the EXACT SAME query string.
    3. The cache must NOT be used for Employee. Employee receives insufficient evidence.
    """
    query = "What is the total quarterly revenue and profit margin?"

    # Manager queries -> populates cache
    mgr_res = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {acme_manager_token}"},
        json={"query": query}
    )
    assert mgr_res.status_code == 200
    assert "$42.8 million" in mgr_res.json()["answer"]

    # Employee queries exact same query -> MUST NOT get cached response
    emp_res = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {acme_employee_token}"},
        json={"query": query}
    )
    assert emp_res.status_code == 200
    emp_data = emp_res.json()
    assert emp_data["insufficient_evidence"] is True
    assert "$42.8 million" not in emp_data["answer"]

def test_cache_does_not_leak_across_tenants(
    client: TestClient,
    acme_manager_token: str,
    cyber_employee_token: str
):
    """
    Acme manager populates cache for a query.
    CyberDyne employee queries identical query.
    CyberDyne must NEVER get Acme cached data.
    """
    query = "What are the core employee working hours and vacation policy?"

    acme_res = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {acme_manager_token}"},
        json={"query": query}
    )
    assert acme_res.status_code == 200
    assert "Acme" in acme_res.json()["answer"]

    cyber_res = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {cyber_employee_token}"},
        json={"query": query}
    )
    assert cyber_res.status_code == 200
    # Must NOT return Acme
    assert "Acme" not in cyber_res.json()["answer"]
