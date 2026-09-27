from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import UserResponse, UserCreate
from backend.app.core.security import get_current_user, get_password_hash

router = APIRouter()

class UserRoleUpdate(BaseModel):
    roles: List[str]
    clearance_level: str = None
    groups: List[str] = None

@router.get("/users", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_roles = set(current_user.roles or [])
    if "Super Admin" in user_roles:
        return db.query(User).all()
    if "Tenant Admin" in user_roles:
        return db.query(User).filter(User.tenant_id == current_user.tenant_id).all()
    raise HTTPException(status_code=403, detail="Forbidden: Admin access required")

@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    update_data: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_roles = set(current_user.roles or [])
    if "Super Admin" not in user_roles and "Tenant Admin" not in user_roles:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if "Super Admin" not in user_roles and target_user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot modify users in another tenant")

    target_user.roles = update_data.roles
    if update_data.clearance_level:
        target_user.clearance_level = update_data.clearance_level
    if update_data.groups is not None:
        target_user.groups = update_data.groups

    db.commit()
    db.refresh(target_user)
    return target_user
