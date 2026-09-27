from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.chunk import Chunk
from backend.app.core.security import get_current_user, AuthorizationEngine
from backend.app.schemas.document import DocumentResponse, DocumentPermissionUpdate, DocumentCreate
from backend.app.services.ingestion_service import ingestion_service

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    classification: str = Form("Internal"),
    allowed_roles: str = Form('["Employee"]'),
    allowed_groups: str = Form('[]'),
    allowed_users: str = Form('[]'),
    summary: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        roles_list = json.loads(allowed_roles) if isinstance(allowed_roles, str) else allowed_roles
        groups_list = json.loads(allowed_groups) if isinstance(allowed_groups, str) else allowed_groups
        users_list = json.loads(allowed_users) if isinstance(allowed_users, str) else allowed_users
    except Exception:
        roles_list = ["Employee"]
        groups_list = []
        users_list = []

    content_bytes = await file.read()
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "txt"

    doc = ingestion_service.ingest_document(
        db=db,
        user=current_user,
        document_name=file.filename,
        document_type=ext,
        content_bytes=content_bytes,
        classification=classification,
        allowed_roles=roles_list,
        allowed_users=users_list,
        allowed_groups=groups_list,
        summary=summary
    )
    return doc

@router.post("/create-raw", response_model=DocumentResponse)
def create_raw_document(
    doc_in: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """API endpoint to create documents directly from raw text payload."""
    content_bytes = doc_in.content.encode("utf-8")
    doc = ingestion_service.ingest_document(
        db=db,
        user=current_user,
        document_name=doc_in.document_name,
        document_type=doc_in.document_type,
        content_bytes=content_bytes,
        classification=doc_in.classification,
        allowed_roles=doc_in.allowed_roles,
        allowed_users=doc_in.allowed_users,
        allowed_groups=doc_in.allowed_groups,
        summary=doc_in.summary or ""
    )
    return doc

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns only documents belonging to the user's tenant that the user is authorized to view.
    Zero cross-tenant bleed.
    """
    tenant_docs = db.query(Document).filter(Document.tenant_id == current_user.tenant_id).all()
    authorized_docs = []
    for doc in tenant_docs:
        if AuthorizationEngine.is_authorized(
            user=current_user,
            resource_classification=doc.classification,
            allowed_roles=doc.allowed_roles,
            allowed_users=doc.allowed_users,
            allowed_groups=doc.allowed_groups,
            resource_tenant_id=doc.tenant_id
        ):
            authorized_docs.append(doc)
    return authorized_docs

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(
        Document.document_id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not AuthorizationEngine.is_authorized(
        user=current_user,
        resource_classification=doc.classification,
        allowed_roles=doc.allowed_roles,
        allowed_users=doc.allowed_users,
        allowed_groups=doc.allowed_groups,
        resource_tenant_id=doc.tenant_id
    ):
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient privileges")

    return doc

@router.patch("/{document_id}/permissions", response_model=DocumentResponse)
def update_permissions(
    document_id: str,
    update_data: DocumentPermissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = ingestion_service.update_document_permissions(
        db=db,
        document_id=document_id,
        user=current_user,
        classification=update_data.classification,
        allowed_roles=update_data.allowed_roles,
        allowed_users=update_data.allowed_users,
        allowed_groups=update_data.allowed_groups
    )
    return doc

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(
        Document.document_id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    user_roles = set(current_user.roles or [])
    if current_user.id != doc.owner_id and "Tenant Admin" not in user_roles and "Super Admin" not in user_roles:
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions to delete")

    # Cascading chunk deletion
    db.query(Chunk).filter(Chunk.document_id == document_id).delete()
    db.delete(doc)
    db.commit()
    return {"status": "deleted", "document_id": document_id}
