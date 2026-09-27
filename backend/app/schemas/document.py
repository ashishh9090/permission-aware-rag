from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentCreate(BaseModel):
    document_name: str
    document_type: str
    classification: str = "Internal"
    allowed_roles: List[str] = ["Employee"]
    allowed_users: List[str] = []
    allowed_groups: List[str] = []
    content: str  # Plaintext or base64
    summary: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

class DocumentPermissionUpdate(BaseModel):
    classification: Optional[str] = None
    allowed_roles: Optional[List[str]] = None
    allowed_users: Optional[List[str]] = None
    allowed_groups: Optional[List[str]] = None

class DocumentResponse(BaseModel):
    document_id: str
    tenant_id: str
    owner_id: str
    document_name: str
    document_type: str
    classification: str
    allowed_roles: List[str]
    allowed_users: List[str]
    allowed_groups: List[str]
    access_policy_version: int
    ingestion_status: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
