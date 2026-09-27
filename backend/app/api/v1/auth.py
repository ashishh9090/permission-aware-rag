from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import Token, UserLogin, UserResponse
from backend.app.core.security import verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    # Query user strictly by username
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or inactive"
        )

    # Issue JWT containing authoritative claims
    token_claims = {
        "sub": user.id,
        "tenant_id": user.tenant_id,
        "username": user.username,
        "roles": user.roles or [],
        "groups": user.groups or [],
        "clearance_level": user.clearance_level,
        "department": user.department
    }
    access_token = create_access_token(data=token_claims)

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        tenant_id=user.tenant_id,
        username=user.username,
        roles=user.roles or [],
        groups=user.groups or [],
        clearance_level=user.clearance_level,
        department=user.department
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/personas")
def get_demo_personas(db: Session = Depends(get_db)):
    """Returns demo personas for quick switching in the interactive UI."""
    users = db.query(User).filter(User.account_status == "active").all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "tenant_id": u.tenant_id,
            "roles": u.roles,
            "groups": u.groups,
            "clearance_level": u.clearance_level,
            "department": u.department
        }
        for u in users
    ]
