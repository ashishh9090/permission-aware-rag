import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.db.session import Base, get_db
import backend.app.models  # Ensures all models (Tenant, User, Document, Chunk, AuditLog) are registered in Base.metadata
from backend.app.main import app
from backend.app.seed_data import seed_database
from backend.app.core.security import create_access_token
from backend.app.models.user import User

# Use StaticPool so all connections share the exact same in-memory SQLite database
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

from backend.app.services.cache_service import cache_service

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    cache_service._cache.clear()
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    cache_service._cache.clear()

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def acme_employee_token(db_session):
    user = db_session.query(User).filter(User.username == "acme_employee").first()
    return create_access_token({
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
        "roles": user.roles,
        "groups": user.groups,
        "clearance_level": user.clearance_level,
        "department": user.department
    })

@pytest.fixture
def acme_manager_token(db_session):
    user = db_session.query(User).filter(User.username == "acme_manager").first()
    return create_access_token({
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
        "roles": user.roles,
        "groups": user.groups,
        "clearance_level": user.clearance_level,
        "department": user.department
    })

@pytest.fixture
def acme_admin_token(db_session):
    user = db_session.query(User).filter(User.username == "acme_admin").first()
    return create_access_token({
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
        "roles": user.roles,
        "groups": user.groups,
        "clearance_level": user.clearance_level,
        "department": user.department
    })

@pytest.fixture
def acme_guest_token(db_session):
    user = db_session.query(User).filter(User.username == "acme_guest").first()
    return create_access_token({
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
        "roles": user.roles,
        "groups": user.groups,
        "clearance_level": user.clearance_level,
        "department": user.department
    })

@pytest.fixture
def cyber_employee_token(db_session):
    user = db_session.query(User).filter(User.username == "cyber_employee").first()
    return create_access_token({
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
        "roles": user.roles,
        "groups": user.groups,
        "clearance_level": user.clearance_level,
        "department": user.department
    })

@pytest.fixture
def cyber_admin_token(db_session):
    user = db_session.query(User).filter(User.username == "cyber_admin").first()
    return create_access_token({
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
        "roles": user.roles,
        "groups": user.groups,
        "clearance_level": user.clearance_level,
        "department": user.department
    })
