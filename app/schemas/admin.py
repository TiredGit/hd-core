from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.database.models import EmployeeType, UserRole


class UserProfileCreate(BaseModel):
    address: Optional[str] = None
    apartment: Optional[str] = None
    personal_account: Optional[str] = None


class UserCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER
    profile: Optional[UserProfileCreate] = None
    employee_type: Optional[EmployeeType] = None


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None
    address: Optional[str] = None
    apartment: Optional[str] = None
    personal_account: Optional[str] = None
    employee_type: Optional[EmployeeType] = None


class UserProfileResponse(BaseModel):
    id: int
    address: Optional[str] = None
    apartment: Optional[str] = None
    personal_account: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeProfileResponse(BaseModel):
    id: int
    employee_type: EmployeeType

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile: Optional[UserProfileResponse] = None
    employee_profile: Optional[EmployeeProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)


class UserActive(BaseModel):
    id: int
    full_name: str
    phone: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)