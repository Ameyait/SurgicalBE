from uuid import UUID
from typing import Optional

from pydantic import BaseModel, EmailStr


class ProfileResponse(BaseModel):
    id: UUID
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    current_password: Optional[str] = None
    new_password: Optional[str] = None