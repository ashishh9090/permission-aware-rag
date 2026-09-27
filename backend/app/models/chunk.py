from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey
from backend.app.db.session import Base

class Chunk(Base):
    __tablename__ = "chunks"

    chunk_id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)  # list of float values (384 dims)
    
    # Classification & granular chunk-level permissions (must not exceed parent document permissions)
    classification = Column(String(32), default="Internal", nullable=True)
    allowed_roles = Column(JSON, default=list, nullable=True)
    allowed_users = Column(JSON, default=list, nullable=True)
    allowed_groups = Column(JSON, default=list, nullable=True)
    access_policy_version = Column(Integer, default=1, nullable=False)
    
    source_reference = Column(String(256), nullable=False)
    chunk_index = Column(Integer, default=0, nullable=False)
    metadata_json = Column(JSON, default=dict)
