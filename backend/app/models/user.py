from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    tenant_id = Column(String(64), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    username = Column(String(64), nullable=False)
    email = Column(String(128), nullable=False)
    hashed_password = Column(String(256), nullable=False)
    
    # RBAC + ABAC attributes
    roles = Column(JSON, default=list, nullable=False)  # e.g. ["Employee"], ["Tenant Admin"], etc.
    groups = Column(JSON, default=list, nullable=False)  # e.g. ["engineering", "finance"]
    account_status = Column(String(32), default="active", nullable=False)  # active, suspended
    clearance_level = Column(String(32), default="Internal", nullable=False)  # Public, Internal, Confidential, Restricted
    department = Column(String(64), default="General", nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
