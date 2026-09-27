from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime, timezone
from backend.app.db.session import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    settings_json = Column(JSON, default=dict)
