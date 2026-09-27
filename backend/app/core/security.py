import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8")[:72], salt).decode("utf-8")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    token: str = Depends(oauth2_scheme),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
) -> User:
    """
    Enforces server-side authentication and authoritative identity resolution.
    Never trusts client-supplied tenant_id or roles.
    Rejects spoofing attempts where X-Tenant-ID header contradicts the token.
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims: missing subject"
        )
    
    # Query database to ensure account is active and get authoritative state
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User identity no longer exists"
        )
    
    if user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.account_status}"
        )
        
    # Check for cross-tenant header spoofing attempt
    if x_tenant_id and x_tenant_id != user.tenant_id:
        # Super Admin may view cross-tenant only if explicitly designed, but here we enforce strict tenant boundary
        if "Super Admin" not in (user.roles or []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security Violation: Tenant spoofing detected. Client-supplied tenant does not match authorized credentials."
            )

    return user

class AuthorizationEngine:
    """
    Zero-Trust Default-Deny RBAC + ABAC policy evaluator.
    Evaluates permissions across roles, groups, explicit user access,
    and ABAC security clearance levels.
    """

    @staticmethod
    def is_authorized(
        user: User,
        resource_classification: str,
        allowed_roles: List[str],
        allowed_users: List[str],
        allowed_groups: List[str],
        resource_tenant_id: str,
    ) -> bool:
        # 1. Strict Tenant Isolation (Zero cross-tenant bleed)
        # Even Super Admin cannot view documents across tenants through standard RAG retrieval
        if resource_tenant_id != user.tenant_id:
            return False

        # 2. Check if explicitly revoked / missing metadata (Default-Deny)
        if not resource_classification or not isinstance(allowed_roles, list):
            return False

        # 3. ABAC Clearance Level Check
        # User clearance must be >= resource classification
        user_clearance_score = settings.CLASSIFICATION_LEVELS.get(user.clearance_level, 1)
        resource_clearance_score = settings.CLASSIFICATION_LEVELS.get(resource_classification, 999)
        if user_clearance_score < resource_clearance_score:
            return False

        # 4. Super Admin or Tenant Admin within their tenant has blanket authorized access
        user_roles = set(user.roles or [])
        if "Super Admin" in user_roles or "Tenant Admin" in user_roles:
            return True

        # 5. Direct User Whitelist Check
        if user.id in (allowed_users or []):
            return True

        # 6. Role Intersection Check
        if any(role in user_roles for role in (allowed_roles or [])):
            return True

        # 7. Group Intersection Check
        user_groups = set(user.groups or [])
        if any(grp in user_groups for grp in (allowed_groups or [])):
            return True

        # Default Deny
        return False
