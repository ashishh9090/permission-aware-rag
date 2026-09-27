from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Text
from datetime import datetime, timezone
from backend.app.db.session import Base

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    document_name = Column(String(256), nullable=False)
    document_type = Column(String(32), nullable=False)  # pdf, docx, txt, md
    
    # Classification: Public, Internal, Confidential, Restricted
    classification = Column(String(32), default="Internal", nullable=True)
    
    # Authorization metadata
    allowed_roles = Column(JSON, default=list, nullable=True)   # e.g. ["Employee", "Manager"]
    allowed_users = Column(JSON, default=list, nullable=True)   # e.g. ["usr_123"]
    allowed_groups = Column(JSON, default=list, nullable=True)  # e.g. ["finance", "executives"]
    access_policy_version = Column(Integer, default=1, nullable=False)
    
    ingestion_status = Column(String(32), default="pending", nullable=False)  # pending, indexed, failed
    content_hash = Column(String(64), nullable=True)  # SHA-256 for dedup analysis
    summary = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
