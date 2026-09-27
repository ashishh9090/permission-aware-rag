import pytest
from fastapi.testclient import TestClient
from backend.app.models.document import Document
from backend.app.models.chunk import Chunk

def test_stale_chunk_metadata_denied(
    client: TestClient,
    acme_admin_token: str,
    db_session
):
    """
    Simulate a stale index:
    The parent document's access_policy_version is incremented to 5,
    leaving a chunk with stale version 1.
    The retrieval engine must detect this version mismatch and deny the chunk.
    """
    doc = db_session.query(Document).filter(
        Document.document_name == "company_employee_handbook.txt",
        Document.tenant_id == "acme-corp"
    ).first()
    assert doc is not None

    # Artificially desynchronize parent document version
    doc.access_policy_version = 5
    db_session.commit()

    # Search for handbook content
    res = client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {acme_admin_token}"},
        json={"query": "working hours hybrid model vacation", "top_k": 5}
    )
    assert res.status_code == 200
    data = res.json()
    # The desynchronized handbook chunks must be denied!
    for result in data["results"]:
        assert result["document_name"] != "company_employee_handbook.txt"

def test_missing_permission_metadata_default_deny(
    client: TestClient,
    acme_admin_token: str,
    db_session
):
    """
    Simulate a corrupted or incomplete chunk where classification or allowed_roles is None.
    The zero-trust engine must default-deny and return 0 results.
    """
    chunk = db_session.query(Chunk).filter(Chunk.tenant_id == "acme-corp").first()
    assert chunk is not None

    # Corrupt classification to None
    chunk.classification = None
    db_session.commit()

    res = client.post(
        "/api/v1/retrieval/search",
        headers={"Authorization": f"Bearer {acme_admin_token}"},
        json={"query": chunk.chunk_text[:50], "top_k": 5}
    )
    assert res.status_code == 200
    data = res.json()
    returned_chunk_ids = [r["chunk_id"] for r in data["results"]]
    assert chunk.chunk_id not in returned_chunk_ids
