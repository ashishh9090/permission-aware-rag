from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    tenant_id: str
    username: str
    roles: List[str]
    groups: List[str]
    clearance_level: str
    department: str

class TokenPayload(BaseModel):
    sub: str  # user_id
    tenant_id: str
    username: str
    roles: List[str]
    groups: List[str]
    clearance_level: str
    exp: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str
    tenant_id: Optional[str] = None  # Optional hint, but server validates against user account

class UserResponse(BaseModel):
    id: str
    tenant_id: str
    username: str
    email: str
    roles: List[str]
    groups: List[str]
    account_status: str
    clearance_level: str
    department: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    tenant_id: str
    roles: List[str] = ["Employee"]
    groups: List[str] = []
    clearance_level: str = "Internal"
    department: str = "General"
