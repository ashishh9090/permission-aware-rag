import pytest
from fastapi.testclient import TestClient

def test_identical_filenames_financials_isolation(
    client: TestClient,
    acme_manager_token: str,
    cyber_admin_token: str
):
    """
    Both tenants have an identical document name: 'quarterly_financials_q3.pdf'.
    Verify that Acme Manager gets Acme's $42.8M revenue and NEVER sees CyberDyne's $890.4M.
    Verify that CyberDyne Admin gets CyberDyne's $890.4M revenue and NEVER sees Acme's $42.8M.
    """
    # Acme Manager query
    acme_res = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {acme_manager_token}"},
        json={"query": "What is the total quarterly revenue in the financial report?"}
    )
    assert acme_res.status_code == 200
    acme_data = acme_res.json()
    assert "$42.8 million" in acme_data["answer"]
    assert "890.4" not in acme_data["answer"]
    assert len(acme_data["citations"]) > 0
    assert acme_data["citations"][0]["document_name"] == "quarterly_financials_q3.pdf"

    # CyberDyne Admin query
    cyber_res = client.post(
        "/api/v1/rag/query",
        headers={"Authorization": f"Bearer {cyber_admin_token}"},
        json={"query": "What is the total quarterly revenue in the defense financial report?"}
    )
    assert cyber_res.status_code == 200
    cyber_data = cyber_res.json()
    assert "$890.4 million" in cyber_data["answer"]
    assert "42.8" not in cyber_data["answer"]
    assert len(cyber_data["citations"]) > 0
    assert cyber_data["citations"][0]["document_name"] == "quarterly_financials_q3.pdf"

def test_identical_content_deduplication_isolation(
    client: TestClient,
    acme_admin_token: str,
    cyber_admin_token: str
):
    """
    Both tenants upload an identical text document: 'master_services_agreement.txt'.
    Verify that storage, chunking, and retrieval remain completely isolated per tenant.
    """
    identical_text = "MASTER SERVICES AGREEMENT: Section 4.2 Confidentiality and Intellectual Property assignment."

    # Acme uploads
    res1 = client.post(
        "/api/v1/documents/create-raw",
        headers={"Authorization": f"Bearer {acme_admin_token}"},
        json={
            "document_name": "master_services_agreement.txt",
            "document_type": "txt",
            "classification": "Internal",
            "allowed_roles": ["Employee", "Tenant Admin"],
            "content": identical_text
        }
    )
    assert res1.status_code == 200
    acme_doc_id = res1.json()["document_id"]

    # CyberDyne uploads identical content
    res2 = client.post(
        "/api/v1/documents/create-raw",
        headers={"Authorization": f"Bearer {cyber_admin_token}"},
        json={
            "document_name": "master_services_agreement.txt",
            "document_type": "txt",
            "classification": "Internal",
            "allowed_roles": ["Employee", "Tenant Admin"],
            "content": identical_text
        }
    )
    assert res2.status_code == 200
    cyber_doc_id = res2.json()["document_id"]

    assert acme_doc_id != cyber_doc_id

    # Acme search returns Acme document ID only
    acme_search = client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {acme_admin_token}"},
        json={"query": "Intellectual Property assignment", "top_k": 5}
    )
    assert acme_search.status_code == 200
    acme_results = acme_search.json()["results"]
    acme_doc_ids = [r["document_id"] for r in acme_results]
    assert acme_doc_id in acme_doc_ids
    assert cyber_doc_id not in acme_doc_ids
